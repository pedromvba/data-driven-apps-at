import pandas as pd
from statsbombpy import sb
from services.matches import get_events

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