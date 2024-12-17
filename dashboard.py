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

    matches = get_matches(competition_id, season_id)
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


