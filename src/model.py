import tensorflow as tf

def load_model(model_path):
    return tf.keras.models.load_model(model_path)

def predict(model, input_data):
    prediction = model.predict(input_data)
    return prediction
