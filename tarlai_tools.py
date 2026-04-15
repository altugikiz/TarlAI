"""
TarlAI Tools - Weather API and Plant Disease Treatment Database
Used by Gemma 4 via native function calling
"""

import json


def get_weather(location: str) -> dict:
    """
    Get current weather information for a given location.
    Args:
        location: City name, e.g. 'Antalya' or 'Istanbul'
    Returns:
        Weather data including temperature, humidity, rain probability
    """
    # TODO: Replace with OpenWeatherMap API in production
    db = {
        "antalya": {"temp": 26, "humidity": 72, "rain_pct": 15, "wind_kmh": 12, "condition": "Sunny"},
        "istanbul": {"temp": 18, "humidity": 65, "rain_pct": 40, "wind_kmh": 22, "condition": "Cloudy"},
        "izmir": {"temp": 24, "humidity": 58, "rain_pct": 10, "wind_kmh": 15, "condition": "Sunny"},
        "mugla": {"temp": 25, "humidity": 60, "rain_pct": 20, "wind_kmh": 14, "condition": "Partly Cloudy"},
        "burdur": {"temp": 22, "humidity": 50, "rain_pct": 5, "wind_kmh": 8, "condition": "Sunny"},
        "konya": {"temp": 20, "humidity": 45, "rain_pct": 10, "wind_kmh": 18, "condition": "Sunny"},
        "mersin": {"temp": 27, "humidity": 75, "rain_pct": 20, "wind_kmh": 10, "condition": "Partly Cloudy"},
        "adana": {"temp": 28, "humidity": 70, "rain_pct": 15, "wind_kmh": 8, "condition": "Sunny"},
    }
    key = location.lower().strip()
    for city, data in db.items():
        if city in key:
            return {"location": location, **data}
    return {"location": location, "temp": 20, "humidity": 60, "rain_pct": 25, "wind_kmh": 10, "condition": "Unknown"}


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