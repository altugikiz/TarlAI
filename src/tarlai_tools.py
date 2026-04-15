"""
TarlAI Tools - Weather API, Agro API and Plant Disease Treatment Database
Used by Gemma 4 via native function calling

Public API (lokasyon bazlı, polyid yönetimi dahili):
    get_weather(location)          → OWM + pollution + agro weather
    get_weather_forecast(location) → 5 gün / 3 saatlik tahmin
    get_location_report(location)  → hava + kirlilik + toprak + UV + NDVI (hepsi tek çağrıda)
    get_treatment(disease_name)    → bitki hastalığı tedavi bilgisi

Polygon yönetimi `polygon_cache` modülünde, otomatik ve şeffaf.
"""

import json
import os
import time
import requests
from dotenv import load_dotenv

from polygon_cache import get_or_create_polygon

# .env dosyasını yükle
load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
AGRO_API_KEY = os.getenv("AGRO_API_KEY")


def _has_agro_key() -> bool:
    return bool(AGRO_API_KEY) and AGRO_API_KEY != "YOUR_AGRO_KEY_HERE"

# ── Standart OpenWeatherMap API URL'leri ──────────────────────────────────
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
OPENWEATHER_POLLUTION_URL = "https://api.openweathermap.org/data/2.5/air_pollution"
GEOCODING_URL = "https://api.openweathermap.org/geo/1.0/direct"

