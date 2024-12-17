import pandas as pd
from statsbombpy import sb
from services.matches import get_events
from langchain.tools import tool
import json


def convert_to_text_list(df):
    text_df = df.apply(lambda row: ', '.join([f"{col}: {row[col]}" for col in df.columns]),
              axis=1).tolist()
    return text_df

def player_events(match_id, player_name):

    match_events = get_events(match_id)
    player_events = match_events[match_events['player'] == player_name]
    player_events = player_events.dropna(axis=1, how='all')

    stats = {
        "passes_completed": player_events[(player_events['type'] == 'Pass') & (player_events.get('pass_outcome', pd.Series()).isna())].shape[0] 
        if 'type' in player_events.columns and 'pass_outcome' in player_events.columns else 0,
        
        "passes_attempted": player_events[player_events['type'] == 'Pass'].shape[0]
        if 'type' in player_events.columns else 0,
        
        "shots": player_events[player_events['type'] == 'Shot'].shape[0]
        if 'type' in player_events.columns else 0,
        
        "shots_on_target": player_events[(player_events['type'] == 'Shot') & (player_events.get('shot_outcome', pd.Series()) == 'On Target')].shape[0]
        if 'type' in player_events.columns and 'shot_outcome' in player_events.columns else 0,
        
        "fouls_committed": player_events[player_events['type'] == 'Foul Committed'].shape[0]
        if 'type' in player_events.columns else 0,
        
        "fouls_won": player_events[player_events['type'] == 'Foul Won'].shape[0]
        if 'type' in player_events.columns else 0,
        
        "tackles": player_events[player_events['type'] == 'Tackle'].shape[0]
        if 'type' in player_events.columns else 0,
        
        "interceptions": player_events[player_events['type'] == 'Interception'].shape[0]
        if 'type' in player_events.columns else 0,
        
        "dribbles_successful": player_events[(player_events['type'] == 'Dribble') & (player_events.get('dribble_outcome', pd.Series()) == 'Complete')].shape[0]
        if 'type' in player_events.columns and 'dribble_outcome' in player_events.columns else 0,
        
        "dribbles_attempted": player_events[player_events['type'] == 'Dribble'].shape[0]
        if 'type' in player_events.columns else 0,
        
        "goals": player_events[player_events['shot_outcome'] == 'Goal'].shape[0]
        if 'shot_outcome' in player_events.columns else 0
    }

    stats['player'] = player_name
    return pd.DataFrame([stats])

@tool
def player_stats(action_input: str) -> str:
    """
    Provide an overview of the player statistics which is useful for the player's 
    performance analysis or comparison.

    It has the following statistics:
    - Passes Completed
    - Passes Attempted
    - Shots
    - Shots on Target
    - Fouls Committed
    - Fouls Won
    - Tackles
    - Interceptions
    - Dribbles Successful
    - Dribbles Attempted
    - Goals

    Args:
    - action_input(str): The input data containing the match_id and player_name
        format: {
            "match_id": 123,
            "player_name": "Cristiano Ronaldo"
        }

    Returns:
    - A summary of the player's statistics in text format.
    """
    try:
        input_data = json.loads(action_input)
        match_id = input_data["match_id"]
        player_name = input_data["player_name"]

        stats_df = player_events(match_id, player_name)
        return '\n'.join(convert_to_text_list(stats_df))
    except KeyError as e:
        return f"Missing key in input data: {e}"
    except Exception as e:
        return f"An error occurred: {str(e)}"
