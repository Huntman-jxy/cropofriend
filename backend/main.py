from pathlib import Path
import shutil
import tempfile

from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.config import BASE_DIR, CORS_ORIGINS
from backend.database import Base, engine, SessionLocal, Analysis
from backend.inference import infer
from backend.risk import calculate_risk
from backend.weather import get_weather

Base.metadata.create_all(bind=engine)

app = FastAPI(title="CropOfriend API")
OUTPUTS_DIR = BASE_DIR / "outputs"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

app.mount(
    "/outputs",
    StaticFiles(directory=OUTPUTS_DIR),
    name="outputs",
)

origins = [x.strip() for x in CORS_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins != ["*"] else ["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = BASE_DIR / "frontend"
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/")
def home():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "cropofriend"}


@app.post("/api/analyze")
async def analyze(
    image: UploadFile = File(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
):
    crop = "Unknown"
    suffix = Path(image.filename or ".jpg").suffix or ".jpg"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(image.file, tmp)
        image_path = Path(tmp.name)

    try:
        try:
            model_result = infer(image_path)
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc))

        try:
            weather = get_weather(latitude, longitude)
        except Exception as exc:
            weather = {
                "temperature": None,
                "humidity": None,
                "precipitation": None,
                "weather_code": None,
                "error": f"Weather unavailable: {exc}",
            }

        disease = model_result["disease_detections"][0] if model_result["disease_detections"] else None
        pest = model_result["pest_detections"][0] if model_result["pest_detections"] else None

        risk = calculate_risk(
            disease_confidence=disease["confidence"] if disease else 0,
            pest_confidence=pest["confidence"] if pest else 0,
            severity=model_result["severity"],
            weather=weather,
        )

        result = {
            "crop": crop,
            "location": 
            {
            "latitude": latitude,
            "longitude": longitude,
            },
            "disease": disease,
            "pest": pest,
            "severity": model_result["severity"],
            "weather": weather,
            "risk": risk,
            "demo": model_result["demo"],
            "preprocess": model_result["preprocess"],

            "disease_image": model_result.get("disease_image"),
            "pest_image": model_result.get("pest_image"),
        }

        db = SessionLocal()
        try:
            row = Analysis(
                crop=crop,
                latitude=latitude,
                longitude=longitude,
                disease=disease["label"] if disease else "None detected",
                disease_confidence=disease["confidence"] if disease else 0,
                pest=pest["label"] if pest else "None detected",
                pest_confidence=pest["confidence"] if pest else 0,
                severity=model_result["severity"],
                risk_score=risk["percentage"],
                risk_level=risk["level"],
                temperature=weather.get("temperature"),
                humidity=weather.get("humidity"),
                precipitation=weather.get("precipitation"),
                weather_code=weather.get("weather_code"),
                raw_result=result,
            )
            db.add(row)
            db.commit()
            result["analysis_id"] = row.id
        finally:
            db.close()

        return result

    finally:
        image_path.unlink(missing_ok=True)

# ==========================================
# GIS DEMO HOTSPOT DATA
# ==========================================

demo_hotspots = [

    {
        "lat": 23.5204,
        "lon": 87.3119,
        "crop": "Tomato",
        "problem": "Early Blight",
        "type": "Disease",
        "reports": 18,
        "severity": 72,
        "risk": 84
    },

    {
        "lat": 23.5260,
        "lon": 87.3180,
        "crop": "Potato",
        "problem": "Late Blight",
        "type": "Disease",
        "reports": 12,
        "severity": 61,
        "risk": 76
    },

    {
        "lat": 23.5150,
        "lon": 87.3050,
        "crop": "Tomato",
        "problem": "Aphids",
        "type": "Pest",
        "reports": 23,
        "severity": 48,
        "risk": 68
    },

    {
        "lat": 23.5300,
        "lon": 87.3260,
        "crop": "Rice",
        "problem": "Brown Planthopper",
        "type": "Pest",
        "reports": 31,
        "severity": 67,
        "risk": 81
    },

    {
        "lat": 23.5090,
        "lon": 87.3190,
        "crop": "Tomato",
        "problem": "Early Blight",
        "type": "Disease",
        "reports": 9,
        "severity": 32,
        "risk": 51
    }

]


# ==========================================
# GIS HOTSPOT API
# ==========================================

@app.get("/api/hotspots")
def get_hotspots():

    return {
        "demo": True,

        "message":
            "Simulated data for demonstration",

        "hotspots":
            demo_hotspots
    }   