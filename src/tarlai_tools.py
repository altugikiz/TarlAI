"""
TarlAI Tools - Weather API and Plant Disease Treatment Database
Used by Gemma 4 via native function calling
"""

import json
import os
import requests
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# OpenWeatherMap condition code -> basitleştirilmiş durum eşlemesi
_CONDITION_MAP = {
    "Clear": "Sunny",
    "Clouds": "Cloudy",
    "Rain": "Rainy",
    "Drizzle": "Rainy",
    "Thunderstorm": "Stormy",
    "Snow": "Snowy",
    "Mist": "Foggy",
    "Fog": "Foggy",
    "Haze": "Hazy",
}


def get_weather(location: str) -> dict:
    """
    Get current weather information for a given location via OpenWeatherMap API.

    Args:
        location: City name, e.g. 'Antalya' or 'Istanbul'
    Returns:
        Weather data including temperature, humidity, rain probability
    """
    if not OPENWEATHER_API_KEY or OPENWEATHER_API_KEY == "YOUR_API_KEY_HERE":
        return {"location": location, "error": "API key tanımlanmamış. .env dosyasını kontrol edin."}

    try:
        params = {
            "q": f"{location},TR",
            "appid": OPENWEATHER_API_KEY,
            "units": "metric",       # Celsius
            "lang": "tr",            # Türkçe açıklamalar
        }
        response = requests.get(OPENWEATHER_BASE_URL, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        # Ana hava durumu bilgisini çıkar
        main = data.get("main", {})
        wind = data.get("wind", {})
        weather_info = data.get("weather", [{}])[0]
        clouds = data.get("clouds", {})

        # Yağış olasılığı: bulutluluk yüzdesini kullan
        rain_pct = clouds.get("all", 0)

        # Ana durum kategorisini basitleştir
        main_condition = weather_info.get("main", "Unknown")
        condition = _CONDITION_MAP.get(main_condition, main_condition)

        return {
            "location": location,
            "temp": round(main.get("temp", 0)),
            "feels_like": round(main.get("feels_like", 0)),
            "humidity": main.get("humidity", 0),
            "rain_pct": rain_pct,
            "wind_kmh": round(wind.get("speed", 0) * 3.6),  # m/s -> km/h
            "condition": condition,
            "description": weather_info.get("description", ""),
        }
    except requests.RequestException as e:
        return {"location": location, "error": f"API hatası: {e}"}


def get_treatment(disease_name: str) -> dict:
    """
    Get treatment information for a plant disease.
    Args:
        disease_name: Name of the disease, e.g. 'early_blight', 'powdery_mildew', 'leaf_spot'
    Returns:
        Treatment details including chemical and organic options
    """
    db = {
        "leaf_spot": {
            "name": "Leaf Spot (Yaprak Lekesi)",
            "chemical": "Copper-based fungicide, Mancozeb",
            "organic": "Bordeaux mixture, Neem oil",
            "interval": "7-14 days",
            "notes": "Avoid overhead watering"
        },
        "early_blight": {
            "name": "Early Blight (Erken Yaniklik)",
            "chemical": "Mancozeb, Chlorothalonil",
            "organic": "Neem oil, copper sulfate solution",
            "interval": "7-10 days",
            "notes": "Apply early morning or late evening"
        },
        "late_blight": {
            "name": "Late Blight (Gec Yaniklik)",
            "chemical": "Metalaxyl, Bordeaux mixture",
            "organic": "Bordeaux mixture (copper based)",
            "interval": "5-7 days",
            "notes": "Remove infected leaves immediately"
        },
        "powdery_mildew": {
            "name": "Powdery Mildew (Kulleme)",
            "chemical": "Sulfur-based fungicide",
            "organic": "Milk-water mix (40% milk)",
            "interval": "7 days",
            "notes": "Improve air circulation between plants"
        },
        "downy_mildew": {
            "name": "Downy Mildew (Mildiyou)",
            "chemical": "Metalaxyl, Fosetyl-Al",
            "organic": "Copper hydroxide",
            "interval": "7-10 days",
            "notes": "Ensure good drainage"
        },
        "rust": {
            "name": "Rust (Pas Hastaligi)",
            "chemical": "Triadimefon, Propiconazole",
            "organic": "Sulfur dust, Neem oil",
            "interval": "7-14 days",
            "notes": "Remove infected plant debris"
        },
        "anthracnose": {
            "name": "Anthracnose (Antrakoz)",
            "chemical": "Chlorothalonil, Copper fungicide",
            "organic": "Bordeaux mixture",
            "interval": "7-10 days",
            "notes": "Avoid working with wet plants"
        },
        "bacterial_spot": {
            "name": "Bacterial Spot (Bakteriyel Leke)",
            "chemical": "Copper-based bactericide",
            "organic": "Copper hydroxide spray",
            "interval": "5-7 days",
            "notes": "No cure once established, focus on prevention"
        },
        "mosaic_virus": {
            "name": "Mosaic Virus (Mozaik Virusu)",
            "chemical": "No chemical treatment available",
            "organic": "Remove and destroy infected plants",
            "interval": "N/A",
            "notes": "Control aphid vectors, use resistant varieties"
        },
        "root_rot": {
            "name": "Root Rot (Kok Curumesi)",
            "chemical": "Metalaxyl soil drench",
            "organic": "Improve drainage, reduce watering",
            "interval": "14-21 days",
            "notes": "Avoid waterlogged conditions"
        },
    }
    key = disease_name.lower().replace(" ", "_").strip()
    for disease, data in db.items():
        if disease in key or key in disease:
            return data
    return {
        "name": disease_name,
        "chemical": "Consult local agricultural office",
        "organic": "N/A",
        "interval": "N/A",
        "notes": "Disease not found in database"
    }


if __name__ == "__main__":
    # Test
    print("Weather test:", json.dumps(get_weather("Antalya"), indent=2))
    print("Treatment test:", json.dumps(get_treatment("leaf_spot"), indent=2))
