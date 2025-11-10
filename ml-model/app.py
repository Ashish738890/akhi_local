import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import pickle

# ---- Config ----
MODEL_PATH = os.environ.get("MODEL_PATH", "models/crop_model.pkl")
LABEL_ENCODER_PATH = os.environ.get("LABEL_ENCODER_PATH", "models/label_encoder.pkl")
PORT = int(os.environ.get("PORT", 5001))
DEBUG = os.environ.get("FLASK_DEBUG", "True").lower() in ("1", "true", "yes")

# ---- App setup ----
app = Flask(__name__)
CORS(app)  # allow cross-origin requests (remove or restrict in prod)

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ---- Model loading ----
if not os.path.exists(MODEL_PATH):
    logger.error("Model file not found at: %s", MODEL_PATH)
    raise FileNotFoundError(f"Model file not found at: {MODEL_PATH}")

with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)
logger.info("Model loaded from %s", MODEL_PATH)

# Optional: load label encoder if available (if you encoded labels during training)
label_encoder = None
if os.path.exists(LABEL_ENCODER_PATH):
    try:
        with open(LABEL_ENCODER_PATH, "rb") as f:
            label_encoder = pickle.load(f)
        logger.info("Label encoder loaded from %s", LABEL_ENCODER_PATH)
    except Exception as e:
        logger.warning("Could not load label encoder: %s", e)

# ---- Helper functions ----
def validate_input(data):
    """
    Expects JSON with numeric keys:
    N, P, K, temperature, humidity, ph, rainfall
    Returns tuple (valid, message or features)
    """
    required = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
    missing = [k for k in required if k not in data]
    if missing:
        return False, f"Missing fields: {', '.join(missing)}"

    try:
        features = [
            float(data["N"]), float(data["P"]), float(data["K"]),
            float(data["temperature"]), float(data["humidity"]),
            float(data["ph"]), float(data["rainfall"])
        ]
    except (ValueError, TypeError) as e:
        return False, f"Invalid number in input: {e}"

    return True, np.array([features])

# ---- Routes ----
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ok", "message": "🌾 ML Model API Running"})

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(force=True, silent=True)
    if data is None:
        return jsonify({"success": False, "error": "Invalid or missing JSON body"}), 400

    valid, payload = validate_input(data)
    if not valid:
        return jsonify({"success": False, "error": payload}), 400

    features = payload  # numpy array shaped (1,7)
    try:
        prediction = model.predict(features)
        if label_encoder is not None:
            try:
                predicted_label = label_encoder.inverse_transform(prediction)[0]
            except Exception:
                predicted_label = prediction[0]
        else:
            # If model returns bytes or numpy.str_, convert to native python str
            predicted_label = prediction[0].item() if hasattr(prediction[0], "item") else prediction[0]

        return jsonify({"success": True, "recommended_crop": str(predicted_label)})
    except Exception as e:
        logger.exception("Prediction error")
        return jsonify({"success": False, "error": f"Prediction failed: {str(e)}"}), 500

# ---- Health endpoint ----
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "model_loaded": True})

# ---- Run ----
if __name__ == "__main__":
    logger.info("Starting Flask app on port %s (debug=%s)", PORT, DEBUG)
    app.run(host="0.0.0.0", port=PORT, debug=DEBUG)

    app.run(port=5001, debug=True)
