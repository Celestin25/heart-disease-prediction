import os
import json
import re
import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu

# Load necessary files and data
working_dir = os.path.dirname(os.path.abspath(__file__))

# Load Kinyarwanda mental health intents dataset
intents_file_path = os.path.join(working_dir, 'kiny.json')
try:
    with open(intents_file_path, 'r') as file:
        intents_data = json.load(file)
except FileNotFoundError:
    st.error("The 'kiny.json' file was not found. Please ensure it is placed in the correct directory.")
    st.stop()
except json.JSONDecodeError:
    st.error("Error decoding the 'kiny.json' file. Please ensure it is in the correct JSON format.")
    st.stop()

# Helper function for chatbot response
def get_chatbot_response(user_query):
    for intent in intents_data['intents']:
        for pattern in intent['patterns']:
            if re.search(pattern.lower(), user_query.lower()):
                return intent['responses'][0]  # Return the first response
    return "Mbabarira, sinabashije kubona igisubizo cy'icyo kibazo. Mwihangane mubaze muganga."

# Streamlit setup
st.set_page_config(page_title="Ubuzima bwo mumutwe", layout="wide", page_icon="🧠")

with st.sidebar:
    selected = option_menu('Ubuzima bwo mumutwe', 
                           ['Mental Health Q&A'], 
                           menu_icon='hospital-fill', 
                           icons=['info-circle'], 
                           default_index=0)

# Mental Health Q&A Section
if selected == 'Mental Health Q&A':
    st.title("Ubuzima bwo mumutwe - Ibibazo n'Ibisubizo")
    st.write("Mumbaze ibibazo byose bijyanye n'ubuzima bwo mumutwe, kandi ngerageze kugufasha kubisubiza.")

    user_query = st.text_input("Ikibazo cyawe:")
    if user_query:
        response = get_chatbot_response(user_query)
        st.write(response)
