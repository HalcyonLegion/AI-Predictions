import logging
from flask import Flask, request, render_template
import requests
import json
import openai

logging.basicConfig(level=logging.DEBUG)

#This lets us read the API Key.
def open_file(filepath):
    with open(filepath, 'r') as infile:
        info = infile.read()
        logging.info(f'File {filepath} read successfully.')
        return info

def get_api_key(filename):
    api_key = open_file(filename)
    logging.info('API key fetched.')
    return api_key

app = Flask(__name__)

@app.route('/')
def home():
    logging.info('Home route accessed.')
    return render_template('index.html')

@app.route("/get-fixtures", methods=["POST"])
def get_fixtures():
    logging.info('get-fixtures route accessed with POST method.')
    fixture_date = request.form.get("date")

    fixture_url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    headers = {
        "X-RapidAPI-Key": get_api_key('xrapidapikey.txt'),
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }
    querystring = {"date": fixture_date, "league": "39", "season": "2024"}
    logging.info('Sending request to fetch fixture data.')
    fixture_response = requests.get(fixture_url, headers=headers, params=querystring)
    fixture_data = fixture_response.json()
    logging.info('Fixture data obtained.')

    fixture_ids = [(match["fixture"]["id"], match["teams"]["home"]["name"], match["teams"]["away"]["name"]) for match in fixture_data["response"]]

    results = []
    for fixture in fixture_ids:
        fixture_id = fixture[0]
        home_team = fixture[1]
        away_team = fixture[2]

        prediction_url = "https://api-football-v1.p.rapidapi.com/v3/predictions"
        prediction_querystring = {"fixture": fixture_id}

        logging.info(f'Retrieving predictions for fixture_id: {fixture_id}.')
        prediction_response = requests.get(prediction_url, headers=headers, params=prediction_querystring)
        prediction_data = prediction_response.json()

        if prediction_data.get("response"):  
            winner = prediction_data["response"][0]["predictions"]["winner"]["name"]
            ai_context = prediction_data["response"][0]["predictions"]
            ai_context2 = prediction_data["response"][0]["teams"]
            analysis = get_chatgpt_analysis(ai_context, ai_context2)
            goalsHome = prediction_data["response"][0]["predictions"]["goals"]["home"]
            goalsAway = prediction_data["response"][0]["predictions"]["goals"]["away"]
            advice = prediction_data["response"][0]["predictions"]["advice"]
            results.append((fixture_id, home_team, away_team, winner, goalsHome, goalsAway, advice, analysis))

    return render_template("index.html", results=results)

def get_chatgpt_analysis(prediction, team):
    logging.info('Sending sentiment analysis request to GPT-4')
    openai.api_key = get_api_key('openaiapikey.txt')
    
    # Extract relevant data from prediction
    winner_name = prediction['winner']['name']
    win_or_draw = prediction['winner']['comment']
    home_goals = prediction['goals']['home']
    away_goals = prediction['goals']['away']
    advice = prediction['advice']
    home_record = team['home']['league']['form']
    away_record = team['away']['league']['form']
    
    # Construct user message
    user_message = f"The prediction suggests that {winner_name} will: {win_or_draw} . \
                    The goals prediction is: home team: {home_goals}, away team: {away_goals}. \
                    The given advice is: {advice}. This is the home team's league record: {home_record} vs the away team's league record: {away_record}. What is your take on this?"

    completion = openai.chat.completions.create(
        model="chatgpt-4o-latest",
        messages=[
            {"role": "system", "content": "You are an expert in statistical and sentimental analysis and will be able to objectively analyse football match predictions and give your own input on the prediction. Keep it short and to the point."},
            {"role": "user", "content": user_message}
        ]
    )
    logging.info('Sentiment analysis response received.')
    return completion.choices[0].message.content.strip()

if __name__ == '__main__':
    logging.info('App starting.')
    app.run(debug=True)