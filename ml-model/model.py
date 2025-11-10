import numpy as np
import pickle
import os

# Load the trained model
model_path = os.path.join('models', 'crop_model.pkl')
model = pickle.load(open(model_path, 'rb'))

def predict_crop(N, P, K, temperature, humidity, ph, rainfall):
    features = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
    prediction = model.predict(features)
    return prediction[0]
