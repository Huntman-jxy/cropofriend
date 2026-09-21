import requests

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


def get_weather(latitude: float, longitude: float):
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,precipitation,weather_code",
        "timezone": "auto",
    }

    response = requests.get(OPEN_METEO_URL, params=params, timeout=10)
    response.raise_for_status()

    current = response.json().get("current", {})

    return {
        "temperature": current.get("temperature_2m"),
        "humidity": current.get("relative_humidity_2m"),
        "precipitation": current.get("precipitation"),
        "weather_code": current.get("weather_code"),
    }
