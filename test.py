from flask import Flask, request, jsonify
from flask_cors import CORS
from ultralytics import YOLO
from PIL import Image
import os
import gdown

app = Flask(__name__)
CORS(app)
# === MODEL SETUP ===
MODEL_PATH = "/tmp/best.pt"
DROPBOX_URL = "https://www.dropbox.com/scl/fi/rrlu0zt6jg54kvlsws3ut/best.pt?rlkey=796n2u3qpltl0gy6l8978m109&st=0km7dbh4&dl=1"

def download_model(url, model_path):
    if os.path.exists(model_path):
        print("Model already exists.")
        return

    print("Downloading model...")
    response = requests.get(url, stream=True)

    # Ensure we're not getting HTML
    content_type = response.headers.get("Content-Type", "")
    if "html" in content_type.lower():
        raise ValueError("Downloaded file is HTML, not a model. Dropbox may have restricted access or throttled the request.")

    with open(model_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    print("Model downloaded successfully.")
# Load the model
try:
    model = YOLO(MODEL_PATH)
except Exception as e:
    print(f"Failed to load model from {MODEL_PATH}: {str(e)}")
    raise

# === PREDICT ENDPOINT ===
@app.route("/predict", methods=["POST"])
def predict():
    if "image" not in request.files:
        return jsonify({"error": "No image provided"}), 400

    try:
        img = Image.open(request.files["image"].stream).convert("RGB")
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    results = model(img)

    predictions = []
    for result in results:
        boxes = result.boxes
        for box in boxes:
            cls = int(box.cls[0])
            conf = float(box.conf[0])
            predictions.append({
                "class": model.names[cls],
                "confidence": round(conf, 3)
            })

    return jsonify({"predictions": predictions})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
