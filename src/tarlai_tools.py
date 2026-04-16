"""
TarlAI Tools - Weather API, Agro API and Plant Disease Treatment Database
Used by Gemma 4 via native function calling

Public API (location-based, polygon management is internal):
    get_weather(location)          -> OWM current + air pollution + agro weather
    get_weather_forecast(location) -> 5-day / 3-hour forecast via Agro API
    get_location_report(location)  -> weather + pollution + soil + UV + NDVI (all-in-one)
    get_treatment(disease_name)    -> plant disease treatment info

Internal (called by get_location_report):
    _get_soil_data(polyid)              -> soil temperature and moisture
    _get_uv_index(polyid)               -> UV index
    _get_satellite_imagery(polyid, ...) -> satellite imagery
    _get_ndvi_history(polyid, ...)      -> NDVI history

Polygon management lives in `polygon_cache` module (automatic and transparent).
"""

import json
import os
import time
import requests
from dotenv import load_dotenv

from polygon_cache import get_or_create_polygon

# Load environment variables from .env
load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
AGRO_API_KEY = os.getenv("AGRO_API_KEY")

# ── Time constants (seconds) ────────────────────────────────────────────
SECONDS_PER_DAY = 24 * 3600
DEFAULT_SATELLITE_LOOKBACK_DAYS = 30
DEFAULT_NDVI_LOOKBACK_DAYS = 90
NDVI_REPORT_LOOKBACK_DAYS = 30

# ── Conversion factors ──────────────────────────────────────────────────
MS_TO_KMH = 3.6
KELVIN_OFFSET = 273.15

# ── HTTP timeout (seconds) ──────────────────────────────────────────────
DEFAULT_TIMEOUT = 5
LONG_TIMEOUT = 10

# ── UV index thresholds (WHO scale) ─────────────────────────────────────
UV_LOW_MAX = 2
UV_MODERATE_MAX = 5
UV_HIGH_MAX = 7
UV_VERY_HIGH_MAX = 10

# ── OpenWeatherMap API endpoints ────────────────────────────────────────
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
OPENWEATHER_POLLUTION_URL = "https://api.openweathermap.org/data/2.5/air_pollution"
GEOCODING_URL = "https://api.openweathermap.org/geo/1.0/direct"

# ── AgroMonitoring API endpoints ────────────────────────────────────────
# Free plan: current weather, forecast, soil, UVI, satellite, NDVI, polygon CRUD
AGRO_BASE_URL = "https://api.agromonitoring.com/agro/1.0"
AGRO_WEATHER_URL = f"{AGRO_BASE_URL}/weather"
AGRO_FORECAST_URL = f"{AGRO_BASE_URL}/weather/forecast"
AGRO_SOIL_URL = f"{AGRO_BASE_URL}/soil"
AGRO_UVI_URL = f"{AGRO_BASE_URL}/uvi"
AGRO_SATELLITE_URL = f"{AGRO_BASE_URL}/image/search"
AGRO_NDVI_URL = f"{AGRO_BASE_URL}/ndvi/history"
AGRO_POLYGON_URL = f"{AGRO_BASE_URL}/polygons"

# ── OWM condition code -> simplified label ──────────────────────────────
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


def _has_agro_key() -> bool:
    """Check whether a valid AgroMonitoring API key is configured."""
    return bool(AGRO_API_KEY) and AGRO_API_KEY != "YOUR_AGRO_KEY_HERE"


def _kelvin_to_celsius(kelvin: float) -> int:
    """Convert a Kelvin temperature to rounded Celsius.

    Args:
        kelvin: Temperature in Kelvin.

    Returns:
        Temperature in Celsius (rounded to nearest integer), or 0 if input is falsy.
    """
    return round(kelvin - KELVIN_OFFSET) if kelvin else 0


def _classify_uv(uvi: float) -> str:
    """Classify a UV index value into a human-readable risk level (Turkish).

    Uses WHO UV index scale thresholds.

    Args:
        uvi: UV index value (float, 0+).

    Returns:
        Turkish risk level string.
    """
    if uvi <= UV_LOW_MAX:
        return "Dusuk"
    elif uvi <= UV_MODERATE_MAX:
        return "Orta"
    elif uvi <= UV_HIGH_MAX:
        return "Yuksek"
    elif uvi <= UV_VERY_HIGH_MAX:
        return "Cok Yuksek"
    return "Asiri"


