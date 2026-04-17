"""
TarlAI Pipeline - Core analysis logic
Connects Gemma 4 vision, function calling, and recommendation generation
"""

from PIL import Image
from IPython.display import display
import json
import re


def diagnose_plant(vqa_pipe, gen_kwargs, image):
    """
    Stage 1: Use Gemma 4 vision to diagnose plant disease from image.
    
    Args:
        vqa_pipe: Hugging Face image-text-to-text pipeline
        gen_kwargs: Generation config kwargs
        image: PIL Image object
    
    Returns:
        dict with keys: plant, disease, severity, disease_key
    """
    messages = [{"role": "user", "content": [
        {"type": "image", "image": image},
        {"type": "text", "text": (
            'You are an expert agricultural engineer. Analyze this plant image. '
            'Respond ONLY with JSON: {"plant": "name", "disease": "name", '
            '"severity": "mild/moderate/severe", "disease_key": "snake_case_name"}'
        )}
    ]}]
    
    output = vqa_pipe(messages, return_full_text=False, generate_kwargs=gen_kwargs)
    raw = output[0]['generated_text']
    
    try:
        match = re.search(r'\{[^}]+\}', raw)
        return json.loads(match.group()) if match else _default_diagnosis()
    except Exception:
        return _default_diagnosis()


def generate_recommendation(vqa_pipe, gen_kwargs, image, diagnosis, weather, treatment):
    """
    Stage 3: Generate final Turkish recommendation combining all data.
    
    Args:
        vqa_pipe: Hugging Face pipeline
        gen_kwargs: Generation config
        image: PIL Image (passed for pipeline compatibility)
        diagnosis: dict from diagnose_plant()
        weather: dict from get_weather()
        treatment: dict from get_treatment()
    
    Returns:
        str: Turkish recommendation text
    """
    messages = [{"role": "user", "content": [
        {"type": "image", "image": image},
        {"type": "text", "text": f"""You are TarlAI, an agricultural AI assistant for Turkish farmers.
Ignore the image. Based on this data, give a complete recommendation in Turkish:
DIAGNOSIS: {json.dumps(diagnosis)}
WEATHER: {json.dumps(weather)}
TREATMENT: {json.dumps(treatment)}
Cover: 1) Disease found 2) Treatment options 3) When to spray based on weather 4) Prevention tips
Use simple Turkish a farmer can understand."""}
    ]}]
    
    output = vqa_pipe(messages, return_full_text=False, generate_kwargs=gen_kwargs)
    return output[0]['generated_text'].replace("<turn|>", "").replace("<eos>", "").strip()


def tarlai_analyze(vqa_pipe, gen_kwargs, get_weather_fn, get_treatment_fn, image_path, location="Antalya"):
    """
    Complete TarlAI pipeline: Image -> Diagnosis -> Tools -> Recommendation
    
    Args:
        vqa_pipe: Loaded Hugging Face pipeline
        gen_kwargs: Generation config
        get_weather_fn: Weather tool function
        get_treatment_fn: Treatment tool function
        image_path: Path to plant image
        location: City name (default: Antalya)
    """
    img = Image.open(image_path)
    display(img.resize((400, 300)))
    
    print(f"\n>> Location: {location}")
    print(">> Diagnosing with Gemma 4...\n")
    
    # Stage 1: Vision diagnosis
    diagnosis = diagnose_plant(vqa_pipe, gen_kwargs, img)
    
    # Stage 2: Tool execution
    weather = get_weather_fn(location)
    treatment = get_treatment_fn(diagnosis.get("disease_key", "unknown"))
    
    print(f">> Plant: {diagnosis.get('plant')}")
    print(f">> Disease: {diagnosis.get('disease')}")
    print(f">> Severity: {diagnosis.get('severity')}")
    print(f">> Weather: {weather.get('condition')}, {weather.get('temp')}C")
    print("\n>> Generating recommendation...\n")
    
    # Stage 3: Recommendation
    result = generate_recommendation(vqa_pipe, gen_kwargs, img, diagnosis, weather, treatment)
    
    print("=" * 50)
    print("TARLAI - ANALYSIS REPORT")
    print("=" * 50)
    print(result)
    print("=" * 50)


def _default_diagnosis():
    return {
        "plant": "Unknown",
        "disease": "Unknown", 
        "severity": "unknown",
        "disease_key": "unknown"
    }
