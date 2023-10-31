from flask import Flask, request, render_template
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get-fixtures', methods=['POST'])
def get_fixtures():
    fixture_date = request.form['date']
    
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    querystring = {"date": fixture_date, "league":"39", "season":"2023"}
    headers = {
        "X-RapidAPI-Key": "ef97436974msha2f90f1e83d332fp1e6007jsnc60c6c3cc314",
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)
    data = response.json()

    fixtures = [(match['fixture']['id'], match['teams']['home']['name'], match['teams']['away']['name']) for match in data['response']]
	
    return render_template('index.html', fixtures=fixtures)

if __name__ == '__main__':
    app.run(debug=True)