# ═══════════════════════════════════════════════════════════════════════════
#  PUBLIC API
# ═══════════════════════════════════════════════════════════════════════════


def get_weather(location: str) -> dict:
    """Fetch current weather by merging OpenWeatherMap and AgroMonitoring data.

    Three API calls are made using the same lat/lon:
      1) OWM /weather       -> core weather (Celsius, TR descriptions,
                               sunrise/sunset, visibility, 1h/3h precipitation)
      2) OWM /air_pollution -> AQI, CO, NO, NO2, O3, SO2, PM2.5, PM10, NH3
      3) Agro /weather      -> sea-level pressure, raw wind m/s, dt timestamp

    If a sub-API fails, its fields default to 0 / ""; other APIs still return.

    Args:
        location: City name, e.g. 'Antalya' or 'Istanbul'.

    Returns:
        Combined weather dict, or a dict with an 'error' key on failure.
    """
    if not OPENWEATHER_API_KEY or OPENWEATHER_API_KEY == "YOUR_API_KEY_HERE":
        return {"location": location, "error": "API key not configured. Check .env file."}

    try:
        weather_params = {
            "q": f"{location},TR",
            "appid": OPENWEATHER_API_KEY,
            "units": "metric",
            "lang": "tr",
        }
        weather_response = requests.get(
            OPENWEATHER_BASE_URL, params=weather_params, timeout=DEFAULT_TIMEOUT
        )
        weather_response.raise_for_status()
        weather_data = weather_response.json()

        # Extract top-level sections from OWM response
        main_data = weather_data.get("main", {})
        wind_data = weather_data.get("wind", {})
        weather_desc = weather_data.get("weather", [{}])[0]
        cloud_data = weather_data.get("clouds", {})
        rain_data = weather_data.get("rain", {})
        snow_data = weather_data.get("snow", {})
        sys_data = weather_data.get("sys", {})
        coord_data = weather_data.get("coord", {})

        cloud_pct = cloud_data.get("all", 0)
        raw_condition = weather_desc.get("main", "Unknown")
        condition = _CONDITION_MAP.get(raw_condition, raw_condition)

        lat = coord_data.get("lat", 0)
        lon = coord_data.get("lon", 0)

        # -- Air pollution (OWM Air Pollution API) --
        pollution_data = {}
        try:
            pollution_response = requests.get(
                OPENWEATHER_POLLUTION_URL,
                params={"lat": lat, "lon": lon, "appid": OPENWEATHER_API_KEY},
                timeout=DEFAULT_TIMEOUT,
            )
            pollution_response.raise_for_status()
            pollution_list = pollution_response.json().get("list", [{}])
            if pollution_list:
                pollution_data = pollution_list[0]
        except requests.RequestException:
            pass

        pollution_main = pollution_data.get("main", {})
        pollution_components = pollution_data.get("components", {})

        # -- Agro API supplementary metrics (sea_level, raw wind m/s, dt) --
        agro_main = {}
        agro_wind = {}
        agro_timestamp = 0
        if _has_agro_key():
            try:
                agro_response = requests.get(
                    AGRO_WEATHER_URL,
                    params={"lat": lat, "lon": lon, "appid": AGRO_API_KEY},
                    timeout=DEFAULT_TIMEOUT,
                )
                agro_response.raise_for_status()
                agro_data = agro_response.json()
                agro_main = agro_data.get("main", {})
                agro_wind = agro_data.get("wind", {})
                agro_timestamp = agro_data.get("dt", 0)
            except requests.RequestException:
                pass

        return {
            "location": location,
            "lat": lat,
            "lon": lon,
            "dt": agro_timestamp,
            # Temperature
            "temp": round(main_data.get("temp", 0)),
            "feels_like": round(main_data.get("feels_like", 0)),
            "temp_min": round(main_data.get("temp_min", 0)),
            "temp_max": round(main_data.get("temp_max", 0)),
            # Humidity & pressure
            "humidity": main_data.get("humidity", 0),
            "pressure_hpa": main_data.get("pressure", 0),
            "grnd_level_hpa": main_data.get("grnd_level", 0),
            "sea_level_hpa": agro_main.get("sea_level", 0),
            # Cloud cover
            "cloud_pct": cloud_pct,
            # Wind (both km/h and raw m/s)
            "wind_kmh": round(wind_data.get("speed", 0) * MS_TO_KMH),
            "wind_speed_ms": agro_wind.get("speed", wind_data.get("speed", 0)),
            "wind_deg": wind_data.get("deg", 0),
            "wind_gust_kmh": round(wind_data.get("gust", 0) * MS_TO_KMH),
            "wind_gust_ms": agro_wind.get("gust", wind_data.get("gust", 0)),
            # Precipitation / Snow
            "rain_1h_mm": rain_data.get("1h", 0),
            "rain_3h_mm": rain_data.get("3h", 0),
            "snow_1h_mm": snow_data.get("1h", 0),
            "snow_3h_mm": snow_data.get("3h", 0),
            # Visibility
            "visibility_m": weather_data.get("visibility", 10000),
            # Sunrise / Sunset
            "sunrise": sys_data.get("sunrise", 0),
            "sunset": sys_data.get("sunset", 0),
            # Condition
            "condition": condition,
            "description": weather_desc.get("description", ""),
            # Air quality
            "air_quality_index": pollution_main.get("aqi", 0),
            "co": pollution_components.get("co", 0),
            "no": pollution_components.get("no", 0),
            "no2": pollution_components.get("no2", 0),
            "o3": pollution_components.get("o3", 0),
            "so2": pollution_components.get("so2", 0),
            "pm2_5": pollution_components.get("pm2_5", 0),
            "pm10": pollution_components.get("pm10", 0),
            "nh3": pollution_components.get("nh3", 0),
        }
    except requests.RequestException as e:
        return {"location": location, "error": f"API error: {e}"}


