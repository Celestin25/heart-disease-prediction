import os
import json
import re
import streamlit as st
from streamlit_option_menu import option_menu

# User credentials storage (hardcoded for demonstration)
user_credentials = {
    "admin": {"password": "admin123"},
    "user": {"password": "user123"}
}

# Initialize session state for authentication
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if 'new_user' not in st.session_state:
    st.session_state['new_user'] = False

def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if username in user_credentials and user_credentials[username]['password'] == password:
            st.session_state['logged_in'] = True
            st.success(f"Welcome, {username}!")
            st.experimental_rerun()
        else:
            st.error("Incorrect username or password!")

def signup():
    st.title("Sign Up")
    new_username = st.text_input("Create a Username")
    new_password = st.text_input("Create a Password", type="password")
    
    if st.button("Sign Up"):
        if new_username in user_credentials:
            st.error("Username already exists! Try another one.")
        else:
            user_credentials[new_username] = {"password": new_password}
            st.session_state['new_user'] = True
            st.success("Sign-up successful! Please log in.")
            st.experimental_rerun()

# Show login/signup options if not logged in
if not st.session_state['logged_in']:
    option = st.sidebar.selectbox("Choose an option", ["Login", "Sign Up"])

    if option == "Login":
        login()
    elif option == "Sign Up":
        signup()

# Proceed to main page if logged in
if st.session_state['logged_in']:
    # Load necessary files and data
    working_dir = os.path.dirname(os.path.abspath(__file__))

    # Load English Mental Health dataset (intents.json)
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

    # Initialize session state to keep track of chat history
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []

    # Define function to add question and response to the chat history
    def add_to_chat(user_query, response):
        st.session_state['chat_history'].append({"query": user_query, "response": response})

    # Display chat history
    if st.session_state['chat_history']:
        for chat in st.session_state['chat_history']:
            st.write(f"**You:** {chat['query']}")
            st.write(f"**Bot:** {chat['response']}")

    # Function to display chat input box with an embedded arrow
    def chat_input_box(key, language, placeholder_text):
        query = st.text_input(placeholder_text, "", key=key)
        if st.button("→", key=f"{key}_arrow"):
            if query:
                response = get_chatbot_response(query, language=language)
                add_to_chat(query, response)
                st.experimental_rerun()  # Rerun to display updated chat history

    # English Mental Health Q&A Session
    if selected == 'Mental Health (English)':
        st.title("Mental Health (English)")
        st.write("Ask me anything about mental health, and I will try to assist you with answers.")
        chat_input_box("chat_en", "en", "Type your message...")

    # Kinyarwanda Ubuzima bwo mumutwe Session
    elif selected == 'Ubuzima bwo mumutwe (Kinyarwanda)':
        st.title("Ubuzima bwo mumutwe (Kinyarwanda)")
        st.write("Mumbaze ibibazo byose bijyanye n'ubuzima bwo mumutwe, kandi ngerageze kubisubiza.")
        chat_input_box("chat_rw", "rw", "Andika ubutumwa bwawe ...")
