import os
import io
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import pickle

# ---- Optional TensorFlow / Keras for pest CNN ----
CNN_ENABLED = os.environ.get("PestCNNEnabled", "true").lower() in ("1", "true", "yes")
if CNN_ENABLED:
    import tensorflow as tf
    from tensorflow.keras.preprocessing import image
    from PIL import Image

# =======================
# ---- Config (ENV) -----
# =======================
# Crop model
MODEL_PATH = os.environ.get("MODEL_PATH", "models/crop_model.pkl")
LABEL_ENCODER_PATH = os.environ.get("LABEL_ENCODER_PATH", "models/label_encoder.pkl")

# Pest model
PEST_MODEL_PATH = os.environ.get("PEST_MODEL_PATH", "models/pest_cnn_model.h5")
PEST_DATA_DIR   = os.environ.get("PEST_DATA_DIR", "data/pest_dataset")   # used to derive class names
PEST_IMG_SIZE   = int(os.environ.get("PEST_IMG_SIZE", "128"))

PORT  = int(os.environ.get("PORT", 5001))
DEBUG = os.environ.get("FLASK_DEBUG", "True").lower() in ("1", "true", "yes")

# =======================
# ---- App setup --------
# =======================
app = Flask(__name__)
CORS(app)  # allow cross-origin requests (tighten in prod)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ml-api")

# =======================
# ---- Load Crop model --
# =======================
if not os.path.exists(MODEL_PATH):
    logger.error("Crop model file not found at: %s", MODEL_PATH)
    raise FileNotFoundError(f"Crop model file not found at: {MODEL_PATH}")

with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)
logger.info("Crop model loaded from %s", MODEL_PATH)

label_encoder = None
if os.path.exists(LABEL_ENCODER_PATH):
    try:
        with open(LABEL_ENCODER_PATH, "rb") as f:
            label_encoder = pickle.load(f)
        logger.info("Crop label encoder loaded from %s", LABEL_ENCODER_PATH)
    except Exception as e:
        logger.warning("Could not load crop label encoder: %s", e)

# =======================
# ---- Load Pest model --
# =======================
pest_model = None
pest_classes = None

if CNN_ENABLED:
    try:
        if not os.path.exists(PEST_MODEL_PATH):
            logger.warning("PEST CNN enabled but model not found at %s", PEST_MODEL_PATH)
        else:
            pest_model = tf.keras.models.load_model(PEST_MODEL_PATH)
            logger.info("Pest CNN model loaded from %s", PEST_MODEL_PATH)

        # Derive class list from dataset folder names (the flow_from_directory convention)
        if os.path.isdir(PEST_DATA_DIR):
            pest_classes = sorted(
                [d for d in os.listdir(PEST_DATA_DIR) if os.path.isdir(os.path.join(PEST_DATA_DIR, d))]
            )
            if not pest_classes:
                pest_classes = None
                logger.warning("No class folders found under %s", PEST_DATA_DIR)
            else:
                logger.info("Pest classes: %s", pest_classes)
        else:
            logger.warning("PEST_DATA_DIR not a directory: %s", PEST_DATA_DIR)
    except Exception as e:
        logger.exception("Failed to load pest CNN: %s", e)
        pest_model = None

# =======================
# ---- Helpers ----------
# =======================
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

def load_and_preprocess_image(file_bytes: bytes, target_size=(128, 128)):
    # Load via PIL to be robust to different formats
    img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
    img = img.resize(target_size)
    arr = np.array(img, dtype=np.float32) / 255.0
    return np.expand_dims(arr, axis=0)

# =======================
# ---- Routes -----------
# =======================
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ok", "message": "🌾 ML Model API Running"})

# ---- Crop prediction (existing) ----
@app.route("/predict", methods=["POST"])
def predict_crop():
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
            predicted_label = prediction[0].item() if hasattr(prediction[0], "item") else prediction[0]

        return jsonify({"success": True, "recommended_crop": str(predicted_label)})
    except Exception as e:
        logger.exception("Prediction error")
        return jsonify({"success": False, "error": f"Prediction failed: {str(e)}"}), 500

# ---- Pest detection (new) ----
@app.route("/predict-pest", methods=["POST"])
def predict_pest():
    if not CNN_ENABLED or pest_model is None:
        return jsonify({"success": False, "error": "Pest model not available"}), 503

    if "file" not in request.files:
        return jsonify({"success": False, "error": "No file uploaded (field name must be 'file')"}), 400

    try:
        f = request.files["file"]
        file_bytes = f.read()
        img_tensor = load_and_preprocess_image(file_bytes, (PEST_IMG_SIZE, PEST_IMG_SIZE))

        preds = pest_model.predict(img_tensor)
        idx = int(np.argmax(preds, axis=1)[0])
        conf = float(np.max(preds))

        if pest_classes and 0 <= idx < len(pest_classes):
            label = pest_classes[idx]
        else:
            label = str(idx)  # fallback to index if classes are unknown

        return jsonify({
            "success": True,
            "pest": label,
            "confidence": round(conf * 100, 2)
        })
    except Exception as e:
        logger.exception("Pest prediction error")
        return jsonify({"success": False, "error": f"Pest prediction failed: {str(e)}"}), 500

# ---- Health endpoint ----
@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "crop_model_loaded": True,
        "pest_model_loaded": bool(pest_model is not None),
        "classes": pest_classes if pest_classes else []
    })

# ---- Run ----
if __name__ == "__main__":
    logger.info("Starting Flask app on port %s (debug=%s)", PORT, DEBUG)
    app.run(host="0.0.0.0", port=PORT, debug=DEBUG)

