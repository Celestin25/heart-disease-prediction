import os
import json
import re
import streamlit as st
from streamlit_option_menu import option_menu

# Set the custom page title and icon
st.set_page_config(page_title="Chatbot Assistant", page_icon="🤖")

# Set page configuration at the very top
st.set_page_config(page_title="Mental Health Assistant", layout="wide", page_icon="🧠")

# User credentials storage (hardcoded for demonstration)
user_credentials = {
    "Celestin": {"password": "admin123"},
    "user": {"password": "user123"}
}

# Initialize session state for authentication
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if 'new_user' not in st.session_state:
    st.session_state['new_user'] = False

if 'current_page' not in st.session_state:
    st.session_state['current_page'] = "login"  # Default page to login

# Function for login
def login():
    st.title("Login")
    with st.form(key="login_form"):
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        submit_button = st.form_submit_button("Login")
    
    if submit_button:
        if username in user_credentials and user_credentials[username]['password'] == password:
            st.session_state['logged_in'] = True
            st.session_state['current_page'] = "main"  # Redirect to main page
            st.experimental_rerun()  # Rerun to display the main page
        else:
            st.error("Incorrect username or password!")

# Function for sign-up
def signup():
    st.title("Sign Up")
    with st.form(key="signup_form"):
        new_username = st.text_input("Create a Username", key="signup_username")
        new_password = st.text_input("Create a Password", type="password", key="signup_password")
        submit_button = st.form_submit_button("Sign Up")
    
    if submit_button:
        if new_username in user_credentials:
            st.error("Username already exists! Try another one.")
        elif new_username and new_password:
            user_credentials[new_username] = {"password": new_password}
            st.session_state['new_user'] = True
            st.success("Sign-up successful! Please log in.")
            st.session_state['current_page'] = "login"  # Redirect to login after sign-up
            st.experimental_rerun()  # Rerun to display login
        else:
            st.error("Please fill in all fields!")

# Function for logout
def logout():
    st.session_state['logged_in'] = False
    st.session_state['current_page'] = "login"
    st.experimental_rerun()  # Rerun to show the login page

# Main page after login
def main_page():
    st.title("Welcome to the Mental Health Assistant!")
    st.write("You are now logged in. Feel free to ask me anything related to mental health.")
    
    # Add logout button in the sidebar
    if st.sidebar.button("Logout"):
        logout()

# Improved chatbot response based on dataset with difflib fuzzy matching
def get_chatbot_response(user_query, language='en'):
    if language == 'en':
        intents_data = intents_data_en
    else:
        intents_data = intents_data_rw

    # Normalize user input
    user_query = user_query.lower()

    # Get all patterns
    all_patterns = [pattern.lower() for intent in intents_data['intents'] for pattern in intent['patterns']]

    # Use difflib to find the closest match
    close_matches = difflib.get_close_matches(user_query, all_patterns, n=1, cutoff=0.7)  # Adjust cutoff for matching

    if close_matches:
        matched_pattern = close_matches[0]
        # Find the intent corresponding to the matched pattern
        for intent in intents_data['intents']:
            if matched_pattern in [p.lower() for p in intent['patterns']]:
                return random.choice(intent['responses'])

    # Fallback response if no good match
    return "Ndasaba imbabazi, sinshobora kubona igisubizo kuri ibyo. Nyamuneka wiyambaze umwuga w'ubuzima ku makuru menshi."  # Kinyarwanda fallback response

# Display login/signup page if not logged in
if not st.session_state['logged_in']:
    if st.session_state['current_page'] == "login":
        login()
    elif st.session_state['current_page'] == "signup":
        signup()

    # Sidebar to switch between login and sign-up
    option = st.sidebar.radio("Choose an option", ["Login", "Sign Up"], index=0 if st.session_state['current_page'] == "login" else 1)
    
    if option == "Login":
        st.session_state['current_page'] = "login"
    elif option == "Sign Up":
        st.session_state['current_page'] = "signup"

# Display main page if logged in
if st.session_state['logged_in']:
    main_page()

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

    # Streamlit setup
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
