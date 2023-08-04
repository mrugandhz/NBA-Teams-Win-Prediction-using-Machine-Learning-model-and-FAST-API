import json
import requests

# url = 'http://127.0.0.1:8000/predict_nba_home_team_win/'
# response = requests.get(url)
# print(response.headers)
#
#
# try:
#     data = json.loads(response.text)
# except json.decoder.JSONDecodeError as e:
#     print(f"Error decoding JSON response: {str(e)}")
#     data = {}

import dash
from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc
from nba_api.stats.endpoints import leaguegamefinder

gamefinder = leaguegamefinder.LeagueGameFinder(
    date_from_nullable='05/01/2021', league_id_nullable='00')
games = gamefinder.get_data_frames()[0]

team_names = games['TEAM_NAME'].unique()
team_names.sort()
team_name_dropdown_options = [{'label': i, 'value': i} for i in team_names]

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Welcome to the NBA games winner prediction"),
    html.H2("Home Team"),
    dcc.Dropdown(
        id='home_team',
        options=team_name_dropdown_options,
        value=team_names[0]
    ),
    html.H2("Away Team"),
    dcc.Dropdown(
        id='away_team',
        options=team_name_dropdown_options,
        value=team_names[1]
    ),
    html.H3(id='output_text')
])


@app.callback(
    Output('output_text', 'children'),
    Input('home_team', 'value'),
    Input('away_team', 'value'),
)
def update_output_div(home_team, away_team):
    response = requests.get('http://127.0.0.1:8000/predict_nba_home_team_win/',
                            headers={'Accept': 'application/json'},
                            params={'team_home': home_team, 'team_away': away_team})

    if 'application/json' not in response.headers['Content-Type']:
        print(f"Unexpected content type received from server: {response.headers['Content-Type']}")
        # handle the error as necessary
    else:
        try:
            json_response = response.json()
            winning_team = home_team if json_response['result'] == 1 else away_team
            probability_of_winning = json_response.get('win_probability', 0.0) if winning_team == home_team \
                else 1.0 - json_response.get('win_probability', 0.0)
            return f'{winning_team} will win with a probability of {probability_of_winning}'
        except json.decoder.JSONDecodeError:
            return "Error: Could not decode JSON response"



if __name__ == '__main__':
    app.run_server(debug=True)
