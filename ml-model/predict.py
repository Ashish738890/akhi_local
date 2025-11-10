import sys
import json
import pickle
import numpy as np
import os

BASE_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(BASE_DIR, "models", "crop_model.pkl")

def error_response(message):
    print(json.dumps({"error": message}))
    sys.exit(1)

def main():
    try:
        with open(MODEL_PATH, 'rb') as f:
            model = pickle.load(f)
    except Exception as e:
        error_response(f"Model loading failed: {e}")

    try:
        raw_input = sys.stdin.read()
        if not raw_input:
            error_response("No input data received")

        data = json.loads(raw_input)
        features = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']

        # Ensure all required fields exist
        values = [float(data[f]) for f in features]

        prediction = model.predict([values])[0]

        print(json.dumps({"predicted_crop": prediction}))
    except Exception as e:
        error_response(f"Prediction failed: {e}")

if __name__ == "__main__":
    main()



