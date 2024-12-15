import os
import pandas as pd
from statsbombpy import sb
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

def get_events(match_id):
    match_events = sb.events(match_id=match_id)
    return match_events

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
    
    """

    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(prompt)
    return response.text