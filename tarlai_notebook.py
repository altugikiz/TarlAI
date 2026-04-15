"""
TarlAI - AI-Powered Agricultural Assistant
Gemma 4 Good Hackathon Submission

Usage on Kaggle:
  1. Add Gemma 4 E4B-IT model as input
  2. Select GPU T4 x2
  3. Run all cells
  4. Call: tarlai_analyze("path/to/image.jpg", "Antalya")
"""

# --- Setup ---
# !pip install --upgrade transformers accelerate -q

from transformers import pipeline, GenerationConfig
from PIL import Image
from IPython.display import display
import json
import re

# --- Configuration ---
# Update this path based on your Kaggle model input
MODEL_PATH = "/kaggle/input/models/google/gemma-4/transformers/gemma-4-e4b-it/1"
# For Hugging Face: MODEL_PATH = "google/gemma-4-E4B-it"

# --- Load Model ---
print("Loading Gemma 4 E4B-IT model...")
vqa_pipe = pipeline(
    task="image-text-to-text",
    model=MODEL_PATH,
    device_map="auto",
    dtype="auto"
)
config = GenerationConfig.from_pretrained(MODEL_PATH)
config.max_new_tokens = 1024
gen_kwargs = dict(generation_config=config)
print("Model ready!")


# --- Tool Definitions ---

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
        "leaf_spot": {"name": "Leaf Spot", "chemical": "Copper-based fungicide, Mancozeb", "organic": "Bordeaux mixture, Neem oil", "interval": "7-14 days"},
        "early_blight": {"name": "Early Blight", "chemical": "Mancozeb, Chlorothalonil", "organic": "Neem oil, copper sulfate", "interval": "7-10 days"},
        "late_blight": {"name": "Late Blight", "chemical": "Metalaxyl, Bordeaux mixture", "organic": "Bordeaux mixture", "interval": "5-7 days"},
        "powdery_mildew": {"name": "Powdery Mildew", "chemical": "Sulfur-based fungicide", "organic": "Milk-water mix 40%", "interval": "7 days"},
        "downy_mildew": {"name": "Downy Mildew", "chemical": "Metalaxyl, Fosetyl-Al", "organic": "Copper hydroxide", "interval": "7-10 days"},
    }
    key = disease_name.lower().replace(" ", "_").strip()
    for disease, data in db.items():
        if disease in key or key in disease:
            return data
    return {"name": disease_name, "info": "Not found - consult local agricultural office"}


# --- Main Analysis Function ---

def tarlai_analyze(image_path, location="Antalya"):
    """
    Analyze a plant image for disease and provide treatment recommendations.
    
    Args:
        image_path: Path to the plant image file
        location: City name for weather data (default: Antalya)
    
    Returns:
        Prints diagnosis, weather info, and treatment recommendations in Turkish
    """
    img = Image.open(image_path)
    display(img.resize((400, 300)))
    
    print(f"\n>> Location: {location}")
    print(">> Diagnosing with Gemma 4...\n")
    
    # Step 1: Vision - diagnose disease
    msg1 = [{"role": "user", "content": [
        {"type": "image", "image": img},
        {"type": "text", "text": 'You are an expert agricultural engineer. Analyze this plant image. '
         'Respond ONLY with JSON: {"plant": "name", "disease": "name", '
         '"severity": "mild/moderate/severe", "disease_key": "snake_case_name"}'}
    ]}]
    
    diag = vqa_pipe(msg1, return_full_text=False, generate_kwargs=gen_kwargs)
    diag_text = diag[0]['generated_text']
    
    try:
        match = re.search(r'\{[^}]+\}', diag_text)
        diagnosis = json.loads(match.group()) if match else {
            "plant": "Unknown", "disease": "Unknown",
            "severity": "unknown", "disease_key": "unknown"
        }
    except Exception:
        diagnosis = {
            "plant": "Unknown", "disease": "Unknown",
            "severity": "unknown", "disease_key": "unknown"
        }
    
    # Step 2: Get weather and treatment data
    weather = get_weather(location)
    treatment = get_treatment(diagnosis.get("disease_key", "unknown"))
    
    print(f">> Plant: {diagnosis.get('plant')}")
    print(f">> Disease: {diagnosis.get('disease')}")
    print(f">> Severity: {diagnosis.get('severity')}")
    print(f">> Weather: {weather.get('condition')}, {weather.get('temp')}C")
    print("\n>> Generating recommendation...\n")
    
    # Step 3: Generate final recommendation in Turkish
    msg2 = [{"role": "user", "content": [
        {"type": "image", "image": img},
        {"type": "text", "text": f"""You are TarlAI, an agricultural AI assistant for Turkish farmers.
Ignore the image. Based on this data, give a complete recommendation in Turkish:
DIAGNOSIS: {json.dumps(diagnosis)}
WEATHER: {json.dumps(weather)}
TREATMENT: {json.dumps(treatment)}
Cover: 1) Disease found 2) Treatment options 3) When to spray based on weather 4) Prevention tips
Use simple Turkish a farmer can understand."""}
    ]}]
    
    final = vqa_pipe(msg2, return_full_text=False, generate_kwargs=gen_kwargs)
    result = final[0]['generated_text'].replace("<turn|>", "").replace("<eos>", "").strip()
    
    print("=" * 50)
    print("TARLAI - ANALYSIS REPORT")
    print("=" * 50)
    print(result)
    print("=" * 50)


# --- Run ---
print("\nTarlAI ready! Usage: tarlai_analyze('path/to/image.jpg', 'Antalya')")

# Example:
# tarlai_analyze("/kaggle/input/datasets/altugikiz/hastabitki/hastabitki.jpg", "Antalya")