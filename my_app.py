import os
import pickle
import numpy as np
import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
from sklearn.tree import _tree
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier

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
    "What is bipolar disorder?": "Bipolar disorder is a mental health condition that causes extreme mood swings that include emotional highs (mania or hypomania) and lows (depression).",
    "What are the symptoms of bipolar disorder?": "Symptoms of bipolar disorder can include mood swings, changes in sleep patterns, energy levels, behavior, and the ability to think clearly.",
    "What is schizophrenia?": "Schizophrenia is a serious mental disorder in which people interpret reality abnormally, which may result in hallucinations, delusions, and extremely disordered thinking and behavior.",
    "What are the symptoms of schizophrenia?": "Symptoms of schizophrenia can include delusions, hallucinations, disorganized thinking, and extremely disorganized or abnormal motor behavior.",
    "How can I improve my sleep?": "Improving sleep can be achieved by maintaining a regular sleep schedule, creating a restful environment, limiting exposure to screens before bedtime, and avoiding large meals, caffeine, and alcohol before sleep.",
    "What is OCD?": "Obsessive-Compulsive Disorder (OCD) is a mental disorder characterized by uncontrollable, recurring thoughts (obsessions) and behaviors (compulsions) that one feels the urge to repeat over and over.",
    "What are the symptoms of OCD?": "Symptoms of OCD include excessive cleaning, arranging things in a particular way, repeatedly checking things, and having intrusive thoughts.",
    "What is PTSD?": "Post-Traumatic Stress Disorder (PTSD) is a mental health condition triggered by experiencing or witnessing a terrifying event, causing flashbacks, nightmares, and severe anxiety.",
    "What are the symptoms of PTSD?": "Symptoms of PTSD include flashbacks, nightmares, severe anxiety, uncontrollable thoughts about the event, and emotional numbness.",
    "How can I help someone with a mental health issue?": "You can help by being supportive, listening without judgment, encouraging them to seek professional help, and educating yourself about their condition.",
    "What is social anxiety disorder?": "Social anxiety disorder is a mental health condition characterized by intense fear of social situations, causing significant distress and impaired ability to function in parts of daily life.",
    "What are the symptoms of social anxiety disorder?": "Symptoms include intense fear of interacting with others, avoiding social situations, and physical symptoms like sweating, trembling, and a rapid heart rate.",
    "How can I improve my mental health?": "Improving mental health can involve regular physical activity, healthy eating, maintaining social connections, practicing mindfulness, and seeking professional help when needed.",
    "What is cognitive behavioral therapy (CBT)?": "Cognitive Behavioral Therapy (CBT) is a type of psychotherapy that helps individuals change negative thought patterns and behaviors to improve mental health.",
    "What is mindfulness?": "Mindfulness is a mental practice that involves focusing on the present moment while calmly acknowledging and accepting one's feelings, thoughts, and bodily sensations.",
    "How can exercise benefit mental health?": "Exercise can benefit mental health by reducing anxiety, depression, and negative mood, and by improving self-esteem and cognitive function.",
    "What is an eating disorder?": "An eating disorder is a mental health condition characterized by abnormal or disturbed eating habits, which can include anorexia nervosa, bulimia nervosa, and binge-eating disorder.",
    "What are the symptoms of an eating disorder?": "Symptoms can include severe food restriction, overeating, purging behaviors, and an unhealthy preoccupation with food, body weight, and shape.",
    "How can I support a friend with depression?": "Support a friend with depression by listening to them, encouraging them to seek professional help, and offering to help with everyday tasks. Show patience and understanding.",
    "What is self-care?": "Self-care involves taking steps to preserve or improve one's own health, well-being, and happiness, especially during periods of stress.",
    "How does nutrition affect mental health?": "Nutrition affects mental health by providing essential nutrients that regulate mood and energy levels. A balanced diet can improve overall brain function and emotional well-being.",
    "What is ADHD?": "Attention-Deficit/Hyperactivity Disorder (ADHD) is a mental health disorder characterized by patterns of inattention, hyperactivity, and impulsivity that interfere with functioning or development.",
    "What are the symptoms of ADHD?": "Symptoms of ADHD include difficulty sustaining attention, hyperactivity, and impulsive behavior.",
    "How can I build resilience?": "Building resilience can involve developing a positive mindset, setting realistic goals, maintaining strong relationships, and practicing stress-management techniques.",
    "What is autism spectrum disorder (ASD)?": "Autism spectrum disorder (ASD) is a developmental disorder characterized by difficulties in social interaction, communication, and by restricted or repetitive patterns of thought and behavior.",
    "What are the symptoms of autism?": "Symptoms of autism include challenges with communication, difficulty with social interactions, and repetitive behaviors or interests.",
    "What is grief?": "Grief is the emotional response to a loss, particularly to the loss of a loved one. It involves feelings of deep sorrow, sadness, and mourning.",
    "How can I cope with grief?": "Coping with grief can involve talking about your feelings with supportive people, seeking professional counseling, participating in support groups, and taking care of your physical health.",
    "What is seasonal affective disorder (SAD)?": "Seasonal affective disorder (SAD) is a type of depression that's related to changes in seasons, usually starting in the fall and continuing into the winter months.",
    "What are the symptoms of SAD?": "Symptoms of SAD include feeling depressed most of the day, losing interest in activities, experiencing low energy, having problems with sleep, and changes in appetite or weight.",
    "How can I improve my mood naturally?": "Improving mood naturally can involve regular exercise, getting enough sleep, spending time in nature, practicing mindfulness, and maintaining social connections.",
    "What is the difference between sadness and depression?": "Sadness is a normal human emotion that everyone experiences, usually in response to an event or situation. Depression is a persistent and severe mood disorder that requires professional treatment.",
    "What is a panic attack?": "A panic attack is a sudden episode of intense fear that triggers severe physical reactions when there is no real danger or apparent cause.",
    "What are the symptoms of a panic attack?": "Symptoms of a panic attack can include a rapid heart rate, sweating, trembling, shortness of breath, chest pain, nausea, dizziness, and feelings of unreality or detachment.",
    "How can I prevent panic attacks?": "Preventing panic attacks can involve regular physical activity, practicing relaxation techniques, avoiding caffeine and alcohol, and seeking professional help if needed.",
    "What is resilience?": "Resilience is the ability to adapt well in the face of adversity, trauma, tragedy, threats, or significant sources of stress.",
}

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
        response = mental_health_data.get(query, "I'm sorry, I don't have an answer to that question. Please consult a professional.")
        st.write(response)