# ═══════════════════════════════════════════════════════════════════════════
#  AGRO API FUNCTIONS (agromonitoring.com — Free Plan)
# ═══════════════════════════════════════════════════════════════════════════


def _geocode(location: str) -> dict:
    """Convert a city name to lat/lon coordinates via OpenWeather Geocoding API.

    Args:
        location: City name, e.g. 'Antalya', 'Istanbul'.

    Returns:
        Dict with 'lat', 'lon', 'name' keys on success,
        or a dict with an 'error' key on failure.
    """
    if not OPENWEATHER_API_KEY or OPENWEATHER_API_KEY == "YOUR_API_KEY_HERE":
        return {"error": "API key not configured."}
    try:
        geocode_params = {
            "q": f"{location},TR",
            "limit": 1,
            "appid": OPENWEATHER_API_KEY,
        }
        geocode_response = requests.get(
            GEOCODING_URL, params=geocode_params, timeout=DEFAULT_TIMEOUT
        )
        geocode_response.raise_for_status()
        results = geocode_response.json()
        if not results:
            return {"error": f"No coordinates found for '{location}'."}
        local_name = results[0].get("local_names", {}).get("tr", results[0]["name"])
        return {"lat": results[0]["lat"], "lon": results[0]["lon"], "name": local_name}
    except requests.RequestException as e:
        return {"error": f"Geocoding error: {e}"}