# ── Agro API (AgroMonitoring) URL'leri ────────────────────────────────────
# Aynı OpenWeather API key'ini kullanır, ayrı key gerekmez.
# Ücretsiz plan: current weather, forecast, current soil, current UVI,
#                satellite imagery, NDVI history, polygon CRUD
AGRO_BASE_URL = "https://api.agromonitoring.com/agro/1.0"
AGRO_WEATHER_URL = f"{AGRO_BASE_URL}/weather"
AGRO_FORECAST_URL = f"{AGRO_BASE_URL}/weather/forecast"
AGRO_SOIL_URL = f"{AGRO_BASE_URL}/soil"
AGRO_UVI_URL = f"{AGRO_BASE_URL}/uvi"
AGRO_SATELLITE_URL = f"{AGRO_BASE_URL}/image/search"
AGRO_NDVI_URL = f"{AGRO_BASE_URL}/ndvi/history"
AGRO_POLYGON_URL = f"{AGRO_BASE_URL}/polygons"

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
    Get current weather for a given location by merging OpenWeatherMap
    (standart hava + hava kirliliği) ve AgroMonitoring (agro ek metrikleri)
    sonuçlarını tek bir sözlükte birleştirir.

    Üç API çağrısı yapılır (aynı lat/lon ile):
      1) OWM /weather          → ana hava verisi (Celsius, TR açıklama,
                                 sunrise/sunset, visibility, 1h/3h yağış)
      2) OWM /air_pollution    → AQI, CO, NO, NO2, O3, SO2, PM2.5, PM10, NH3
      3) Agro /weather         → sea_level basıncı, ham wind m/s, dt timestamp

    Args:
        location: Şehir adı, ör. 'Antalya' veya 'Istanbul'
    Returns:
        Birleşik hava durumu sözlüğü. Bir API başarısız olursa o alanlar
        varsayılan (0 / "") değerlerle döner; diğer API'ler yine çalışır.
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
        rain = data.get("rain", {})
        snow = data.get("snow", {})
        sys_info = data.get("sys", {})
        coord = data.get("coord", {})

        cloud_pct = clouds.get("all", 0)
        main_condition = weather_info.get("main", "Unknown")
        condition = _CONDITION_MAP.get(main_condition, main_condition)

        lat = coord.get("lat", 0)
        lon = coord.get("lon", 0)

        # ── Hava kirliliği (OWM Air Pollution) ──
        air_quality = {}
        try:
            poll_resp = requests.get(
                OPENWEATHER_POLLUTION_URL,
                params={"lat": lat, "lon": lon, "appid": OPENWEATHER_API_KEY},
                timeout=5,
            )
            poll_resp.raise_for_status()
            poll_list = poll_resp.json().get("list", [{}])
            if poll_list:
                air_quality = poll_list[0]
        except requests.RequestException:
            pass

        poll_main = air_quality.get("main", {})
        poll_comp = air_quality.get("components", {})

        # ── Agro API ek metrikleri (sea_level, ham wind m/s, dt) ──
        agro_main = {}
        agro_wind = {}
        agro_dt = 0
        if _has_agro_key():
            try:
                agro_resp = requests.get(
                    AGRO_WEATHER_URL,
                    params={"lat": lat, "lon": lon, "appid": AGRO_API_KEY},
                    timeout=5,
                )
                agro_resp.raise_for_status()
                agro_data = agro_resp.json()
                agro_main = agro_data.get("main", {})
                agro_wind = agro_data.get("wind", {})
                agro_dt = agro_data.get("dt", 0)
            except requests.RequestException:
                pass

        return {
            "location": location,
            "lat": lat,
            "lon": lon,
            "dt": agro_dt,                                     # Agro'dan: gözlem zaman damgası (Unix)
            # Sıcaklık
            "temp": round(main.get("temp", 0)),
            "feels_like": round(main.get("feels_like", 0)),
            "temp_min": round(main.get("temp_min", 0)),
            "temp_max": round(main.get("temp_max", 0)),
            # Nem ve basınç
            "humidity": main.get("humidity", 0),
            "pressure_hpa": main.get("pressure", 0),
            "grnd_level_hpa": main.get("grnd_level", 0),
            "sea_level_hpa": agro_main.get("sea_level", 0),    # Agro'dan: deniz seviyesi basıncı
            # Bulutluluk
            "cloud_pct": cloud_pct,
            # Rüzgar (hem km/h hem ham m/s)
            "wind_kmh": round(wind.get("speed", 0) * 3.6),
            "wind_speed_ms": agro_wind.get("speed", wind.get("speed", 0)),  # Agro'dan ham m/s (yoksa OWM)
            "wind_deg": wind.get("deg", 0),
            "wind_gust_kmh": round(wind.get("gust", 0) * 3.6),
            "wind_gust_ms": agro_wind.get("gust", wind.get("gust", 0)),     # Agro'dan ham m/s
            # Yağış / Kar
            "rain_1h_mm": rain.get("1h", 0),
            "rain_3h_mm": rain.get("3h", 0),
            "snow_1h_mm": snow.get("1h", 0),
            "snow_3h_mm": snow.get("3h", 0),
            # Görüş mesafesi
            "visibility_m": data.get("visibility", 10000),
            # Gün doğumu / batımı
            "sunrise": sys_info.get("sunrise", 0),
            "sunset": sys_info.get("sunset", 0),
            # Durum
            "condition": condition,
            "description": weather_info.get("description", ""),
            # Hava kirliliği
            "air_quality_index": poll_main.get("aqi", 0),
            "co": poll_comp.get("co", 0),
            "no": poll_comp.get("no", 0),
            "no2": poll_comp.get("no2", 0),
            "o3": poll_comp.get("o3", 0),
            "so2": poll_comp.get("so2", 0),
            "pm2_5": poll_comp.get("pm2_5", 0),
            "pm10": poll_comp.get("pm10", 0),
            "nh3": poll_comp.get("nh3", 0),
        }
    except requests.RequestException as e:
        return {"location": location, "error": f"API hatası: {e}"}


# ══════════════════════════════════════════════════════════════════════════
#  AGRO API FONKSİYONLARI  (agromonitoring.com  — Ücretsiz Plan)
# ══════════════════════════════════════════════════════════════════════════

