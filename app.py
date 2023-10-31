from flask import Flask, request, render_template
import requests
import openai

#This lets us read the API Key.
def open_file(filepath):
    with open(filepath, 'r') as infile:
        return infile.read()

def get_api_key(filename):
    api_key = open_file(filename)
    return api_key

openai.api_key = get_api_key('openaiapikey.txt')

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route("/get-fixtures", methods=["POST"])
def get_fixtures():
    fixture_date = request.form.get("date")

    fixture_url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    headers = {
        "X-RapidAPI-Key": get_api_key('xrapidapikey.txt'),
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }
    querystring = {"date": fixture_date, "league": "39", "season": "2023"}
    fixture_response = requests.get(fixture_url, headers=headers, params=querystring)
    fixture_data = fixture_response.json()

    fixture_ids = [(match["fixture"]["id"], match["teams"]["home"]["name"], match["teams"]["away"]["name"]) for match in fixture_data["response"]]

    results = []
    gpt_outputs = []
    for fixture in fixture_ids:
        fixture_id = fixture[0]
        home_team = fixture[1]
        away_team = fixture[2]

    prediction_url = "https://api-football-v1.p.rapidapi.com/v3/predictions"
    prediction_querystring = {"fixture": fixture_id}
	
    prediction_response = requests.get(prediction_url, headers=headers, params=prediction_querystring)
    prediction_data = prediction_response.json()

    if prediction_data.get("response"):  
        winner = prediction_data["response"][0]["predictions"]["winner"]["name"]
        advice = prediction_data["response"][0]["predictions"]["advice"]
        results.append((fixture_id, home_team, away_team, winner, advice))

    message = f"""
        The upcoming fixture between {home_team} and {away_team} 
        (A fixture ID: {fixture_id}) has the following predictions:
        The likely winner would be {winner} with a possibility of a draw.
        Additional advice provided is: {advice}.
        """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an insightful assistant who is able to analyse and make accurate predictions on Football scores based on the data provided. Please try your best to provide a full-time score."},
            {"role": "user", "content": message}
        ]
    )

    gpt_outputs.append(response['choices'][0]['message']['content'])

    return render_template("index.html", results_and_outputs=zip(results, gpt_outputs))

if __name__ == '__main__':
    app.run(debug=True)