import os
import pickle
import numpy as np
import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
from sklearn.tree import _tree
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
from transformers import BertTokenizer, BertForSequenceClassification
import torch
import subprocess  # Added import for subprocess
import sys
try:
    from transformers import BertTokenizer, BertForSequenceClassification
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "transformers"])
    from transformers import BertTokenizer, BertForSequenceClassification
# Load necessary models and data
working_dir = os.path.dirname(os.path.abspath(__file__))
heart_disease_model = pickle.load(open(f'{working_dir}/saved_models/heart_disease_model.sav', 'rb'))

# Load datasets
training_dataset = pd.read_csv(f'{working_dir}/Training.csv')
test_dataset = pd.read_csv(f'{working_dir}/Testing.csv')
doc_dataset = pd.read_csv(f'{working_dir}/doctors_dataset.csv', names=['Name', 'Description'])

# Preprocessing
X = training_dataset.iloc[:, 0:132].values
Y = training_dataset.iloc[:, -1].values
dimensionality_reduction = training_dataset.groupby(training_dataset['prognosis']).max()
labelencoder = LabelEncoder()
y = labelencoder.fit_transform(Y)

# Train the classifier
classifier = DecisionTreeClassifier()
classifier.fit(X, y)

# Define `cols`
cols = training_dataset.columns[:-1]  # Assuming all columns except the last one are features

# Helper function for hyperlink
def create_hyperlink(text, url):
    return f'<a href="{url}" target="_blank">{text}</a>'

# Mental Health Q&A Data
mental_health_data = {
    "What is depression?": "Depression is a mood disorder that causes persistent feelings of sadness and loss of interest.",
    "What are the symptoms of anxiety?": "Symptoms of anxiety include feeling nervous, restless, or tense, having an increased heart rate, and sweating.",
    "How can I manage stress?": "Managing stress can be done through regular physical activity, relaxation techniques like deep breathing, and maintaining a healthy lifestyle.",
    # Add more Q&A as needed
}

# Load BERT model for mental health Q&A
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=2)

# Function for BERT model prediction
def get_bert_response(question):
    inputs = tokenizer(question, return_tensors="pt")
    outputs = model(**inputs)
    probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
    return "Yes" if probs[0][1] > probs[0][0] else "No"

# Streamlit setup
st.set_page_config(page_title="Health Assistant", layout="wide", page_icon="🧑‍⚕️")

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
                    next_node = tree_.children_right[node]
                else:
                    next_node = tree_.children_left[node]
                st.session_state.current_node = next_node
        else:
            present_disease = print_disease(tree_.value[node])
            st.write("You may have: " + str(present_disease))
            red_cols = dimensionality_reduction.columns
            symptoms_given = red_cols[dimensionality_reduction.loc[present_disease].values[0].nonzero()]
            st.write("Symptoms present: " + str(list(st.session_state.symptoms_present)))
            st.write("Symptoms given: " + str(list(symptoms_given)))
            confidence_level = (1.0 * len(st.session_state.symptoms_present)) / len(symptoms_given)
            st.write("Confidence level is: " + str(confidence_level))

            # Check if there is a doctor available for the predicted disease
            if not doc_dataset[doc_dataset['Name'] == present_disease[0]].empty:
                row = doc_dataset[doc_dataset['Name'] == present_disease[0]]
                st.write(f'Consult {str(row["Name"].values[0])}')
                link = str(row['Description'].values[0])
                st.write(f'Visit {create_hyperlink("this link", link)}')
            else:
                st.write("No specific doctor available in the dataset for this disease.")

    def tree_to_code(tree, feature_names):
        global tree_, feature_name
        tree_ = tree.tree_
        feature_name = [feature_names[i] if i != _tree.TREE_UNDEFINED else "undefined!" for i in tree_.feature]
        return recurse(st.session_state.current_node, 1)

    if st.button('Start Chatbot'):
        st.session_state.current_node = 0
        st.session_state.symptoms_present = []
        st.session_state.started = True

    if 'started' in st.session_state:
        tree_to_code(classifier, cols)

elif selected == 'Mental Health Q&A':
    st.title('Mental Health Chatbot')
    st.write("Ask me anything about mental health!")

    query = st.text_input("Your Question:")

    if query:
        response = get_bert_response(query)
        st.write(response)
