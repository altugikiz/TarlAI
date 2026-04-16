"""
TarlAI Tools - Weather API and Plant Disease Treatment Database
Used by Gemma 4 via native function calling
"""

import json
import sys
import os

# diseases.py ile aynı klasörde olduğu için path ekle
sys.path.insert(0, os.path.dirname(__file__))
from diseases import DISEASE_DB


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
    key = disease_name.lower().replace(" ", "_").strip()
    for disease, data in DISEASE_DB.items():
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
    # Test - mevcut
    print("Weather test:", json.dumps(get_weather("Antalya"), indent=2))
    print("Treatment test (leaf_spot):", json.dumps(get_treatment("leaf_spot"), indent=2))

    # Test - yeni hastalıklar
    test_diseases = [
        "citrus_greening", "fusarium_wilt", "grape_black_rot",
        "olive_peacock_spot", "blossom_end_rot", "gray_mold",
        "unknown_disease"
    ]
    print(f"\n--- Toplam hastalık sayısı: {len(DISEASE_DB)} ---")
    for d in test_diseases:
        result = get_treatment(d)
        status = "BULUNDU" if result.get("notes") != "Disease not found in database" else "BULUNAMADI"
        print(f"[{status}] {d}: {result.get('name', 'N/A')}")
