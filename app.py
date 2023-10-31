from flask import Flask, request, render_template
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route("/get-fixtures", methods=["POST"])
def get_fixtures():
    fixture_date = request.form.get("date")

    fixture_url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    headers = {
        "X-RapidAPI-Key": "ef97436974msha2f90f1e83d332fp1e6007jsnc60c6c3cc314",
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }
    querystring = {"date": fixture_date, "league": "39", "season": "2023"}
    fixture_response = requests.get(fixture_url, headers=headers, params=querystring)
    fixture_data = fixture_response.json()

    fixture_ids = [(match["fixture"]["id"], match["teams"]["home"]["name"], match["teams"]["away"]["name"]) for match in fixture_data["response"]]

    results = []
    for fixture in fixture_ids:
        fixture_id = fixture[0]
        home_team = fixture[1]
        away_team = fixture[2]

        prediction_url = "https://api-football-v1.p.rapidapi.com/v3/predictions"
        prediction_querystring = {"fixture": fixture_id}
	
        prediction_response = requests.get(prediction_url, headers=headers, params=prediction_querystring)
        prediction_data = prediction_response.json()

        if prediction_data.get("response"):  # Check to make sure there is a result
            winner = prediction_data["response"][0]["predictions"]["winner"]["name"]
            results.append((fixture_id, home_team, away_team, winner))

    return render_template("index.html", results=results)

if __name__ == '__main__':
    app.run(debug=True)