def get_weather_forecast(location: str) -> dict:
    """Fetch 5-day / 3-hour weather forecast via Agro API (free tier).

    Agro API returns temperatures in Kelvin; this function converts them to Celsius.

    Args:
        location: City name, e.g. 'Antalya'.

    Returns:
        Dict with 'forecasts' list (each entry is a 3-hour period),
        or a dict with an 'error' key on failure.
    """
    if not _has_agro_key():
        return {"location": location, "error": "AGRO_API_KEY not configured."}

    geo = _geocode(location)
    if "error" in geo:
        return {"location": location, "error": geo["error"]}

    try:
        forecast_params = {
            "lat": geo["lat"],
            "lon": geo["lon"],
            "appid": AGRO_API_KEY,
        }
        forecast_response = requests.get(
            AGRO_FORECAST_URL, params=forecast_params, timeout=LONG_TIMEOUT
        )
        forecast_response.raise_for_status()
        raw_forecast = forecast_response.json()

        forecasts = []
        for period in raw_forecast if isinstance(raw_forecast, list) else []:
            period_main = period.get("main", {})
            period_wind = period.get("wind", {})
            period_weather = period.get("weather", [{}])[0]
            period_clouds = period.get("clouds", {})
            period_rain = period.get("rain", {})

            raw_condition = period_weather.get("main", "Unknown")
            condition = _CONDITION_MAP.get(raw_condition, raw_condition)

            forecasts.append({
                "dt": period.get("dt", 0),
                "temp": _kelvin_to_celsius(period_main.get("temp", 0)),
                "feels_like": _kelvin_to_celsius(period_main.get("feels_like", 0)),
                "temp_min": _kelvin_to_celsius(period_main.get("temp_min", 0)),
                "temp_max": _kelvin_to_celsius(period_main.get("temp_max", 0)),
                "humidity": period_main.get("humidity", 0),
                "pressure_hpa": period_main.get("pressure", 0),
                "wind_kmh": round(period_wind.get("speed", 0) * MS_TO_KMH),
                "wind_deg": period_wind.get("deg", 0),
                "cloud_pct": period_clouds.get("all", 0),
                "rain_3h_mm": period_rain.get("3h", 0),
                "condition": condition,
                "description": period_weather.get("description", ""),
            })

        return {
            "source": "agro_api",
            "location": geo["name"],
            "lat": geo["lat"],
            "lon": geo["lon"],
            "count": len(forecasts),
            "forecasts": forecasts,
        }
    except requests.RequestException as e:
        return {"location": location, "error": f"Agro Forecast API error: {e}"}


def _get_soil_data(polyid: str) -> dict:
    """Fetch current soil data from Agro API (free tier).

    Returns soil surface temperature, 10 cm depth temperature, and moisture.
    Updated twice per day by the API.

    Args:
        polyid: Polygon ID (created via polygon_cache).

    Returns:
        Soil data dict with temperatures in both Celsius and Kelvin,
        or a dict with an 'error' key on failure.
    """
    if not _has_agro_key():
        return {"error": "AGRO_API_KEY not configured."}

    try:
        soil_params = {
            "polyid": polyid,
            "appid": AGRO_API_KEY,
        }
        soil_response = requests.get(
            AGRO_SOIL_URL, params=soil_params, timeout=DEFAULT_TIMEOUT
        )
        soil_response.raise_for_status()
        soil_data = soil_response.json()

        surface_temp_k = soil_data.get("t0", 0)
        depth_temp_k = soil_data.get("t10", 0)

        return {
            "source": "agro_api",
            "polyid": polyid,
            "dt": soil_data.get("dt", 0),
            "surface_temp_c": round(surface_temp_k - KELVIN_OFFSET, 1) if surface_temp_k else 0,
            "depth_10cm_temp_c": round(depth_temp_k - KELVIN_OFFSET, 1) if depth_temp_k else 0,
            "moisture": soil_data.get("moisture", 0),
            "surface_temp_k": surface_temp_k,
            "depth_10cm_temp_k": depth_temp_k,
        }
    except requests.RequestException as e:
        return {"polyid": polyid, "error": f"Agro Soil API error: {e}"}


def _get_uv_index(polyid: str) -> dict:
    """Fetch current UV index from Agro API (free tier).

    Used for plant stress assessment and field-work scheduling.

    Args:
        polyid: Polygon ID.

    Returns:
        Dict with 'uvi' (float) and 'uv_level' (Turkish risk label),
        or a dict with an 'error' key on failure.
    """
    if not _has_agro_key():
        return {"error": "AGRO_API_KEY not configured."}

    try:
        uv_params = {
            "polyid": polyid,
            "appid": AGRO_API_KEY,
        }
        uv_response = requests.get(
            AGRO_UVI_URL, params=uv_params, timeout=DEFAULT_TIMEOUT
        )
        uv_response.raise_for_status()
        uv_data = uv_response.json()

        uvi_value = uv_data.get("uvi", 0)

        return {
            "source": "agro_api",
            "polyid": polyid,
            "dt": uv_data.get("dt", 0),
            "uvi": uvi_value,
            "uv_level": _classify_uv(uvi_value),
        }
    except requests.RequestException as e:
        return {"polyid": polyid, "error": f"Agro UVI API error: {e}"}


