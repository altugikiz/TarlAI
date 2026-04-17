"""
TarlAI Agro API — AgroMonitoring sensor and location report functions.

Internal functions (called by get_location_report):
    _get_soil_data(polyid)              -> soil temperature and moisture
    _get_uv_index(polyid)               -> UV index
    _get_satellite_imagery(polyid, ...) -> satellite imagery
    _get_ndvi_history(polyid, ...)      -> NDVI history

Public API:
    get_location_report(location) -> weather + pollution + soil + UV + NDVI (all-in-one)
"""

import os
import time
import requests
from dotenv import load_dotenv

from polygon_cache import get_or_create_polygon
from weather_api import get_weather, _has_agro_key, _classify_uv, KELVIN_OFFSET, DEFAULT_TIMEOUT, LONG_TIMEOUT

load_dotenv()

AGRO_API_KEY = os.getenv("AGRO_API_KEY")

# ── Time constants (seconds) ─────────────────────────────────────────────────
SECONDS_PER_DAY = 24 * 3600
DEFAULT_SATELLITE_LOOKBACK_DAYS = 30
DEFAULT_NDVI_LOOKBACK_DAYS = 90
NDVI_REPORT_LOOKBACK_DAYS = 30

# ── AgroMonitoring sensor endpoints ──────────────────────────────────────────
AGRO_BASE_URL = "https://api.agromonitoring.com/agro/1.0"
AGRO_SOIL_URL = f"{AGRO_BASE_URL}/soil"
AGRO_UVI_URL = f"{AGRO_BASE_URL}/uvi"
AGRO_SATELLITE_URL = f"{AGRO_BASE_URL}/image/search"
AGRO_NDVI_URL = f"{AGRO_BASE_URL}/ndvi/history"


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
