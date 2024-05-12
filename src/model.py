import numpy as np
import matplotlib.pyplot as plt
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import classification_report, accuracy_score, roc_auc_score, roc_curve
import joblib
import pandas as pd

def load_data(filepath='saved_models/heart_disease_model.pkl'):
    df = pd.read_csv(filepath)
    X = df.drop('target', axis=1).values 
    y = df['target'].values
    return X, y

def preprocess_data(X):
    X_processed = (X - np.mean(X, axis=0)) / np.std(X, axis=0)
    return X_processed

def build_model():
    mlp = MLPClassifier(max_iter=100, random_state=1)
    parameter_space = {
        'hidden_layer_sizes': [(50,), (100,), (50,50), (100,100)],
        'solver': ['sgd', 'adam'],
        'alpha': [0.0001, 0.001, 0.01],
        'learning_rate_init': [0.001, 0.01]
    }
    clf = GridSearchCV(mlp, parameter_space, n_jobs=-1, cv=3)
    return clf

def train_model(clf, X_train, y_train):
    clf.fit(X_train, y_train)
    print("Best parameters found:\n", clf.best_params_)
    return clf.best_estimator_

def evaluate_model(model, X_test, y_test):
    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    print(f"Accuracy: {accuracy}")

    probs = model.predict_proba(X_test)[:, 1]
    auc_score = roc_auc_score(y_test, probs)
    print(f"AUC Score: {auc_score}")

    report = classification_report(y_test, predictions)
    print("Classification Report:\n", report)

    fpr, tpr, _ = roc_curve(y_test, probs)
    plt.figure()
    plt.plot(fpr, tpr, color='darkorange', lw=2, label='ROC curve (area = %0.2f)' % auc_score)
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver Operating Characteristic')
    plt.legend(loc="lower right")
    plt.show()

    return accuracy

def save_model(model, filename):
    joblib.dump(model, filename)

if __name__ == "__main__":
    X, y = load_data('data/heart.csv')
    X = preprocess_data(X)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
    clf = build_model()
    model = train_model(clf, X_train, y_train)
    accuracy = evaluate_model(model, X_test, y_test)
    save_model(model, 'saved_models/heart_disease_model.pkl')