def _get_satellite_imagery(polyid: str, start: int = None, end: int = None) -> dict:
    """Search satellite imagery via Agro API (NDVI, EVI, True/False Color).

    Free tier provides Sentinel-2 and Landsat 8 data.

    Args:
        polyid: Polygon ID.
        start:  Start date (unix timestamp). Defaults to DEFAULT_SATELLITE_LOOKBACK_DAYS ago.
        end:    End date (unix timestamp). Defaults to now.

    Returns:
        Dict with 'images' list containing URLs and metadata,
        or a dict with an 'error' key on failure.
    """
    if not _has_agro_key():
        return {"error": "AGRO_API_KEY not configured."}

    now = int(time.time())
    if end is None:
        end = now
    if start is None:
        start = now - (DEFAULT_SATELLITE_LOOKBACK_DAYS * SECONDS_PER_DAY)

    try:
        satellite_params = {
            "polyid": polyid,
            "start": start,
            "end": end,
            "appid": AGRO_API_KEY,
        }
        satellite_response = requests.get(
            AGRO_SATELLITE_URL, params=satellite_params, timeout=LONG_TIMEOUT
        )
        satellite_response.raise_for_status()
        raw_images = satellite_response.json()

        images = []
        for image_entry in raw_images if isinstance(raw_images, list) else []:
            images.append({
                "dt": image_entry.get("dt", 0),
                "type": image_entry.get("type", ""),
                "coverage_pct": image_entry.get("dc", 0),
                "cloud_pct": image_entry.get("cl", 0),
                "sun": image_entry.get("sun", {}),
                "image_urls": image_entry.get("image", {}),
                "tile_urls": image_entry.get("tile", {}),
                "stats_urls": image_entry.get("stats", {}),
                "data_urls": image_entry.get("data", {}),
            })

        return {
            "source": "agro_api",
            "polyid": polyid,
            "start": start,
            "end": end,
            "count": len(images),
            "images": images,
        }
    except requests.RequestException as e:
        return {"polyid": polyid, "error": f"Agro Satellite API error: {e}"}


def _get_ndvi_history(polyid: str, start: int = None, end: int = None) -> dict:
    """Fetch NDVI history from Agro API (free tier).

    NDVI (Normalized Difference Vegetation Index) ranges from -1 to 1.
    Values above 0.6 indicate healthy vegetation.

    Args:
        polyid: Polygon ID.
        start:  Start date (unix timestamp). Defaults to DEFAULT_NDVI_LOOKBACK_DAYS ago.
        end:    End date (unix timestamp). Defaults to now.

    Returns:
        Dict with 'history' list of daily NDVI statistics,
        or a dict with an 'error' key on failure.
    """
    if not _has_agro_key():
        return {"error": "AGRO_API_KEY not configured."}

    now = int(time.time())
    if end is None:
        end = now
    if start is None:
        start = now - (DEFAULT_NDVI_LOOKBACK_DAYS * SECONDS_PER_DAY)

    try:
        ndvi_params = {
            "polyid": polyid,
            "start": start,
            "end": end,
            "appid": AGRO_API_KEY,
        }
        ndvi_response = requests.get(
            AGRO_NDVI_URL, params=ndvi_params, timeout=LONG_TIMEOUT
        )
        ndvi_response.raise_for_status()
        raw_ndvi = ndvi_response.json()

        entries = []
        for ndvi_entry in raw_ndvi if isinstance(raw_ndvi, list) else []:
            ndvi_stats = ndvi_entry.get("data", {})
            entries.append({
                "dt": ndvi_entry.get("dt", 0),
                "source": ndvi_entry.get("source", ""),
                "coverage_pct": ndvi_entry.get("dc", 0),
                "cloud_pct": ndvi_entry.get("cl", 0),
                "ndvi_mean": ndvi_stats.get("mean", 0),
                "ndvi_median": ndvi_stats.get("median", 0),
                "ndvi_min": ndvi_stats.get("min", 0),
                "ndvi_max": ndvi_stats.get("max", 0),
                "ndvi_std": ndvi_stats.get("std", 0),
                "ndvi_p25": ndvi_stats.get("p25", 0),
                "ndvi_p75": ndvi_stats.get("p75", 0),
            })

        return {
            "source": "agro_api",
            "polyid": polyid,
            "start": start,
            "end": end,
            "count": len(entries),
            "history": entries,
        }
    except requests.RequestException as e:
        return {"polyid": polyid, "error": f"Agro NDVI API error: {e}"}


