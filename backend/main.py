from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pydicom
import io
import base64
from PIL import Image
import requests
import numpy as np

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ROBOFLOW_API_KEY = "rf_aFN0eBZhgNPw0dcYmSKe08mLTDv1"
ROBOFLOW_MODEL_ENDPOINT = "https://detect.roboflow.com/adr/6"


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Read DICOM file
        contents = await file.read()
        dicom_data = pydicom.dcmread(io.BytesIO(contents))
        pixel_array = dicom_data.pixel_array

        # Normalize pixel values to 0-255 range
        if pixel_array.dtype != np.uint8:
            pixel_min = pixel_array.min()
            pixel_max = pixel_array.max()
            pixel_range = pixel_max - pixel_min
            pixel_array = ((pixel_array - pixel_min) * 255.0 / pixel_range).astype(np.uint8)

        # Create PIL Image (convert to RGB for annotation)
        image = Image.fromarray(pixel_array).convert("RGB")

        # Convert to base64 for Roboflow API
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        img_byte_arr_val = img_byte_arr.getvalue()
        img_base64 = base64.b64encode(img_byte_arr_val).decode()

        # Call Roboflow API
        response = requests.post(
            f"{ROBOFLOW_MODEL_ENDPOINT}",
            headers={
                "Content-Type": "application/x-www-form-urlencoded"
            },
            data={
                "api_key": ROBOFLOW_API_KEY,
                "image": img_base64,
                "confidence": 0.3,
                "overlap": 0.5
            }
        )

        predictions = response.json()
        print("Roboflow predictions:", predictions)  # Debug

        # Draw bounding boxes if present
        annotated_image_base64 = img_base64
        preds = predictions.get("predictions") or predictions.get("objects") or []
        if preds:
            annotated_image = draw_boxes_on_image(image.copy(), preds)
            img_byte_arr_annot = io.BytesIO()
            annotated_image.save(img_byte_arr_annot, format='PNG')
            img_byte_arr_annot.seek(0)
            annotated_image_base64 = base64.b64encode(img_byte_arr_annot.getvalue()).decode()
        else:
            print("No predictions to draw.")

        report = generate_mock_report(predictions)

        return {
            "image": annotated_image_base64,
            "predictions": predictions,
            "report": report
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"error": str(e)}

def draw_boxes_on_image(image, predictions):
    from PIL import ImageDraw, ImageFont

    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("arial.ttf", 18)
    except:
        font = ImageFont.load_default()

    for pred in predictions:
        # Roboflow may return floats, so cast to int
        x, y, w, h = float(pred["x"]), float(pred["y"]), float(pred["width"]), float(pred["height"])
        class_name = pred.get("class", "Unknown")
        confidence = pred.get("confidence", 0)
        left = int(x - w / 2)
        top = int(y - h / 2)
        right = int(x + w / 2)
        bottom = int(y + h / 2)

        # Draw rectangle
        draw.rectangle([left, top, right, bottom], outline="red", width=3)
        # Draw label
        label = f"{class_name} ({confidence:.2f})"
        text_size = draw.textsize(label, font=font)
        # Make sure label is inside image
        label_top = max(0, top - text_size[1] - 4)
        draw.rectangle([left, label_top, left + text_size[0] + 4, label_top + text_size[1] + 4], fill="red")
        draw.text((left + 2, label_top + 2), label, fill="white", font=font)

    return image

def generate_mock_report(predictions):
    return """
    Dental Radiograph Analysis Report
    
    Findings:
    - Detected cavity in upper right molar region
    - Potential periapical lesion observed in lower left quadrant
    
    Recommendations:
    - Immediate attention required for cavity treatment
    - Follow-up examination recommended for periapical lesion
    """