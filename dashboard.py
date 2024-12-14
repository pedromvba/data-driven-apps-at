import streamlit as st
from services.matches import *
import os
import pandas as pd
from statsbombpy import sb
from dotenv import load_dotenv
import google.generativeai as genai

st.write(summarizer(18245))