# ═══════════════════════════════════════════════════════════════════════════
#  COMBINED LOCATION REPORT
# ═══════════════════════════════════════════════════════════════════════════


def get_location_report(location: str) -> dict:
    """Generate a comprehensive agricultural report for a location.

    Combines weather, air pollution, soil, UV, and latest NDVI data in a single call.
    On first invocation for a location, a polygon is created and cached to disk;
    subsequent calls reuse the cached polygon (via polygon_cache module).

    Note: NDVI/satellite data for a newly created polygon may take ~24 hours
    to populate. ndvi_latest may be None on the first call — this is expected.

    Args:
        location: City name, e.g. 'Antalya'.

    Returns:
        Combined report dict with keys: weather, polygon, soil, uv, ndvi_latest, errors.
    """
    report = {
        "location": location,
        "weather": None,
        "polygon": None,
        "soil": None,
        "uv": None,
        "ndvi_latest": None,
        "errors": [],
    }

    # 1) Weather (OWM + pollution + agro weather)
    weather = get_weather(location)
    report["weather"] = weather
    if "error" in weather:
        report["errors"].append({"weather": weather["error"]})

    # 2) Polygon (load from cache or create)
    polygon = get_or_create_polygon(location)
    if "error" in polygon:
        report["errors"].append({"polygon": polygon["error"]})
        report["polygon"] = polygon
        return report

    report["polygon"] = polygon
    polygon_id = polygon["id"]

    # 3) Soil data
    soil = _get_soil_data(polygon_id)
    report["soil"] = soil
    if "error" in soil:
        report["errors"].append({"soil": soil["error"]})

    # 4) UV index
    uv = _get_uv_index(polygon_id)
    report["uv"] = uv
    if "error" in uv:
        report["errors"].append({"uv": uv["error"]})

    # 5) NDVI history — last NDVI_REPORT_LOOKBACK_DAYS, pick most recent entry
    now = int(time.time())
    ndvi_start = now - (NDVI_REPORT_LOOKBACK_DAYS * SECONDS_PER_DAY)
    ndvi = _get_ndvi_history(polygon_id, start=ndvi_start, end=now)
    if "error" in ndvi:
        report["errors"].append({"ndvi": ndvi["error"]})
    else:
        history = ndvi.get("history", [])
        if history:
            latest_entry = max(history, key=lambda entry: entry.get("dt", 0))
            report["ndvi_latest"] = {
                "dt": latest_entry.get("dt", 0),
                "ndvi_mean": latest_entry.get("ndvi_mean", 0),
                "ndvi_median": latest_entry.get("ndvi_median", 0),
                "ndvi_max": latest_entry.get("ndvi_max", 0),
                "source": latest_entry.get("source", ""),
            }
        else:
            report["ndvi_latest"] = None
            if not polygon.get("cached", True):
                report["note"] = "NDVI data for a new polygon takes ~24 hours to populate."

    return report


# ═══════════════════════════════════════════════════════════════════════════
#  PLANT DISEASE TREATMENT DATABASE
# ═══════════════════════════════════════════════════════════════════════════

