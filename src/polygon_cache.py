"""
Polygon Cache — Persists location-based polygon IDs to disk.

AgroMonitoring free plan allows a maximum of 10 polygon creations per month.
This module creates each polygon once and reuses it via a local JSON cache.
"""

import json
import math
import os
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
AGRO_API_KEY = os.getenv("AGRO_API_KEY")

# ── API endpoints ───────────────────────────────────────────────────────
AGRO_POLYGON_URL = "https://api.agromonitoring.com/agro/1.0/polygons"
GEOCODING_URL = "https://api.openweathermap.org/geo/1.0/direct"

# ── Cache file paths ────────────────────────────────────────────────────
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_CACHE_DIR = _PROJECT_ROOT / "data"
_CACHE_FILE = _CACHE_DIR / "polygons.json"

# ── Geographic constants ────────────────────────────────────────────────
KM_PER_DEGREE_LAT = 111.0          # 1 degree of latitude ≈ 111 km
DEFAULT_POLYGON_SIZE_KM = 1.0      # Side length of the square polygon (km)
MIN_COS_CLAMP = 0.01               # Minimum cosine clamp to avoid division by zero at poles

# ── HTTP timeouts (seconds) ─────────────────────────────────────────────
GEOCODE_TIMEOUT = 5
POLYGON_CREATE_TIMEOUT = 10


def _load_cache() -> dict:
    """Load the polygon cache from disk.

    Returns:
        Dict mapping location keys to polygon entries,
        or an empty dict if the cache file is missing or corrupt.
    """
    if not _CACHE_FILE.exists():
        return {}
    try:
        with open(_CACHE_FILE, "r", encoding="utf-8") as cache_file:
            return json.load(cache_file)
    except (json.JSONDecodeError, OSError):
        return {}


def _save_cache(cache: dict) -> None:
    """Write the polygon cache to disk, creating directories if needed.

    Args:
        cache: Dict mapping location keys to polygon entries.
    """
    _CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CACHE_FILE, "w", encoding="utf-8") as cache_file:
        json.dump(cache, f=cache_file, indent=2, ensure_ascii=False)


def _geocode(location: str) -> dict:
    """Convert a city name to lat/lon coordinates via OpenWeather Geocoding API.

    Args:
        location: City name, e.g. 'Antalya', 'Istanbul'.

    Returns:
        Dict with 'lat', 'lon', 'name' keys.

    Raises:
        ValueError: If no coordinates are found for the given location.
        requests.RequestException: On network or HTTP errors.
    """
    geocode_params = {
        "q": f"{location},TR",
        "limit": 1,
        "appid": OPENWEATHER_API_KEY,
    }
    geocode_response = requests.get(
        GEOCODING_URL, params=geocode_params, timeout=GEOCODE_TIMEOUT
    )
    geocode_response.raise_for_status()
    results = geocode_response.json()
    if not results:
        raise ValueError(f"No coordinates found for '{location}'.")
    local_name = results[0].get("local_names", {}).get("tr", results[0]["name"])
    return {
        "lat": results[0]["lat"],
        "lon": results[0]["lon"],
        "name": local_name,
    }


def _cos_deg(degrees: float) -> float:
    """Compute cosine of an angle given in degrees.

    Args:
        degrees: Angle in degrees.

    Returns:
        Cosine value.
    """
    return math.cos(math.radians(degrees))


