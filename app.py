import logging
from flask import Flask, request, render_template
import requests
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
    querystring = {"date": fixture_date, "league": "39", "season": "2023"}
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
            analysis = get_chatgpt_analysis(winner)
            goalsHome = prediction_data["response"][0]["predictions"]["goals"]["home"]
            goalsAway = prediction_data["response"][0]["predictions"]["goals"]["away"]
            advice = prediction_data["response"][0]["predictions"]["advice"]
            results.append((fixture_id, home_team, away_team, winner, goalsHome, goalsAway, advice, analysis))

    return render_template("index.html", results=results)

def get_chatgpt_analysis(prediction):
    logging.info('Sending sentiment analysis request to GPT-3.')
    openai.api_key = get_api_key('openaiapikey.txt')
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an expert in sentiment analysis and will be able to objectively analyse football match predictions and give your own input on the prediction."},
            {"role": "user", "content": prediction}
        ]
    )
    logging.info('Sentiment analysis response received.')
    return response['choices'][0]['message']['content'].strip() # Corrected line

if __name__ == '__main__':
    logging.info('App starting.')
    app.run(debug=True)