# Treatment database — static lookup for common plant diseases
_TREATMENT_DB = {
    "leaf_spot": {
        "name": "Leaf Spot (Yaprak Lekesi)",
        "chemical": "Copper-based fungicide, Mancozeb",
        "organic": "Bordeaux mixture, Neem oil",
        "interval": "7-14 days",
        "notes": "Avoid overhead watering",
    },
    "early_blight": {
        "name": "Early Blight (Erken Yaniklik)",
        "chemical": "Mancozeb, Chlorothalonil",
        "organic": "Neem oil, copper sulfate solution",
        "interval": "7-10 days",
        "notes": "Apply early morning or late evening",
    },
    "late_blight": {
        "name": "Late Blight (Gec Yaniklik)",
        "chemical": "Metalaxyl, Bordeaux mixture",
        "organic": "Bordeaux mixture (copper based)",
        "interval": "5-7 days",
        "notes": "Remove infected leaves immediately",
    },
    "powdery_mildew": {
        "name": "Powdery Mildew (Kulleme)",
        "chemical": "Sulfur-based fungicide",
        "organic": "Milk-water mix (40% milk)",
        "interval": "7 days",
        "notes": "Improve air circulation between plants",
    },
    "downy_mildew": {
        "name": "Downy Mildew (Mildiyou)",
        "chemical": "Metalaxyl, Fosetyl-Al",
        "organic": "Copper hydroxide",
        "interval": "7-10 days",
        "notes": "Ensure good drainage",
    },
    "rust": {
        "name": "Rust (Pas Hastaligi)",
        "chemical": "Triadimefon, Propiconazole",
        "organic": "Sulfur dust, Neem oil",
        "interval": "7-14 days",
        "notes": "Remove infected plant debris",
    },
    "anthracnose": {
        "name": "Anthracnose (Antrakoz)",
        "chemical": "Chlorothalonil, Copper fungicide",
        "organic": "Bordeaux mixture",
        "interval": "7-10 days",
        "notes": "Avoid working with wet plants",
    },
    "bacterial_spot": {
        "name": "Bacterial Spot (Bakteriyel Leke)",
        "chemical": "Copper-based bactericide",
        "organic": "Copper hydroxide spray",
        "interval": "5-7 days",
        "notes": "No cure once established, focus on prevention",
    },
    "mosaic_virus": {
        "name": "Mosaic Virus (Mozaik Virusu)",
        "chemical": "No chemical treatment available",
        "organic": "Remove and destroy infected plants",
        "interval": "N/A",
        "notes": "Control aphid vectors, use resistant varieties",
    },
    "root_rot": {
        "name": "Root Rot (Kok Curumesi)",
        "chemical": "Metalaxyl soil drench",
        "organic": "Improve drainage, reduce watering",
        "interval": "14-21 days",
        "notes": "Avoid waterlogged conditions",
    },
}


def get_treatment(disease_name: str) -> dict:
    """Look up treatment information for a plant disease.

    Performs fuzzy matching: the query and database keys are compared
    with substring matching in both directions.

    Args:
        disease_name: Disease identifier, e.g. 'early_blight', 'powdery_mildew'.

    Returns:
        Dict with 'name', 'chemical', 'organic', 'interval', 'notes' keys.
        Returns a fallback entry if the disease is not found in the database.
    """
    normalized_key = disease_name.lower().replace(" ", "_").strip()
    for disease_id, treatment_info in _TREATMENT_DB.items():
        if disease_id in normalized_key or normalized_key in disease_id:
            return treatment_info
    return {
        "name": disease_name,
        "chemical": "Consult local agricultural office",
        "organic": "N/A",
        "interval": "N/A",
        "notes": "Disease not found in database",
    }


# ═══════════════════════════════════════════════════════════════════════════
#  MANUAL TEST
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("TarlAI Tools - Test")
    print("=" * 60)

    # 1. All-in-one location report (weather + pollution + soil + UV + NDVI)
    print("\n-- [1] Location Report (Antalya) --")
    location_report = get_location_report("Antalya")
    print(json.dumps(location_report, indent=2, ensure_ascii=False))

    # 2. 5-day forecast (first 2 periods)
    print("\n-- [2] Forecast (first 2 periods) --")
    forecast_result = get_weather_forecast("Antalya")
    if "error" not in forecast_result:
        forecast_result["forecasts"] = forecast_result.get("forecasts", [])[:2]
    print(json.dumps(forecast_result, indent=2, ensure_ascii=False))

    # 3. Treatment lookup
    print("\n-- [3] Treatment --")
    print(json.dumps(get_treatment("leaf_spot"), indent=2, ensure_ascii=False))
