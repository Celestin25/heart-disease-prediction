import os
import pickle
import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
from sklearn.tree import _tree
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
import spacy

# Download SpaCy model
import spacy.cli
spacy.cli.download("en_core_web_sm")
nlp = spacy.load("en_core_web_sm")

# Set up the working directory
working_dir = os.path.dirname(os.path.abspath(__file__))

# Load models and data
try:
    heart_disease_model = pickle.load(open(os.path.join(working_dir, 'saved_models', 'heart_disease_model.sav'), 'rb'))
except Exception as e:
    st.error(f"Error loading heart disease model: {e}")
    st.stop()

# Load datasets
try:
    training_dataset = pd.read_csv(os.path.join(working_dir, 'Training.csv'))
    test_dataset = pd.read_csv(os.path.join(working_dir, 'Testing.csv'))
    doc_dataset = pd.read_csv(os.path.join(working_dir, 'doctors_dataset.csv'), names=['Name', 'Description'])
except Exception as e:
    st.error(f"Error loading datasets: {e}")
    st.stop()

# Preprocessing
X = training_dataset.iloc[:, 0:132].values
Y = training_dataset.iloc[:, -1].values
dimensionality_reduction = training_dataset.groupby(training_dataset['prognosis']).max()
labelencoder = LabelEncoder()
y = labelencoder.fit_transform(Y)

# Train the classifier
classifier = DecisionTreeClassifier()
classifier.fit(X, y)

# Define cols
cols = training_dataset.columns[:-1]  # Assuming all columns except the last one are features

# Helper function for hyperlink
def create_hyperlink(text, url):
    return f'<a href="{url}" target="_blank">{text}</a>'

# Load Mental Health Q&A Intents
intents_file_path = os.path.join(working_dir, 'intents.json')
try:
    with open(intents_file_path, 'r') as file:
        intents_data = json.load(file)
except FileNotFoundError:
    st.error("The 'intents.json' file was not found. Please ensure it is placed in the root directory.")
    st.stop()
except json.JSONDecodeError:
    st.error("Error decoding the 'intents.json' file. Please ensure it is in the correct JSON format.")
    st.stop()

# Function to preprocess text
def preprocess_text(text):
    doc = nlp(text.lower())
    tokens = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
    return ' '.join(tokens)

# Function to get chatbot response
from fuzzywuzzy import fuzz

def get_chatbot_response(user_query):
    highest_similarity = 0
    best_response = "I'm sorry, I don't have an answer to that question. Please consult a professional."

    for intent in intents_data['intents']:
        for pattern in intent['patterns']:
            similarity = fuzz.partial_ratio(pattern.lower(), user_query.lower())
            if similarity > highest_similarity:
                highest_similarity = similarity
                best_response = intent['responses'][0]  # Return the first response

    return best_response

# Streamlit setup
st.set_page_config(page_title="Health Assistant", layout="wide", page_icon="🧑‍⚕️")

st.write("Debug: Streamlit is running")  # Debugging statement

with st.sidebar:
    selected = option_menu('Disease Prediction System', 
                           ['Heart Disease Prediction', 'Health Chatbot', 'Mental Health Q&A'], 
                           menu_icon='hospital-fill', 
                           icons=['heart', 'chat', 'info-circle'], 
                           default_index=0)

if selected == 'Heart Disease Prediction':
    st.title('Heart Disease Prediction using ML')
    st.markdown("Please fill out the following details to predict the presence of heart disease.")
    col1, col2, col3 = st.columns(3)

    with col1:
        age = st.number_input('Age', min_value=1, max_value=120)
        trestbps = st.number_input('Resting Blood Pressure (mm Hg)', min_value=50, max_value=300)
        restecg = st.selectbox('Resting Electrocardiographic Results', options=[0, 1, 2], format_func=lambda x: {0: "Normal", 1: "ST-T Wave Abnormality", 2: "Probable or Definite Left Ventricular Hypertrophy"}[x])
        oldpeak = st.number_input('ST Depression Induced by Exercise', min_value=0.0, max_value=10.0, step=0.1)
        ca = st.number_input('Major Vessels Colored by Flouroscopy', min_value=0, max_value=4)

    with col2:
        sex = st.selectbox('Sex', options=[0, 1], format_func=lambda x: {0: "Female", 1: "Male"}[x])
        chol = st.number_input('Serum Cholestoral (mg/dl)', min_value=100, max_value=700)
        thalach = st.number_input('Maximum Heart Rate Achieved', min_value=60, max_value=250)
        slope = st.selectbox('Slope of the Peak Exercise ST Segment', options=[0, 1, 2], format_func=lambda x: {0: "Upsloping", 1: "Flat", 2: "Downsloping"}[x])

    with col3:
        cp = st.selectbox('Chest Pain Type', options=[0, 1, 2, 3], format_func=lambda x: {0: "Typical Angina", 1: "Atypical Angina", 2: "Non-Anginal Pain", 3: "Asymptomatic"}[x])
        fbs = st.radio('Fasting Blood Sugar > 120 mg/dl', options=[0, 1], format_func=lambda x: {0: "False", 1: "True"}[x])
        exang = st.radio('Exercise Induced Angina', options=[0, 1], format_func=lambda x: {0: "No", 1: "Yes"}[x])
        thal = st.selectbox('Thalassemia', options=[0, 1, 2, 3], format_func=lambda x: {0: "Normal", 1: "Fixed Defect", 2: "Reversible Defect", 3: "Other"}[x])

    if st.button('Heart Disease Test Result'):
        user_input = [age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal]
        try:
            heart_prediction = heart_disease_model.predict([user_input])
            heart_diagnosis = 'The person is having heart disease' if heart_prediction[0] == 1 else 'The person does not have any heart disease'
            st.success(heart_diagnosis)
        except Exception as e:
            st.error(f"Error in prediction: {e}")

elif selected == 'Health Chatbot':
    st.title('Health Chatbot for Disease Diagnosis')
    st.write("Hey, I am HealthChatbot that can help you to know your disease. How may I help you today?")

    if 'current_node' not in st.session_state:
        st.session_state.current_node = 0
        st.session_state.symptoms_present = []

    def print_disease(node):
        node = node[0]
        val = node.nonzero()
        disease = labelencoder.inverse_transform(val[0])
        return disease

    def recurse(node, depth):
        global tree_, feature_name
        if tree_.feature[node] != _tree.TREE_UNDEFINED:
            name = feature_name[node]
            threshold = tree_.threshold[node]
            st.write(f"Do you have {name}?")
            ans = st.radio("Your Answer:", ["yes", "no"], key=f"answer_{depth}")
            if st.button('Next', key=f'next_{depth}'):
                if ans == "yes":
                    st.session_state.symptoms_present.append(name)
                if ans == "no":
                    st.session_state.symptoms_present.append(f"not {name}")

                if tree_.children_left[node] != _tree.TREE_LEAF:
                    next_node = tree_.children_left[node] if ans == "yes" else tree_.children_right[node]
                    recurse(next_node, depth + 1)
                else:
                    st.success(f"You may have {print_disease(dimensionality_reduction.loc[:, st.session_state.symptoms_present].sum(axis=1).values.reshape(1, -1))}")

    if st.button('Start Diagnosis'):
        recurse(st.session_state.current_node, 0)

elif selected == 'Mental Health Q&A':
    st.title('Mental Health Q&A')
    st.write("Welcome to the Mental Health Q&A. Ask me anything about mental health.")

    user_input = st.text_input("You:", key="mental_health_input")
    if st.button("Send", key="send_button"):
        response = get_chatbot_response(user_input)
        st.write(f"Bot: {response}")
