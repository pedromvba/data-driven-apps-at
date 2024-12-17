import os
import pandas as pd
from statsbombpy import sb
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

############# StatsBomb Data Functions #############
def get_competitions():
    return sb.competitions()

def get_match_details(competition_id, season_id):
    return sb.matches(competition_id=competition_id, season_id=season_id)

def get_events(match_id):
    match_events = sb.events(match_id=match_id)
    return match_events

def starting_lineups(match_id):
    lineup = sb.lineups(match_id=match_id)
    starting_xi_data = []

    for team in lineup:
        team_data = lineup[team]

        for index, player in team_data.iterrows():
            for position in player['positions']:
                if position.get('start_reason') == 'Starting XI':
                    starting_xi_data.append({
                        'team': team,
                        'player_id': player['player_id'],
                        'player_name': player['player_name'],
                        'player_nickname': player['player_nickname'],
                        'jersey_number': player['jersey_number'],
                        'country': player['country'],
                        'cards': player['cards'],
                        'position_id': position['position_id'],
                        'position': position['position'],
                        'from': position['from'],
                        'to': position['to']
                    })

    df_starting_xi = pd.DataFrame(starting_xi_data)
    return df_starting_xi


def match_goals(match_id):
    events = get_events(match_id)
    goals = events[events['shot_outcome'] == 'Goal'][['player', 'team', 'minute', 'shot_outcome', 'shot_technique', 'team']]
    goals = goals.dropna(axis=1, how='all')
    return goals

def match_assitencies(match_id):
    events = get_events(match_id)
    assistencies = events[events['pass_goal_assist']==True]
    assistencies = assistencies.dropna(axis=1, how='all')
    return assistencies

def shots_on_target(match_id):
    events = get_events(match_id)
    on_target_shots = events[events['shot_outcome'] == 'Saved'][['minute','period','team', 'player']]
    on_target_shots = on_target_shots.dropna(axis=1, how='all')
    return on_target_shots

def cards(match_id):
    events = get_events(match_id)
    if 'foul_committed_card' not in events.columns:
        return pd.DataFrame()
    game_cards = events[events['foul_committed_card'].notnull()]
    game_cards = game_cards.dropna(axis=1, how='all')
    return game_cards

def substitutions(match_id):
    events = get_events(match_id)
    substitions = events[events['substitution_replacement'].notnull()]
    substitions = substitions.dropna(axis=1, how='all')
    return substitions

def convert_to_text_list(df):
    text_df = df.apply(lambda row: ', '.join([f"{col}: {row[col]}" for col in df.columns]),
              axis=1).tolist()
    return text_df

############# LLM Functions #############

def summarizer(match_id):
    goals = convert_to_text_list(match_goals(match_id))
    assistencies = convert_to_text_list(match_assitencies(match_id))
    on_target_shots = convert_to_text_list(shots_on_target(match_id))
    game_cards = convert_to_text_list(cards(match_id))
    substitions = convert_to_text_list(substitutions(match_id))


    prompt = f""""

    ## Context
    You are a sports journalist covering a soccer match. 
    You have been tasked with writing a summary of the match.

    ## Instructions

    Provide, in portuguese of Brazil, a clear and concise summary of the match, including the goals,
    assistencies, shots on target, game cards, and substitutions.

    To do that, you can use the following information:

    goals: {goals}
    assistencies: {assistencies}
    on_target_shots: {on_target_shots}
    game_cards: {game_cards}
    substitions: {substitions}

    If you dont have any information about a specific event, you can skip it.

    
    """

    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text

def commentator(competition_id, season_id, match_id, type):

    goals = convert_to_text_list(match_goals(match_id))
    assistencies = convert_to_text_list(match_assitencies(match_id))
    on_target_shots = convert_to_text_list(shots_on_target(match_id))
    game_cards = convert_to_text_list(cards(match_id))
    substitions = convert_to_text_list(substitutions(match_id))
    match_details = convert_to_text_list(get_match_details(competition_id, season_id))
    lineups = convert_to_text_list(starting_lineups(match_id))


    prompt = f""""

    ## Context
    You are a {type} soccer commentador covering a soccer match.
    You have been tasked with commenting the game.

    ## Instructions

    Provide, in portuguese of Brazil, a narrative of the match including the <match details>,  
    the <lineups>, <goals>, <assistencies>, <on_target_shots>, <game cards>, and <substitutions>.

    To do that, you use the following information:

    match details: {match_details}
    lineups: {lineups} 
    goals: {goals}
    assistencies: {assistencies}
    on_target_shots: {on_target_shots}
    game_cards: {game_cards}
    substitions: {substitions}
    

    Provide the expert commentary on the match as you are in a sports broadcast.
    Start your analysis now and engage the audience with your insights.
    
    """

    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text