"""
Polygon Cache — Lokasyon bazlı polygon ID'lerini diskte tutar.

AgroMonitoring ücretsiz planı ayda max 10 polygon oluşturmaya izin verir.
Bu modül her lokasyon için polygon'u bir kez oluşturur ve yeniden kullanır.
"""

import json
import os
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
AGRO_API_KEY = os.getenv("AGRO_API_KEY")

AGRO_POLYGON_URL = "https://api.agromonitoring.com/agro/1.0/polygons"
GEOCODING_URL = "https://api.openweathermap.org/geo/1.0/direct"

# Proje kökünden data/polygons.json yolu
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_CACHE_DIR = _PROJECT_ROOT / "data"
_CACHE_FILE = _CACHE_DIR / "polygons.json"


def _load_cache() -> dict:
    if not _CACHE_FILE.exists():
        return {}
    try:
        with open(_CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save_cache(cache: dict) -> None:
    _CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)


def _geocode(location: str) -> dict:
    """Şehir adını lat/lon'a çevir (OpenWeather Geocoding, ücretsiz)."""
    params = {
        "q": f"{location},TR",
        "limit": 1,
        "appid": OPENWEATHER_API_KEY,
    }
    resp = requests.get(GEOCODING_URL, params=params, timeout=5)
    resp.raise_for_status()
    data = resp.json()
    if not data:
        raise ValueError(f"'{location}' için koordinat bulunamadı.")
    return {
        "lat": data[0]["lat"],
        "lon": data[0]["lon"],
        "name": data[0].get("local_names", {}).get("tr", data[0]["name"]),
    }


def _build_square_polygon(lat: float, lon: float, size_km: float = 1.0) -> list:
    """
    lat/lon merkezli, kenar uzunluğu size_km olan kapalı kare polygon.
    Alan ~= size_km² (1 km² ≈ 100 ha — Agro limitleri dahilinde).
    """
    # 1 derece enlem ≈ 111 km; boylam enlem'e göre değişir
    d_lat = (size_km / 2) / 111.0
    d_lon = (size_km / 2) / (111.0 * max(0.01, abs(_cos_deg(lat))))
    coords = [
        [lon - d_lon, lat - d_lat],
        [lon + d_lon, lat - d_lat],
        [lon + d_lon, lat + d_lat],
        [lon - d_lon, lat + d_lat],
        [lon - d_lon, lat - d_lat],  # kapat
    ]
    return coords


def _cos_deg(deg: float) -> float:
    import math
    return math.cos(math.radians(deg))


def _create_polygon(name: str, coordinates: list) -> dict:
    """Agro API'de polygon oluştur. Başarıda id/name/center/area döner."""
    body = {
        "name": name,
        "geo_json": {
            "type": "Feature",
            "properties": {},
            "geometry": {
                "type": "Polygon",
                "coordinates": [coordinates],
            },
        },
    }
    resp = requests.post(
        AGRO_POLYGON_URL,
        params={"appid": AGRO_API_KEY},
        json=body,
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def get_or_create_polygon(location: str) -> dict:
    """
    Lokasyon için polygon'u cache'den getir; yoksa oluştur ve cache'le.

    Returns:
        {"id": str, "lat": float, "lon": float, "name": str,
         "area_ha": float, "created_at": int, "cached": bool}
        Hata durumunda: {"error": str}
    """
    if not OPENWEATHER_API_KEY or OPENWEATHER_API_KEY == "YOUR_API_KEY_HERE":
        return {"error": "OPENWEATHER_API_KEY tanımlanmamış."}
    if not AGRO_API_KEY or AGRO_API_KEY == "YOUR_AGRO_KEY_HERE":
        return {"error": "AGRO_API_KEY tanımlanmamış."}

    key = location.lower().strip()
    cache = _load_cache()

    if key in cache:
        entry = dict(cache[key])
        entry["cached"] = True
        return entry

    try:
        geo = _geocode(location)
        coords = _build_square_polygon(geo["lat"], geo["lon"], size_km=1.0)
        created = _create_polygon(f"tarlai_{key}", coords)

        entry = {
            "id": created.get("id", ""),
            "lat": geo["lat"],
            "lon": geo["lon"],
            "name": geo["name"],
            "area_ha": created.get("area", 0),
            "created_at": int(time.time()),
        }
        cache[key] = entry
        _save_cache(cache)

        result = dict(entry)
        result["cached"] = False
        return result
    except (requests.RequestException, ValueError) as e:
        return {"error": f"Polygon oluşturma hatası: {e}"}


def list_cached_polygons() -> dict:
    """Diskte cache'lenmiş tüm polygon'ları döner."""
    cache = _load_cache()
    return {
        "count": len(cache),
        "polygons": cache,
    }
