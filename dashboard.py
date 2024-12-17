import streamlit as st
from services.matches import *
from services.playerStats import *
import os
import pandas as pd
from statsbombpy import sb
from dotenv import load_dotenv
import google.generativeai as genai


if 'match_id' not in st.session_state:
    st.session_state.match_id = None
if 'competition_id' not in st.session_state:
    st.session_state.competition_id = None
if 'season_id' not in st.session_state:
    st.session_state.season_id = None

tab1, tab2, tab3 = st.tabs(['Partidas', 'Narração', 'ChatBot'])


with tab1:

    st.title('Análise de Partidas de Futebol')

    st.write('#### Selecione a competição e a temporada para ver os detalhes da partida')

    competitions = get_competitions()

    competition_name = st.selectbox('Competição',competitions['competition_name'].unique())
    competition_id = competitions[competitions['competition_name'] == competition_name]['competition_id'].unique()[0]
    st.session_state.competition_id = competition_id

    filtered_seasons = competitions[competitions['competition_name'] == competition_name]['season_name'].unique()
    season_selected = st.selectbox('Temporada', filtered_seasons)
    season_id = competitions[
                    (competitions['competition_name'] == competition_name) & 
                    (competitions['season_name'] == season_selected)
                    ]['season_id'].iloc[0]
    st.session_state.season_id = season_id

    st.write(competition_id, season_id)

    st.write(f"**Competição Selecionada:** {competition_name}")
    st.write(f"**Temporada Selecionada:** {season_selected}")

    matches = get_match_details(competition_id, season_id)
    match_id = st.selectbox('Id do Jogo', matches['match_id'])
    
    st.session_state.match_id = match_id

    st.write('#### Principais Eventos da Partida')
    st.write(summarizer(match_id))

    st.write('#### Ficha Técnica do Jogador')

    if player_name := st.selectbox('Jogadores', 
                            get_events(match_id)['player'].dropna().unique()):
        
        melted_df = player_events(match_id, player_name).melt().rename(columns={'variable': 'metrica', 'value': 'valor'})
        st.dataframe(melted_df, hide_index=True, width=1000)

with tab2:


    st.title('Análise de Partidas de Futebol')
    
    st.write(f'#### Id da Partida: {st.session_state.match_id}')

    if type := st.selectbox('Escolha o Tipo da Narração', ['Formal', 'Técnica', 'Humorística'], key='narration_type'):
        if st.session_state.match_id:
            st.write(commentator(
                competition_id=st.session_state.competition_id, 
                season_id=st.session_state.season_id, 
                match_id=st.session_state.match_id, 
                type=type
                ))
with tab3:

    st.title('ChatBot')
