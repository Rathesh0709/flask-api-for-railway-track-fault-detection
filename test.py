from flask import Flask, request, jsonify
from flask_cors import CORS
from ultralytics import YOLO
from PIL import Image
import requests
import os

app = Flask(__name__)
CORS(app)

# === MODEL SETUP ===
MODEL_PATH = "best.pt"  # Replace with your actual file ID

def download_model_if_needed():
    if not os.path.exists(MODEL_PATH):
        print("Downloading YOLO model from Google Drive...")
        url = f"https://drive.google.com/file/d/1-AnA0UPIwZHxdEEOKf1Ilyeqij1Bdhfm/view?usp=sharing"
        r = requests.get(url)
        with open(MODEL_PATH, "wb") as f:
            f.write(r.content)
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
    app.run(host="0.0.0.0", port=5000)
