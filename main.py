from fastapi import FastAPI
from fastapi.responses import JSONResponse
from nba_api.stats.endpoints import leaguegamefinder
import pandas as pd
import numpy as np
from joblib import load

app = FastAPI()

model_saved = load('model_nba.joblib')

def predict_games(team_home=None, team_away=None):
    try:
        gamefinder = leaguegamefinder.LeagueGameFinder(date_from_nullable='01/01/2021', league_id_nullable='00')
        games = gamefinder.get_data_frames()[0]
        games = games[['TEAM_NAME', 'GAME_ID', 'GAME_DATE', 'MATCHUP', 'WL', 'PLUS_MINUS']]

        games['GAME_DATE'] = pd.to_datetime(games['GAME_DATE'])

        msk_home=(games['TEAM_NAME']==team_home)
        games_30_home=games[msk_home].sort_values('GAME_DATE').tail(30)
        home_plus_minus=games_30_home['PLUS_MINUS'].mean()

        msk_away=(games['TEAM_NAME']==team_away)
        games_30_away=games[msk_away].sort_values('GAME_DATE').tail(30)
        away_plus_minus=games_30_away['PLUS_MINUS'].mean()

        games_diff = home_plus_minus - away_plus_minus
        games_diff=np.array([games_diff])

        predict_home_win=model_saved.predict(games_diff.reshape(1, -1))[0]

        predict_winning_probability=model_saved.predict_proba(games_diff.reshape(1, -1))[0][1]

        return {'result':int(predict_home_win),
                'win_probability':float(predict_winning_probability)}
    except ValueError as ve:
        return {'error': 'ValueError: ' + str(ve)}
    except Exception as e:
        return {'error': 'An error occurred during prediction: ' + str(e)}
    
@app.get("/predict_nba_home_team_win/", response_class=JSONResponse)
def predict_games_results(team_home: str = None, team_away: str = None):
    if not team_home or not team_away:
        return {'error': 'Please provide values for team_home and team_away.'}
    return predict_games(team_home, team_away)


