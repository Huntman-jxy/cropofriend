import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "models"

DISEASE_MODEL = MODEL_DIR / "best1.pt"
PEST_MODEL = MODEL_DIR / "best.pt"
OUTPUTS_DIR = BASE_DIR / "outputs"

USE_MODELS = True
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'cropofriend.db'}")
RISK_SEED = int(os.getenv("RISK_SEED", "26131"))
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")
