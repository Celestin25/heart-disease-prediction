import os
import pickle
import webbrowser
import numpy as np
import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
from sklearn.tree import _tree
from sklearn.preprocessing import LabelEncoder

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
from sklearn.tree import DecisionTreeClassifier
classifier = DecisionTreeClassifier()
classifier.fit(X, y)

# Helper function for hyperlink
def create_hyperlink(text, url):
    return f'<a href="{url}" target="_blank">{text}</a>'

# Streamlit setup
st.set_page_config(page_title="Health Assistant", layout="wide", page_icon="🧑‍⚕️")

with st.sidebar:
    selected = option_menu('Disease Prediction System', ['Heart Disease Prediction', 'Health Chatbot'], menu_icon='hospital-fill', icons=['heart', 'chat'], default_index=0)

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
        slope = st.selectbox('Slope of the Peak Exercise ST Segment', options=[0, 1, 2], format_func=lambda x: {0: "Upsloping", 1: "Flat", 2: "Downsloping"})

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

    def print_disease(node):
        node = node[0]
        val = node.nonzero()
        disease = labelencoder.inverse_transform(val[0])
        return disease

    def recurse(node, depth):
        global val, ans, tree_, feature_name, symptoms_present
        if tree_.feature[node] != _tree.TREE_UNDEFINED:
            name = feature_name[node]
            threshold = tree_.threshold[node]
            yield name + " ?"
            ans = ans.lower()
            if ans == 'yes':
                val = 1
            else:
                val = 0
            if val <= threshold:
                yield from recurse(tree_.children_left[node], depth + 1)
            else:
                symptoms_present.append(name)
                yield from recurse(tree_.children_right[node], depth + 1)
        else:
            present_disease = print_disease(tree_.value[node])
            yield "You may have: " + str(present_disease)
            red_cols = dimensionality_reduction.columns
            symptoms_given = red_cols[dimensionality_reduction.loc[present_disease].values[0].nonzero()]
            yield "Symptoms present: " + str(list(symptoms_present))
            yield "Symptoms given: " + str(list(symptoms_given))
            confidence_level = (1.0 * len(symptoms_present)) / len(symptoms_given)
            yield "Confidence level is: " + str(confidence_level)
            row = doctors[doctors['disease'] == present_disease[0]]
            yield f'Consult {str(row["name"].values)}'
            link = str(row['link'].values[0])
            yield f'Visit {create_hyperlink("this link", link)}'

    def tree_to_code(tree, feature_names):
        global tree_, feature_name, symptoms_present
        tree_ = tree.tree_
        feature_name = [feature_names[i] if i != _tree.TREE_UNDEFINED else "undefined!" for i in tree_.feature]
        symptoms_present = []
        return recurse(0, 1)

    def execute_bot():
        return tree_to_code(classifier, cols)

    if st.button('Start Chatbot'):
        st.session_state['iter'] = execute_bot()

    if 'iter' in st.session_state:
        try:
            query = next(st.session_state['iter'])
            ans = st.radio(query, ['yes', 'no'])
            if st.button('Next'):
                st.session_state['iter'] = execute_bot()
        except StopIteration:
            st.success("Diagnosis completed.")
