import random
from backend.config import RISK_SEED

# Prototype weights. They are initialized deterministically from a seed so the
# demo remains reproducible. They are NOT scientifically validated weights.
_rng = random.Random(RISK_SEED)

RAW_WEIGHTS = {
    "disease": _rng.uniform(0.30, 0.45),
    "pest": _rng.uniform(0.20, 0.35),
    "severity": _rng.uniform(0.10, 0.20),
    "weather": _rng.uniform(0.10, 0.25),
}

total = sum(RAW_WEIGHTS.values())
WEIGHTS = {k: v / total for k, v in RAW_WEIGHTS.items()}


def clamp(value, low=0.0, high=1.0):
    return max(low, min(high, value))


def weather_factor(weather):
    if not weather:
        return 0.0

    humidity = weather.get("humidity")
    precipitation = weather.get("precipitation")

    # Simple prototype environmental-pressure heuristic.
    humidity_score = clamp((float(humidity or 0) - 55) / 40)
    rain_score = clamp(float(precipitation or 0) / 8)

    return 0.6 * humidity_score + 0.4 * rain_score


def calculate_risk(disease_confidence, pest_confidence, severity, weather):
    severity_map = {
        "low": 0.25,
        "mild": 0.25,
        "moderate": 0.60,
        "high": 0.85,
        "severe": 1.00,
    }

    disease_score = clamp(float(disease_confidence or 0))
    pest_score = clamp(float(pest_confidence or 0))
    severity_score = severity_map.get(str(severity or "").lower(), 0.50)
    environment_score = weather_factor(weather)

    score = (
        WEIGHTS["disease"] * disease_score
        + WEIGHTS["pest"] * pest_score
        + WEIGHTS["severity"] * severity_score
        + WEIGHTS["weather"] * environment_score
    )

    percentage = round(clamp(score) * 100, 1)

    if percentage < 35:
        level = "Low"
    elif percentage < 65:
        level = "Moderate"
    elif percentage < 85:
        level = "High"
    else:
        level = "Very High"

    return {
        "percentage": percentage,
        "level": level,
        "weights": {k: round(v, 4) for k, v in WEIGHTS.items()},
        "components": {
            "disease": round(disease_score, 3),
            "pest": round(pest_score, 3),
            "severity": round(severity_score, 3),
            "weather": round(environment_score, 3),
        },
    }
