from flask import Flask, request, jsonify
from flask_cors import CORS
from ultralytics import YOLO
from PIL import Image
import os
import gdown

app = Flask(__name__)
CORS(app)

# === MODEL SETUP ===
MODEL_PATH = "best.pt"
DRIVE_FILE_ID = "1-AnA0UPIwZHxdEEOKf1Ilyeqij1Bdhfm"  # your actual file ID

def download_model_if_needed():
    if not os.path.exists(MODEL_PATH):
        print("Downloading YOLO model from Google Drive using gdown...")
        url = f"https://drive.google.com/uc?id={DRIVE_FILE_ID}"
        gdown.download(url, MODEL_PATH, quiet=False)
        print("Model downloaded.")

download_model_if_needed()
model = YOLO(MODEL_PATH)

# === PREDICT ENDPOINT ===
@app.route("/predict", methods=["POST"])
def predict():
    if "image" not in request.files:
        return jsonify({"error": "No image provided"}), 400

    try:
        img = Image.open(request.files["image"].stream)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    results = model(img)
    predictions = []

    for result in results:
        for box in result.boxes:
            predictions.append({
                "class": model.names[int(box.cls[0])],
                "confidence": round(float(box.conf[0]), 3)
            })

    return jsonify({"predictions": predictions})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
