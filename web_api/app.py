import io
import numpy as np
import torch
from flask import Flask, render_template, request, redirect, url_for, flash
from PIL import Image
from model import ECG_Classifier
from mongo import Mongo_Client
from transformer import transform

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
CLASSES = ["Ab-Normal HeartBeat", "STEMI", "Patient With History of MI ", "Normal ECG"]

app = Flask(__name__, static_url_path="/static", static_folder="static")
app.secret_key = 'your-secret-key-here'  # Required for flash messages

def upload_to_mongo(diagnosis, patient_id):
    try:
        document = {"_id": patient_id, "diagnosis": diagnosis}
        mongo_client = Mongo_Client()
        mongo_client.insert_document(document)
        print("Document Inserted Successfully!")
    except Exception as e:
        print(f"MongoDB Error: {str(e)}")
        # Continue even if MongoDB fails
        pass

def transform_to_tensor(image):
    try:
        image_tensor = transform(image)
        image_tensor = image_tensor.unsqueeze(0)
        return image_tensor
    except Exception as e:
        print(f"Transform Error: {str(e)}")
        raise

def make_prediction(image):
    """
    Utilize the model to predict the ECG diagnosis
    """
    try:
        model = ECG_Classifier(num_classes=4)
        model.load_state_dict(
            torch.load("backend/ecg_classifier.pth", weights_only=True, map_location=DEVICE)
        )
        model.eval()
        with torch.no_grad():
            image_tensor = image.to(DEVICE)
            outputs = model(image_tensor)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)
            probabilities = probabilities.cpu().numpy().flatten()
        predicted_class = CLASSES[np.argmax(probabilities)]
        print(f"Prediction made successfully: {predicted_class}")
        return predicted_class
    except Exception as e:
        print(f"Prediction Error: {str(e)}")
        raise

def check_validity(patient_id, files):
    """
    Check validity of patient ID and uploaded file
    """
    if not patient_id or patient_id.strip() == "":
        return False, "No ID was entered for patient."

    if "file" not in files:
        return False, "No file was uploaded"

    file = files["file"]
    if file.filename == "":
        return False, "No file was selected"

    return True, None

@app.route("/", methods=["GET"])
def home():
    """
    Landing page
    """
    return render_template('home.html')

@app.route("/show_results", methods=["POST"])
def get_ecg_info():
    """
    Handle file upload and processing
    """
    try:
        print("Starting upload process...")
        patient_id = request.form.get("patient_id")
        print(f"Patient ID received: {patient_id}")

        # Check validity
        is_valid, error_message = check_validity(patient_id, request.files)
        if not is_valid:
            print(f"Validation failed: {error_message}")
            return f"Error: {error_message}", 400

        file = request.files["file"]
        print(f"File received: {file.filename}")

        # Read and process the image
        img_bytes = file.read()
        img = Image.open(io.BytesIO(img_bytes))
        image_tensor = transform_to_tensor(img)
        print("Image transformed successfully")

        # Get diagnosis
        diagnosis = make_prediction(image_tensor)
        print(f"Diagnosis obtained: {diagnosis}")

        # Upload to MongoDB
        upload_to_mongo(diagnosis, patient_id)

        # Render the results template
        return render_template("show_results.html",
                             diagnosis=diagnosis,
                             patient_id=patient_id)

    except Exception as e:
        print(f"Error in get_ecg_info route: {str(e)}")
        return f"An error occurred: {str(e)}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)