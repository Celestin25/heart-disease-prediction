import os
import json
import re
import streamlit as st
from streamlit_option_menu import option_menu

# Load necessary files and data
working_dir = os.path.dirname(os.path.abspath(__file__))

# Hardcoded credentials for testing
HARD_CODED_USERNAME = "testuser"
HARD_CODED_PASSWORD = "testpassword"

# Validate user login with hardcoded credentials
def validate_login(username, password):
    return username == HARD_CODED_USERNAME and password == HARD_CODED_PASSWORD

# Function to handle user login
def login():
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if validate_login(username, password):
            st.success("Logged in successfully!")
            st.session_state['authenticated'] = True
            st.experimental_rerun()  # Rerun to load the main app
        else:
            st.error("Invalid username or password.")

# Load datasets for chatbot (if authenticated)
def load_datasets():
    intents_file_path_en = os.path.join(working_dir, 'intents.json')
    intents_file_path_rw = os.path.join(working_dir, 'kiny.json')

    try:
        with open(intents_file_path_en, 'r') as file:
            intents_data_en = json.load(file)
    except FileNotFoundError:
        st.error("The 'intents.json' file was not found. Please ensure it is placed in the correct directory.")
        st.stop()
    except json.JSONDecodeError:
        st.error("Error decoding the 'intents.json' file. Please ensure it is in the correct JSON format.")
        st.stop()

    try:
        with open(intents_file_path_rw, 'r') as file:
            intents_data_rw = json.load(file)
    except FileNotFoundError:
        st.error("The 'kiny.json' file was not found. Please ensure it is placed in the correct directory.")
        st.stop()
    except json.JSONDecodeError:
        st.error("Error decoding the 'kiny.json' file. Please ensure it is in the correct JSON format.")
        st.stop()

    return intents_data_en, intents_data_rw

# Main app logic (if authenticated)
def run_app():
    intents_data_en, intents_data_rw = load_datasets()

    def get_chatbot_response(user_query, language='en'):
        if language == 'en':
            intents_data = intents_data_en
        else:
            intents_data = intents_data_rw

        for intent in intents_data['intents']:
            for pattern in intent['patterns']:
                if re.search(pattern.lower(), user_query.lower()):
                    return intent['responses'][0]  # Return the first response
        return "Sorry, I don't have an answer to that question." if language == 'en' else "Mbabarira, sinabashije kubona igisubizo cy'icyo kibazo."

    # Streamlit setup
    st.set_page_config(page_title="Mental Health Assistant", layout="wide", page_icon="🧠")

    selected = option_menu('Menu', 
                           ['Mental Health (English)', 'Ubuzima bwo mumutwe (Kinyarwanda)'], 
                           menu_icon='hospital-fill', 
                           icons=['info-circle', 'info-circle'], 
                           default_index=0)

    if selected == 'Mental Health (English)':
        st.title("Mental Health (English)")
        chat_input_box("chat_en", "en", "Type your message...")
    elif selected == 'Ubuzima bwo mumutwe (Kinyarwanda)':
        st.title("Ubuzima bwo mumutwe (Kinyarwanda)")
        chat_input_box("chat_rw", "rw", "Andika ubutumwa bwawe ...")

# Function to display chat input box
def chat_input_box(key, language, placeholder_text):
    query = st.text_input(placeholder_text, "", key=key)
    if st.button("→", key=f"{key}_arrow"):
        if query:
            response = get_chatbot_response(query, language=language)
            add_to_chat(query, response)
            st.experimental_rerun()  # Rerun to display updated chat history

# Keep track of chat history in session state
def add_to_chat(user_query, response):
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []
    st.session_state['chat_history'].append({"query": user_query, "response": response})

# Initialize session state variables
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

# Run the app
if st.session_state['authenticated']:
    run_app()
else:
    login()
