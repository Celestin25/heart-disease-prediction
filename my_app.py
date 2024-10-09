import os
import json
import re
import streamlit as st
from streamlit_option_menu import option_menu

# Load necessary files and data
working_dir = os.path.dirname(os.path.abspath(__file__))

# Load English Mental Health Q&A dataset (intents.json)
intents_file_path_en = os.path.join(working_dir, 'intents.json')
try:
    with open(intents_file_path_en, 'r') as file:
        intents_data_en = json.load(file)
except FileNotFoundError:
    st.error("The 'intents.json' file was not found. Please ensure it is placed in the correct directory.")
    st.stop()
except json.JSONDecodeError:
    st.error("Error decoding the 'intents.json' file. Please ensure it is in the correct JSON format.")
    st.stop()

# Load Kinyarwanda Mental Health Q&A dataset (kiny.json)
intents_file_path_rw = os.path.join(working_dir, 'kiny.json')
try:
    with open(intents_file_path_rw, 'r') as file:
        intents_data_rw = json.load(file)
except FileNotFoundError:
    st.error("The 'kiny.json' file was not found. Please ensure it is placed in the correct directory.")
    st.stop()
except json.JSONDecodeError:
    st.error("Error decoding the 'kiny.json' file. Please ensure it is in the correct JSON format.")
    st.stop()

# Helper function to get chatbot response based on language
def get_chatbot_response(user_query, language='en'):
    if language == 'en':
        intents_data = intents_data_en
    else:
        intents_data = intents_data_rw

    for intent in intents_data['intents']:
        for pattern in intent['patterns']:
            if re.search(pattern.lower(), user_query.lower()):
                return intent['responses'][0]  # Return the first response
    return "Sorry, I don't have an answer to that question. Please consult a professional." if language == 'en' else "Mbabarira, sinabashije kubona igisubizo cy'icyo kibazo. Mwihangane mubaze muganga."

# Streamlit setup
st.set_page_config(page_title="Mental Health Assistant", layout="wide", page_icon="🧠")

with st.sidebar:
    selected = option_menu('Mental Health Assistant', 
                           ['Mental Health (English)', 'Ubuzima bwo mumutwe (Kinyarwanda)'], 
                           menu_icon='hospital-fill', 
                           icons=['info-circle', 'info-circle'], 
                           default_index=0)

# English Mental Health Q&A Session
if selected == 'Mental Health (English)':
    st.title("Mental Health (English)")
    st.write("Ask me anything about mental health, and I will try to assist you with answers.")

    user_query_en = st.text_input("Your Question:")
    if user_query_en:
        response_en = get_chatbot_response(user_query_en, language='en')
        st.write(response_en)

# Kinyarwanda Ubuzima bwo mumutwe Session
elif selected == 'Ubuzima bwo mumutwe (Kinyarwanda)':
    st.title("Ubuzima bwo mumutwe -(Kinyarwanda)")
    st.write("Mumbaze ibibazo byose bijyanye n'ubuzima bwo mumutwe, kandi ngerageze kubisubiza.")

    user_query_rw = st.text_input("Ikibazo cyawe:")
    if user_query_rw:
        response_rw = get_chatbot_response(user_query_rw, language='rw')
        st.write(response_rw)
