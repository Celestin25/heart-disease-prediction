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
                           ['Mental Health Q&A (English)', 'Ubuzima bwo mumutwe (Kinyarwanda)'], 
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

def chat_input_box(key, language, placeholder_text):
    # CSS for the input box, textarea, and button inside the textarea
    st.markdown("""
    <style>
    .input-container {
        position: relative;
        width: 100%;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    .input-textarea {
        width: 100%;
        padding: 10px;
        font-size: 16px;
        border: 1px solid #CCC;
        border-radius: 10px;
        resize: none;
        min-height: 50px;
        max-height: 200px;
        overflow-y: auto;
        line-height: 1.5em;
        box-sizing: border-box;
    }
    .input-textarea:focus {
        outline: none;
        border-color: #4CAF50;
    }
    .input-arrow {
        position: absolute;
        right: 15px;
        bottom: 10px;
        background-color: #4CAF50;
        border: none;
        color: white;
        padding: 5px;
        border-radius: 50%;
        cursor: pointer;
        font-size: 16px;
        height: 40px;
        width: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .input-arrow:hover {
        background-color: #45a049;
    }
    </style>
    """, unsafe_allow_html=True)

    # HTML for the textarea with an embedded arrow button inside the textarea
    query = st.text_area(placeholder_text, "", key=key, height=50)

    # Check if key exists in session state and initialize if not
    if key not in st.session_state:
        st.session_state[key] = ""

    # Use a regular button positioned separately as an arrow
    arrow_clicked = st.button("→", key=f"{key}_arrow", help="Send Message")
    
    # Check for arrow click or if the Enter key is pressed (simulate form submission)
    if arrow_clicked or (query and st.session_state.get(f"{key}_enter", False)):
        if query.strip():  # Ensure the input is not empty
            response = get_chatbot_response(query, language=language)
            add_to_chat(query, response)
            st.session_state[key] = ""  # Clear input after submission
            st.experimental_rerun()  # Rerun to display updated chat history




# Example of how to use the function for English and Kinyarwanda sessions
if selected == 'Mental Health Q&A (English)':
    st.title("Mental Health Q&A (English)")
    st.write("Ask me anything about mental health, and I will try to assist you with answers.")
    
    # Display chat input box for English
    chat_input_box("chat_en", "en", "Type your message...")

elif selected == 'Ubuzima bwo mumutwe (Kinyarwanda)':
    st.title("Ubuzima bwo mumutwe - Ibibazo n'Ibisubizo (Kinyarwanda)")
    st.write("Mumbaze ibibazo byose bijyanye n'ubuzima bwo mumutwe, kandi ngerageze kubisubiza.")
    
    # Display chat input box for Kinyarwanda
    chat_input_box("chat_rw", "rw", "Andika ubutumwa bwawe ...")


