# Dental X-ray Analyzer

This project is a web-based dashboard for uploading dental DICOM X-ray images, running AI-based pathology detection (via Roboflow), and visualizing annotated results and diagnostic reports.

---

## Features

- Upload dental DICOM (.dcm) or RVG files
- Automatic conversion and normalization of images
- AI-powered detection of dental pathologies (Roboflow API)
- Visualization of bounding boxes and pathology labels on the X-ray
- Diagnostic report generation
- Modern, responsive dashboard UI

---

## Backend Setup (FastAPI)

1. **Install Python dependencies:**

   ```bash
   cd backend
   pip install -r requirements.txt
   ```
**Note: For DICOM JPEG decompression, you may need:**
```bash
pip install gdcm pylibjpeg pylibjpeg-libjpeg
```



2. ## Run The Fastapi server 
```bash
 uvicorn main:app --reload 
```


## Frontend Setup (React)

1. **Install Node Dependencies**
```bash
cd frontend
npm install
```

2. **Start The React Development Server**
```bash
npm run dev
```