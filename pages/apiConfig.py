import streamlit as st
import os
import pandas as pd
import json

# Ensure ./temp directory exists
os.makedirs("./temp", exist_ok=True)

# Store current working directory
st.session_state.cwd = os.getcwd()

# Load session file or create a new one
session_path = "./temp/session.json"
if os.path.exists(session_path):
    with open(session_path, "r") as f:
        session = json.load(f)
else:
    session = {}

# Page config
st.set_page_config(page_title="API Configuration", page_icon="🖥️", initial_sidebar_state='collapsed')
st.sidebar.success('Currently on API Configuration page')
# Load existing API keys if available
try:
    api_df = pd.read_csv('./temp/api_keys.csv')
    gemini = api_df.loc[api_df['Service'] == 'Gemini', 'API Key'].values[0]
    openai = api_df.loc[api_df['Service'] == 'OpenAI', 'API Key'].values[0]
except FileNotFoundError:
    gemini = "Enter your Gemini API Key here"
    openai = ""

# UI
st.title("API Configuration 🖥️")
gemini = st.text_input("Gemini API Key", type="password", placeholder="Enter your Gemini API Key here", value=gemini if gemini != "Enter your Gemini API Key here" else "")
openai = st.text_input("OpenAI API Key (optional)", type="password", placeholder="Optional OpenAI API Key", value=openai)

# Store in session state
st.session_state.gemini_api_key = gemini
st.session_state.openai_api_key = openai

# Validate only Gemini key
api_valid = bool(gemini)

# Save keys if valid
if api_valid:
    st.success("Gemini API Key is set successfully!")

    # Save to CSV and JSON
    api_df = pd.DataFrame([
        {'Service': 'Gemini', 'API Key': gemini},
        {'Service': 'OpenAI', 'API Key': openai}
    ])
    api_df.to_csv('./temp/api_keys.csv', index=False)

    api_dic = {
        'gemini_api_key': gemini,
        'openai_api_key': openai
    }

    with open("./temp/API.json", "w") as file:
        json.dump(api_dic, file, indent=4)

    with open(session_path, "w") as file:
        json.dump(session, file, indent=4)
else:
    st.warning("Please enter your Gemini API key to proceed.")

# Navigation buttons
st.markdown('#')
if st.button("Home", type="secondary"):
    st.switch_page("streamlit_app.py")