def _geocode(location: str) -> dict:
    """
    Şehir adını lat/lon koordinatlarına çevir (OpenWeather Geocoding API — ücretsiz).

    Args:
        location: Şehir adı, ör. 'Antalya', 'Istanbul'
    Returns:
        {"lat": float, "lon": float, "name": str} veya hata durumunda {"error": str}
    """
    if not OPENWEATHER_API_KEY or OPENWEATHER_API_KEY == "YOUR_API_KEY_HERE":
        return {"error": "API key tanımlanmamış."}
    try:
        params = {
            "q": f"{location},TR",
            "limit": 1,
            "appid": OPENWEATHER_API_KEY,
        }
        resp = requests.get(GEOCODING_URL, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        if not data:
            return {"error": f"'{location}' için koordinat bulunamadı."}
        return {"lat": data[0]["lat"], "lon": data[0]["lon"], "name": data[0].get("local_names", {}).get("tr", data[0]["name"])}
    except requests.RequestException as e:
        return {"error": f"Geocoding hatası: {e}"}


def get_weather_forecast(location: str) -> dict:
    """
    Agro API üzerinden 5 günlük / 3 saatlik hava tahmini al (ücretsiz).

    Args:
        location: Şehir adı, ör. 'Antalya'
    Returns:
        Forecast listesi (her biri 3 saatlik periyot)
    """
    if not _has_agro_key():
        return {"location": location, "error": "AGRO_API_KEY tanımlanmamış."}

    geo = _geocode(location)
    if "error" in geo:
        return {"location": location, "error": geo["error"]}

    try:
        params = {
            "lat": geo["lat"],
            "lon": geo["lon"],
            "appid": AGRO_API_KEY,
        }
        resp = requests.get(AGRO_FORECAST_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        def k2c(k):
            return round(k - 273.15) if k else 0

        forecasts = []
        for item in data if isinstance(data, list) else []:
            main = item.get("main", {})
            wind = item.get("wind", {})
            weather_info = item.get("weather", [{}])[0]
            clouds = item.get("clouds", {})
            rain = item.get("rain", {})

            main_condition = weather_info.get("main", "Unknown")
            condition = _CONDITION_MAP.get(main_condition, main_condition)

            forecasts.append({
                "dt": item.get("dt", 0),
                "temp": k2c(main.get("temp", 0)),
                "feels_like": k2c(main.get("feels_like", 0)),
                "temp_min": k2c(main.get("temp_min", 0)),
                "temp_max": k2c(main.get("temp_max", 0)),
                "humidity": main.get("humidity", 0),
                "pressure_hpa": main.get("pressure", 0),
                "wind_kmh": round(wind.get("speed", 0) * 3.6),
                "wind_deg": wind.get("deg", 0),
                "cloud_pct": clouds.get("all", 0),
                "rain_3h_mm": rain.get("3h", 0),
                "condition": condition,
                "description": weather_info.get("description", ""),
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
        return {"location": location, "error": f"Agro Forecast API hatası: {e}"}


def get_soil_data(polyid: str) -> dict:
    """
    Agro API üzerinden güncel toprak verisi al (ücretsiz).
    Toprak sıcaklığı ve nem oranı — sulama planlaması için kritik.
    Güncelleme sıklığı: Günde 2 kez.

    Args:
        polyid: Polygon ID (create_polygon ile oluşturulmuş)
    Returns:
        Toprak verisi: yüzey sıcaklığı, 10cm derinlik sıcaklığı, nem
    """
    if not _has_agro_key():
        return {"error": "AGRO_API_KEY tanımlanmamış."}

    try:
        params = {
            "polyid": polyid,
            "appid": AGRO_API_KEY,
        }
        resp = requests.get(AGRO_SOIL_URL, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()

        # Kelvin → Celsius çevrimi
        t0_k = data.get("t0", 0)
        t10_k = data.get("t10", 0)

        return {
            "source": "agro_api",
            "polyid": polyid,
            "dt": data.get("dt", 0),
            "surface_temp_c": round(t0_k - 273.15, 1) if t0_k else 0,      # Yüzey sıcaklığı (°C)
            "depth_10cm_temp_c": round(t10_k - 273.15, 1) if t10_k else 0,  # 10cm derinlik sıcaklığı (°C)
            "moisture": data.get("moisture", 0),                             # Toprak nemi (m³/m³)
            # Ham Kelvin değerleri de sakla
            "surface_temp_k": t0_k,
            "depth_10cm_temp_k": t10_k,
        }
    except requests.RequestException as e:
        return {"polyid": polyid, "error": f"Agro Soil API hatası: {e}"}


def get_uv_index(polyid: str) -> dict:
    """
    Agro API üzerinden güncel UV indeksi al (ücretsiz).
    Bitki stres değerlendirmesi ve çalışma saati planlaması için.

    Args:
        polyid: Polygon ID
    Returns:
        UV indeks verisi
    """
    if not _has_agro_key():
        return {"error": "AGRO_API_KEY tanımlanmamış."}

    try:
        params = {
            "polyid": polyid,
            "appid": AGRO_API_KEY,
        }
        resp = requests.get(AGRO_UVI_URL, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()

        uvi = data.get("uvi", 0)
        # UV seviye sınıflandırması
        if uvi <= 2:
            uv_level = "Düşük"
        elif uvi <= 5:
            uv_level = "Orta"
        elif uvi <= 7:
            uv_level = "Yüksek"
        elif uvi <= 10:
            uv_level = "Çok Yüksek"
        else:
            uv_level = "Aşırı"

        return {
            "source": "agro_api",
            "polyid": polyid,
            "dt": data.get("dt", 0),
            "uvi": uvi,                # UV indeks değeri (float)
            "uv_level": uv_level,      # Türkçe seviye açıklaması
        }
    except requests.RequestException as e:
        return {"polyid": polyid, "error": f"Agro UVI API hatası: {e}"}


def get_satellite_imagery(polyid: str, start: int = None, end: int = None) -> dict:
    """
    Agro API üzerinden uydu görüntülerini ara (NDVI, EVI, True/False Color).
    Ücretsiz plan — Sentinel-2 ve Landsat 8 verileri.

    Args:
        polyid: Polygon ID
        start: Başlangıç tarihi (unix timestamp). Varsayılan: 30 gün önce
        end:   Bitiş tarihi (unix timestamp). Varsayılan: şimdi
    Returns:
        Uydu görüntü URL'leri ve metadata listesi
    """
    if not _has_agro_key():
        return {"error": "AGRO_API_KEY tanımlanmamış."}

    now = int(time.time())
    if end is None:
        end = now
    if start is None:
        start = now - (30 * 24 * 3600)  # 30 gün önce

    try:
        params = {
            "polyid": polyid,
            "start": start,
            "end": end,
            "appid": AGRO_API_KEY,
        }
        resp = requests.get(AGRO_SATELLITE_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        results = []
        for item in data if isinstance(data, list) else []:
            results.append({
                "dt": item.get("dt", 0),
                "type": item.get("type", ""),            # "Landsat 8" veya "Sentinel 2"
                "coverage_pct": item.get("dc", 0),       # Geçerli veri kapsama %
                "cloud_pct": item.get("cl", 0),           # Bulut kapsama %
                "sun": item.get("sun", {}),               # Güneş açısı bilgisi
                # Görüntü URL'leri (PNG)
                "image_urls": item.get("image", {}),      # truecolor, falsecolor, ndvi, evi ...
                # Tile URL'leri (harita katmanları için)
                "tile_urls": item.get("tile", {}),
                # İstatistik URL'leri (NDVI/EVI min, max, median vb.)
                "stats_urls": item.get("stats", {}),
                # GeoTIFF URL'leri
                "data_urls": item.get("data", {}),
            })

        return {
            "source": "agro_api",
            "polyid": polyid,
            "start": start,
            "end": end,
            "count": len(results),
            "images": results,
        }
    except requests.RequestException as e:
        return {"polyid": polyid, "error": f"Agro Satellite API hatası: {e}"}


def get_ndvi_history(polyid: str, start: int = None, end: int = None) -> dict:
    """
    Agro API üzerinden NDVI geçmişi al (ücretsiz).
    Bitki sağlığı takibi — NDVI mevsimsel değişim analizi için.
    NDVI: -1 ile 1 arası değer. 0.6+ = sağlıklı bitki örtüsü.

    Args:
        polyid: Polygon ID
        start: Başlangıç tarihi (unix timestamp). Varsayılan: 90 gün önce
        end:   Bitiş tarihi (unix timestamp). Varsayılan: şimdi
    Returns:
        NDVI geçmiş verisi (günlük değerler)
    """
    if not _has_agro_key():
        return {"error": "AGRO_API_KEY tanımlanmamış."}

    now = int(time.time())
    if end is None:
        end = now
    if start is None:
        start = now - (90 * 24 * 3600)  # 90 gün önce

    try:
        params = {
            "polyid": polyid,
            "start": start,
            "end": end,
            "appid": AGRO_API_KEY,
        }
        resp = requests.get(AGRO_NDVI_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        entries = []
        for item in data if isinstance(data, list) else []:
            dc = item.get("dc", 0)
            ndvi_data = item.get("data", {})
            entries.append({
                "dt": item.get("dt", 0),
                "source": item.get("source", ""),
                "coverage_pct": dc,
                "cloud_pct": item.get("cl", 0),
                # NDVI istatistikleri
                "ndvi_mean": ndvi_data.get("mean", 0),
                "ndvi_median": ndvi_data.get("median", 0),
                "ndvi_min": ndvi_data.get("min", 0),
                "ndvi_max": ndvi_data.get("max", 0),
                "ndvi_std": ndvi_data.get("std", 0),
                "ndvi_p25": ndvi_data.get("p25", 0),
                "ndvi_p75": ndvi_data.get("p75", 0),
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
        return {"polyid": polyid, "error": f"Agro NDVI API hatası: {e}"}


# ── Birleşik Lokasyon Raporu ──────────────────────────────────────────────

def get_location_report(location: str) -> dict:
    """
    Bir lokasyon için TÜM tarımsal veriyi tek çağrıda döner:
    hava durumu + hava kirliliği + toprak + UV + son NDVI.

    İlk çağrıda arka planda polygon oluşturur ve diske cache'ler.
    Sonraki çağrılar aynı polygon'u yeniden kullanır (polygon_cache modülü).

    Not: Yeni oluşturulan polygon için NDVI/uydu verisi ~24 saat sonra dolar.
    İlk çağrıda ndvi_latest None dönebilir — bu beklenen davranıştır.

    Args:
        location: Şehir adı, ör. 'Antalya'
    Returns:
        Birleşik rapor: weather, soil, uv, ndvi_latest, polygon bilgisi
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

    # 1) Hava durumu (OWM + pollution + agro weather)
    weather = get_weather(location)
    report["weather"] = weather
    if "error" in weather:
        report["errors"].append({"weather": weather["error"]})

    # 2) Polygon (cache veya oluştur)
    poly = get_or_create_polygon(location)
    if "error" in poly:
        report["errors"].append({"polygon": poly["error"]})
        report["polygon"] = poly
        return report

    report["polygon"] = poly
    polyid = poly["id"]

    # 3) Toprak verisi
    soil = get_soil_data(polyid)
    report["soil"] = soil
    if "error" in soil:
        report["errors"].append({"soil": soil["error"]})

    # 4) UV indeksi
    uv = get_uv_index(polyid)
    report["uv"] = uv
    if "error" in uv:
        report["errors"].append({"uv": uv["error"]})

    # 5) NDVI geçmişi — son 30 gün, en güncel kaydı al
    now = int(time.time())
    ndvi = get_ndvi_history(polyid, start=now - 30 * 24 * 3600, end=now)
    if "error" in ndvi:
        report["errors"].append({"ndvi": ndvi["error"]})
    else:
        history = ndvi.get("history", [])
        if history:
            latest = max(history, key=lambda x: x.get("dt", 0))
            report["ndvi_latest"] = {
                "dt": latest.get("dt", 0),
                "ndvi_mean": latest.get("ndvi_mean", 0),
                "ndvi_median": latest.get("ndvi_median", 0),
                "ndvi_max": latest.get("ndvi_max", 0),
                "source": latest.get("source", ""),
            }
        else:
            report["ndvi_latest"] = None
            if not poly.get("cached", True):
                report["note"] = "NDVI verisi yeni polygon için ~24 saat sonra dolacak."

    return report


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
    print("=" * 60)
    print("TarlAI Tools - Test")
    print("=" * 60)

    # 1. Tek çağrıda tüm veri (hava + kirlilik + toprak + UV + NDVI)
    print("\n-- [1] Location Report (Antalya) --")
    report = get_location_report("Antalya")
    print(json.dumps(report, indent=2, ensure_ascii=False))

    # 2. 5 günlük tahmin (ilk 2 periyot)
    print("\n-- [2] Forecast (ilk 2) --")
    forecast = get_weather_forecast("Antalya")
    if "error" not in forecast:
        forecast["forecasts"] = forecast.get("forecasts", [])[:2]
    print(json.dumps(forecast, indent=2, ensure_ascii=False))

    # 3. Tedavi testi
    print("\n-- [3] Treatment --")
    print(json.dumps(get_treatment("leaf_spot"), indent=2, ensure_ascii=False))
