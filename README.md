# CropOfriend — SIH Deployment-Ready Web App

Minimal full-stack crop health prototype.

## Stack
Frontend: HTML + CSS + JavaScript
Backend: FastAPI + Python
Vision: OpenCV + YOLO
Database: PostgreSQL in production / SQLite fallback locally
Weather: Open-Meteo
Location: browser Geolocation API

## Features
1. Farmer uploads crop image.
2. Browser requests location permission.
3. Image is sent to FastAPI.
4. OpenCV validates/preprocesses the image.
5. Disease and pest YOLO models run.
6. Backend fetches current weather from Open-Meteo using latitude/longitude.
7. A configurable weighted risk score is calculated.
8. Prediction + location + weather + risk are stored in the database.
9. Browser displays the report.

## Local run

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
uvicorn backend.main:app --reload
```

Open http://127.0.0.1:8000

## Models

Put your trained files here:

models/disease_model.pt
models/pest_model.pt

Then set:

USE_MODELS=true

The app can still run without model files using demo mode.

## Production deployment

This repository includes:
- Dockerfile
- render.yaml

For Render:
1. Create a PostgreSQL database.
2. Create a Web Service from this repository.
3. Render will use render.yaml.
4. Set `USE_MODELS=true`.
5. Upload your model weights through your deployment strategy or use a model artifact/object-storage URL.

Important: browser geolocation requires a secure context such as HTTPS and user permission.

## Environment variables

DATABASE_URL=postgresql+psycopg://...
USE_MODELS=false
RISK_SEED=26131
CORS_ORIGINS=*

The risk score is a prototype decision-support score, not a scientifically validated disease probability. Tune/validate the weights with agricultural data before making real-world treatment decisions.
