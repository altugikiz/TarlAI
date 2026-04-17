"""
TarlAI Weather API — OpenWeatherMap + AgroMonitoring weather functions.

Public API:
    get_weather(location)          -> OWM current + air pollution + agro weather
    get_weather_forecast(location) -> 5-day / 3-hour forecast via Agro API
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
AGRO_API_KEY = os.getenv("AGRO_API_KEY")

# ── Time & conversion constants ─────────────────────────────────────────────
MS_TO_KMH = 3.6
KELVIN_OFFSET = 273.15

# ── HTTP timeouts (seconds) ──────────────────────────────────────────────────
DEFAULT_TIMEOUT = 5
LONG_TIMEOUT = 10

# ── UV index thresholds (WHO scale) ─────────────────────────────────────────
UV_LOW_MAX = 2
UV_MODERATE_MAX = 5
UV_HIGH_MAX = 7
UV_VERY_HIGH_MAX = 10

# ── OpenWeatherMap API endpoints ─────────────────────────────────────────────
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
OPENWEATHER_POLLUTION_URL = "https://api.openweathermap.org/data/2.5/air_pollution"
GEOCODING_URL = "https://api.openweathermap.org/geo/1.0/direct"

# ── AgroMonitoring weather endpoints ─────────────────────────────────────────
AGRO_BASE_URL = "https://api.agromonitoring.com/agro/1.0"
AGRO_WEATHER_URL = f"{AGRO_BASE_URL}/weather"
AGRO_FORECAST_URL = f"{AGRO_BASE_URL}/weather/forecast"

# ── OWM condition code -> simplified label ───────────────────────────────────
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
