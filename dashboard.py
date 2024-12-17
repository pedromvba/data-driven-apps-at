import streamlit as st
from services.matches import *
from services.playerStats import *
import os
import pandas as pd
from statsbombpy import sb
from dotenv import load_dotenv
import google.generativeai as genai
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain.schema import AIMessage, HumanMessage
from services.agent import load_agent
import matplotlib.pyplot as plt
import numpy as np


def radar_chart(player_data, player_name, ax):

    metrics = player_data['metrica'].unique()
    values = [player_data[player_data['metrica'] == metric]['valor'].values[0] for metric in metrics]
    
    
    num_vars = len(metrics)

    angles = [n / float(num_vars) * 2 * 3.1416 for n in range(num_vars)]
    values += values[:1]  # Fechando o círculo no gráfico
    angles += angles[:1]  # Fechando o círculo no gráfico

    ax.set_theta_offset(3.1416 / 2)
    ax.set_theta_direction(-1)

    ax.plot(angles, values, linewidth=1, linestyle='solid', label=player_name)
    ax.fill(angles, values, alpha=0.3)
    
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(metrics)

    ax.set_title(f'{player_name} - Radar', size=16, color='black', y=1.1)
    ax.legend(loc='upper right', bbox_to_anchor=(1.1, 1.1))


st.write('#### Compare 2 jogadores')

selected_players = st.multiselect(
        'Selecione até 2 jogadores para comparar',
        get_events(match_id)['player'].dropna().unique(),
        max_selections=2
    )



if 'match_id' not in st.session_state:
    st.session_state.match_id = None
if 'competition_id' not in st.session_state:
    st.session_state.competition_id = None
if 'season_id' not in st.session_state:
    st.session_state.season_id = None

msgs = StreamlitChatMessageHistory()
if "memory" not in st.session_state:
    st.session_state["memory"] = ConversationBufferMemory(messages=msgs, memory_key="chat_history", return_messages=True)
memory = st.session_state.memory

def memorize_message():
    user_input = st.session_state["user_input"]
    st.session_state["memory"].chat_memory.add_message(HumanMessage(content=user_input))



tab1, tab2, tab3, tab4 = st.tabs(['Partidas', 'Narração', 'Ficha Técnica do Jogador', 'ChatBot'])


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

    st.write(f"**Competição Selecionada:** {competition_name}")
    st.write(f"**Temporada Selecionada:** {season_selected}")

    matches = get_matches(competition_id, season_id)
    match_id = st.selectbox('Id do Jogo', matches['match_id'])
    
    st.session_state.match_id = match_id

    st.write('#### Principais Eventos da Partida')
    st.write(summarizer(match_id))


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

    st.title('Ficha Técnica do Jogador')

    st.write('#### Selecione um jogador para ver os detalhes da partida')
    if player_name := st.selectbox('Jogadores', 
                            get_events(match_id)['player'].dropna().unique()):
        
        melted_df = player_events(match_id, player_name).melt().rename(columns={'variable': 'metrica', 'value': 'valor'})
        st.dataframe(melted_df, hide_index=True, width=1000)

    st.write(f'#### Estatísticas do Jogador {player_name}')

    col1, col2, col3 = st.columns(3)


    gols = melted_df[melted_df['metrica'] == 'goals']['valor'].values[0]
    col1.metric('Gols', gols)

    pct_chutes_no_alvo = (melted_df[melted_df['metrica'] == 'shots_on_target']['valor'].values[0] + gols) / \
                                 melted_df[melted_df['metrica'] == 'shots']['valor'].values[0]
    col2.metric('Pct. Chutes no Alvo', f"{pct_chutes_no_alvo:.2%}")


    pct_passes_completados = melted_df[melted_df['metrica'] == 'passes_completed']['valor'].values[0] / \
                            melted_df[melted_df['metrica'] == 'passes_attempted']['valor'].values[0]
    col3.metric('Pct. Passes Completados', f"{pct_passes_completados:.2%}")

        
    if len(selected_players) == 2:
            p1, p2 = st.columns(2)
            
            fig1, ax1 = plt.subplots(figsize=(6, 6), dpi=150, subplot_kw=dict(polar=True))
            player_data1 = player_events(match_id, selected_players[0]).melt().rename(columns={'variable': 'metrica', 'value': 'valor'})
            p1.dataframe(player_data1, hide_index=True, width=400)
            radar_chart(player_data1, selected_players[0], ax1)
            p1.pyplot(fig1)
            
            fig2, ax2 = plt.subplots(figsize=(6, 6), dpi=150, subplot_kw=dict(polar=True))
            player_data2 = player_events(match_id, selected_players[1]).melt().rename(columns={'variable': 'metrica', 'value': 'valor'})
            p2.dataframe(player_data2, hide_index=True, width=400)
            radar_chart(player_data2, selected_players[1], ax2)
            p2.pyplot(fig2)

    else:
        st.write("Por favor, selecione dois jogadores para comparar.")
    
    
with tab4:

    st.title('ChatBot')

    with st.container(border=False):
        st.chat_input(key="user_input", on_submit=memorize_message) 
        if user_input := st.session_state.user_input:
            chat_history = st.session_state["memory"].chat_memory.messages
            for msg in chat_history:
                if isinstance(msg, HumanMessage):
                    with st.chat_message("user"):
                        st.write(f"{msg.content}")
                elif isinstance(msg, AIMessage):
                    with st.chat_message("assistant"):
                        st.write(f"{msg.content}")
                        
            with st.spinner("Agent is responding..."):
                try:
                    # Load agent
                    agent = load_agent()
                    
                    # Cache tools to avoid redundant calls
                    tools = [           
                    retrieve_match_details,
                    get_specialist_comments
                    ]
                    tool_names = [tool.name for tool in tools]
                    tool_descriptions = [tool.description for tool in tools]

                    # Prepare input for the agent
                    input_data = {
                        "match_id": st.session_state.match_id,
                        "input": user_input,
                        "agent_scratchpad": "",
                        "competition_id": int(st.session_state.competition_id),
                        "season_id": int(st.session_state.season_id),
                        "tool_names": tool_names,
                        "tools": tool_descriptions,
                    }

                    # Invoke agent
                    response = agent.invoke(input=input_data, handle_parsing_errors=True)

                    # Validate response
                    if isinstance(response, dict) and "output" in response:
                        output = response.get("output")
                    else:
                        output = "Sorry, I couldn't understand your request. Please try again."

                    # Add response to chat memory
                    st.session_state["memory"].chat_memory.add_message(AIMessage(content=output))

                    # Display response in chat
                    with st.chat_message("assistant"):
                        st.write(output)

                except Exception as e:
                    # Handle and display errors gracefully
                    st.error(f"Error during agent execution: {str(e)}")
                    st.write("Ensure that your inputs and agent configuration are correct.")


