import streamlit as st
from transformers import pipeline

# Initialize BERT model for question answering
qa_pipeline = pipeline("question-answering", model="bert-base-uncased", tokenizer="bert-base-uncased")

# Streamlit setup
st.set_page_config(page_title="Health Assistant", layout="wide", page_icon="🧑‍⚕️")

# Sidebar menu options
with st.sidebar:
    selected = st.selectbox('Navigation', 
                           ['Heart Disease Prediction', 'Health Chatbot', 'Mental Health Q&A'], 
                           index=2)

# Main content based on selected option
if selected == 'Heart Disease Prediction':
    st.title('Heart Disease Prediction using ML')
    st.write("This section is under construction.")

elif selected == 'Health Chatbot':
    st.title('Health Chatbot for Disease Diagnosis')
    st.write("This section is under construction.")

elif selected == 'Mental Health Q&A':
    st.title('Mental Health Chatbot')
    st.write("Ask me anything about mental health!")

    # Text input for user question
    query = st.text_input("Your Question:")

    if query:
        # Use BERT for question answering
        response = qa_pipeline({
            "question": query,
            "context": ""
        })

        # Display BERT's answer
        st.write(response['answer'])

