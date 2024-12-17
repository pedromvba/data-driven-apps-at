import streamlit as st
from services.matches import *
from services.playerStats import *
import os
import pandas as pd
from statsbombpy import sb
from dotenv import load_dotenv
import google.generativeai as genai


st.title('Análise de Partidas de Futebol')

st.write('#### Selecione a competição e a temporada para ver os detalhes da partida')

competitions = get_competitions()

competition_name = st.selectbox('Competição',competitions['competition_name'].unique())
competition_id = competitions[competitions['competition_name'] == competition_name]['competition_id'].unique()[0]

filtered_seasons = competitions[competitions['competition_name'] == competition_name]['season_name'].unique()
season_selected = st.selectbox('Temporada', filtered_seasons)
season_id = competitions[
                (competitions['competition_name'] == competition_name) & 
                (competitions['season_name'] == season_selected)
                ]['season_id'].iloc[0]

st.write(f"**Competição Selecionada:** {competition_name}")
st.write(f"**Temporada Selecionada:** {season_selected}")

match = get_match_details(competition_id, season_id)
match_id = match['match_id'][0]

st.write('#### Principais Eventos da Partida')
st.write(summarizer(match_id))

st.write('#### Ficha Técnica do Jogador')

if player_name := st.selectbox('Jogadores', 
                           get_events(match_id)['player'].dropna().unique()):
    
    melted_df = player_events(match_id, player_name).melt().rename(columns={'variable': 'metrica', 'value': 'valor'})
    st.dataframe(melted_df, hide_index=True, width=1000)