def _build_square_polygon(lat: float, lon: float, side_km: float = DEFAULT_POLYGON_SIZE_KM) -> list:
    """Build a closed square polygon centered on lat/lon.

    The polygon area ≈ side_km² (1 km² ≈ 100 ha, within Agro free tier limits).
    Longitude offset is adjusted for latitude to maintain a true square shape.

    Args:
        lat:     Center latitude (degrees).
        lon:     Center longitude (degrees).
        side_km: Side length of the square (km). Defaults to DEFAULT_POLYGON_SIZE_KM.

    Returns:
        List of [lon, lat] coordinate pairs forming a closed GeoJSON ring.
    """
    half_side_km = side_km / 2

    # 1 degree latitude ≈ KM_PER_DEGREE_LAT km (constant worldwide)
    delta_lat = half_side_km / KM_PER_DEGREE_LAT

    # Longitude degrees per km vary with latitude
    cos_lat = max(MIN_COS_CLAMP, abs(_cos_deg(lat)))
    delta_lon = half_side_km / (KM_PER_DEGREE_LAT * cos_lat)

    coordinates = [
        [lon - delta_lon, lat - delta_lat],   # bottom-left
        [lon + delta_lon, lat - delta_lat],   # bottom-right
        [lon + delta_lon, lat + delta_lat],   # top-right
        [lon - delta_lon, lat + delta_lat],   # top-left
        [lon - delta_lon, lat - delta_lat],   # close the ring
    ]
    return coordinates


def _create_polygon(polygon_name: str, coordinates: list) -> dict:
    """Create a polygon on AgroMonitoring API.

    Args:
        polygon_name: Human-readable name for the polygon (e.g. 'tarlai_antalya').
        coordinates:  List of [lon, lat] pairs forming a closed GeoJSON ring.

    Returns:
        API response dict containing 'id', 'name', 'center', 'area' etc.

    Raises:
        requests.RequestException: On network or HTTP errors.
    """
    request_body = {
        "name": polygon_name,
        "geo_json": {
            "type": "Feature",
            "properties": {},
            "geometry": {
                "type": "Polygon",
                "coordinates": [coordinates],
            },
        },
    }
    create_response = requests.post(
        AGRO_POLYGON_URL,
        params={"appid": AGRO_API_KEY},
        json=request_body,
        timeout=POLYGON_CREATE_TIMEOUT,
    )
    create_response.raise_for_status()
    return create_response.json()


def get_or_create_polygon(location: str) -> dict:
    """Retrieve a polygon from cache, or create and cache a new one.

    On first call for a given location, geocodes the city, builds a 1 km²
    square polygon via the Agro API, and saves it to disk. Subsequent calls
    return the cached entry without any API calls.

    Args:
        location: City name, e.g. 'Antalya'.

    Returns:
        Dict with keys: 'id', 'lat', 'lon', 'name', 'area_ha', 'created_at', 'cached'.
        On failure, returns a dict with an 'error' key instead.
    """
    if not OPENWEATHER_API_KEY or OPENWEATHER_API_KEY == "YOUR_API_KEY_HERE":
        return {"error": "OPENWEATHER_API_KEY not configured."}
    if not AGRO_API_KEY or AGRO_API_KEY == "YOUR_AGRO_KEY_HERE":
        return {"error": "AGRO_API_KEY not configured."}

    location_key = location.lower().strip()
    cache = _load_cache()

    # Return cached entry if available
    if location_key in cache:
        cached_entry = dict(cache[location_key])
        cached_entry["cached"] = True
        return cached_entry

    # Create new polygon: geocode -> build square -> call Agro API -> cache
    try:
        geo = _geocode(location)
        coordinates = _build_square_polygon(geo["lat"], geo["lon"])
        created_polygon = _create_polygon(f"tarlai_{location_key}", coordinates)

        polygon_entry = {
            "id": created_polygon.get("id", ""),
            "lat": geo["lat"],
            "lon": geo["lon"],
            "name": geo["name"],
            "area_ha": created_polygon.get("area", 0),
            "created_at": int(time.time()),
        }
        cache[location_key] = polygon_entry
        _save_cache(cache)

        result = dict(polygon_entry)
        result["cached"] = False
        return result
    except (requests.RequestException, ValueError) as e:
        return {"error": f"Polygon creation error: {e}"}


def list_cached_polygons() -> dict:
    """List all polygons currently stored in the disk cache.

    Returns:
        Dict with 'count' (int) and 'polygons' (dict of location -> entry).
    """
    cache = _load_cache()
    return {
        "count": len(cache),
        "polygons": cache,
    }
