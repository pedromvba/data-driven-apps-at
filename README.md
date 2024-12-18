# Projeto de Dashboard e API para Análise de Partidas

## Descrição do projeto e objetivo

Este projeto consiste em um dashboard interativo e uma API para análise de partidas de futebol utilizando dados da biblioteca StatsBomb. O objetivo é fornecer uma ferramenta visual que permita apresentar os principais eventos dos jogos, bem como comparar o desempenho de jogadores em diferentes partidas e um ofertar um chatbot que possa responder perguntas sobre a partida em análise.

## Instruções para configurar o ambiente e executar o código

1. **Clone o repositório:**
    ```sh
    git clone <https://github.com/pedromvba/data-driven-apps-at.git>
    ```

2. **Crie e ative um ambiente virtual:**
    ```sh
    python -m venv venv
    source venv/bin/activate  # No Windows use `venv\Scripts\activate`
    ```

3. **Instale as dependências:**
    ```sh
    pip install -r requirements.txt
    ```

4. **Configure as variáveis de ambiente:**
    Crie um arquivo [.env](http://_vscodecontentref_/1) na raiz do projeto e adicione sua chave do Gemini no formato: GEMINI_API_KEY = Xxxxxxxxxxxxx

5. **Execute a API:**
    ```sh
    uvicorn main_api:app --reload
    ```

6. **Execute o dashboard:**
    ```sh
    streamlit run dashboard.py
    ```

## Exemplos de entrada e saída das funcionalidades

### Dashboard

- **Análise da Partida:**
    - Selecione a partida de futebol que deseja análise.
    - Saída: Principais eventos da partida com sumarização dos mesmos.

- **Narração da Partida:**
    - A partir da partida selecionada gera a narração da partida com diferentes tipos de narração.
    - Saída: A narração da partida com o estilo escolhido.

- **Comparação de Jogadores:**
    - Selecione dois jogadores para comparar suas métricas de desempenho em uma partida específica.
    - Saída: Gráficos radar comparando as métricas dos jogadores selecionados.

- **ChatBot:**
    - Pergunte ao ChatBot alguma informação sobre o jogo
    - Saída: Resposta da Pergunta

### API

- **Endpoint `/match-summary`:**
    - **Entrada:** `GET /match-summary?match_id=<ID_DA_PARTIDA>`
    - **Exemplo** `GET /match_summary/?match_id=18245`
    - **Saída:** Resumo dos principais eventos da partida

- **Endpoint `/player-profile`:**
    - **Entrada:** `GET /player-profile?match_id=<ID_DA_PARTIDA>&player_name=<NOME_JOGADOR>`
    - **Exemplo** `GET /player_profile/?match_id=18245&player_name=Daniel+Carvajal+Ramos`
    - **Saída:** Perfil detalhado do jogador.
