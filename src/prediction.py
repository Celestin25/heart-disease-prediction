import numpy as np
import joblib

def load_model(filename='saved_models/heart_disease_model.pkl'):
   
    try:
        model = joblib.load(filename)
        return model
    except Exception as e:
        print(f"Failed to load model: {e}")
        return None

def preprocess_input(X_new, scaler_path='saved_models/scaler.pkl'):
   
    try:
        scaler = joblib.load(scaler_path)
        X_processed = scaler.transform(X_new.reshape(1, -1))  
        return X_processed
    except Exception as e:
        print(f"Failed to preprocess input: {e}")
        return None

def make_prediction(model, X_new):
   
    if model is not None:
        try:
            prediction = model.predict(X_new)
            return prediction
        except Exception as e:
            print(f"Prediction failed: {e}")
    return None

if __name__ == "__main__":
    model_path = 'saved_models/heart_disease_model.pkl'
    scaler_path = 'saved_models/scaler.pkl' 
    model = load_model(model_path)
   
    X_new = np.array([57, 1, 2, 140, 240, 0, 1, 140, 0, 2.3, 1, 0, 2])  
    X_new_processed = preprocess_input(X_new, scaler_path)
    if X_new_processed is not None:
        prediction = make_prediction(model, X_new_processed)
        print(f"Prediction: {'Disease' if prediction[0] == 1 else 'No Disease'}")
    else:
        print("Preprocessing failed.")
