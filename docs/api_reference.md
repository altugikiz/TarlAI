# TarlAI Tools — API Reference

> Source: `src/tarlai_tools.py` and `src/polygon_cache.py`

---

## Architecture Overview

```
User (Gemma 4 function calling)
  │
  ├── get_weather(location)            ─── OWM Weather + Air Pollution + Agro Weather
  ├── get_weather_forecast(location)   ─── Agro Forecast API
  ├── get_location_report(location)    ─── All-in-one (calls everything below internally)
  │     ├── get_weather()
  │     ├── get_or_create_polygon()    ─── polygon_cache module
  │     ├── _get_soil_data(polyid)
  │     ├── _get_uv_index(polyid)
  │     └── _get_ndvi_history(polyid)
  └── get_treatment(disease_name)      ─── Static treatment DB lookup
```

---

## Environment Variables

| Variable | Required | Source | Description |
|---|---|---|---|
| `OPENWEATHER_API_KEY` | Yes | openweathermap.org | Used for weather, air pollution, geocoding |
| `AGRO_API_KEY` | No (optional) | agromonitoring.com | Used for soil, UV, NDVI, satellite, agro weather/forecast |

---

## External APIs Used

| API | Endpoint | Free Tier Limit |
|---|---|---|
| OWM Current Weather | `api.openweathermap.org/data/2.5/weather` | 60 calls/min |
| OWM Air Pollution | `api.openweathermap.org/data/2.5/air_pollution` | 60 calls/min |
| OWM Geocoding | `api.openweathermap.org/geo/1.0/direct` | 60 calls/min |
| Agro Weather | `api.agromonitoring.com/agro/1.0/weather` | 60 calls/min |
| Agro Forecast | `api.agromonitoring.com/agro/1.0/weather/forecast` | 60 calls/min |
| Agro Soil | `api.agromonitoring.com/agro/1.0/soil` | 60 calls/min |
| Agro UVI | `api.agromonitoring.com/agro/1.0/uvi` | 60 calls/min |
| Agro Satellite | `api.agromonitoring.com/agro/1.0/image/search` | 60 calls/min |
| Agro NDVI History | `api.agromonitoring.com/agro/1.0/ndvi/history` | 60 calls/min |
| Agro Polygons | `api.agromonitoring.com/agro/1.0/polygons` | 10 polygons/month |

---

## Public Functions

### `get_weather(location: str) -> dict`

Fetches current weather by merging three API sources into a single response.

**API calls made (sequentially):**
1. OWM `/weather` — core weather data
2. OWM `/air_pollution` — air quality metrics
3. Agro `/weather` — supplementary metrics (if AGRO_API_KEY set)

**Parameters:**
| Name | Type | Description |
|---|---|---|
| `location` | `str` | City name, e.g. `"Antalya"`, `"Istanbul"` |

**Returns:**

| Field | Type | Source | Description |
|---|---|---|---|
| `location` | `str` | input | City name |
| `lat` | `float` | OWM | Latitude |
| `lon` | `float` | OWM | Longitude |
| `dt` | `int` | Agro | Observation timestamp (Unix) |
| `temp` | `int` | OWM | Temperature (°C, rounded) |
| `feels_like` | `int` | OWM | Feels-like temperature (°C) |
| `temp_min` | `int` | OWM | Minimum temperature (°C) |
| `temp_max` | `int` | OWM | Maximum temperature (°C) |
| `humidity` | `int` | OWM | Humidity (%) |
| `pressure_hpa` | `int` | OWM | Atmospheric pressure (hPa) |
| `grnd_level_hpa` | `int` | OWM | Ground-level pressure (hPa) |
| `sea_level_hpa` | `int` | Agro | Sea-level pressure (hPa) |
| `cloud_pct` | `int` | OWM | Cloud cover (%) |
| `wind_kmh` | `int` | OWM | Wind speed (km/h, converted) |
| `wind_speed_ms` | `float` | Agro/OWM | Wind speed (m/s, raw) |
| `wind_deg` | `int` | OWM | Wind direction (degrees) |
| `wind_gust_kmh` | `int` | OWM | Wind gust (km/h, converted) |
| `wind_gust_ms` | `float` | Agro/OWM | Wind gust (m/s, raw) |
| `rain_1h_mm` | `float` | OWM | Rain volume last 1h (mm) |
| `rain_3h_mm` | `float` | OWM | Rain volume last 3h (mm) |
| `snow_1h_mm` | `float` | OWM | Snow volume last 1h (mm) |
| `snow_3h_mm` | `float` | OWM | Snow volume last 3h (mm) |
| `visibility_m` | `int` | OWM | Visibility (meters) |
| `sunrise` | `int` | OWM | Sunrise time (Unix) |
| `sunset` | `int` | OWM | Sunset time (Unix) |
| `condition` | `str` | OWM | Simplified condition (Sunny/Cloudy/Rainy/...) |
| `description` | `str` | OWM | Detailed description (Turkish) |
| `air_quality_index` | `int` | OWM | AQI (1=Good, 5=Very Poor) |
| `co` | `float` | OWM | Carbon monoxide (μg/m³) |
| `no` | `float` | OWM | Nitrogen monoxide (μg/m³) |
| `no2` | `float` | OWM | Nitrogen dioxide (μg/m³) |
| `o3` | `float` | OWM | Ozone (μg/m³) |
| `so2` | `float` | OWM | Sulphur dioxide (μg/m³) |
| `pm2_5` | `float` | OWM | Fine particles PM2.5 (μg/m³) |
| `pm10` | `float` | OWM | Coarse particles PM10 (μg/m³) |
| `nh3` | `float` | OWM | Ammonia (μg/m³) |

---

### `get_weather_forecast(location: str) -> dict`

Fetches 5-day / 3-hour weather forecast via Agro API. Temperatures are converted from Kelvin to Celsius.

**API calls made:**
1. OWM Geocoding `/direct` — resolve city to lat/lon
2. Agro `/weather/forecast` — forecast data

**Parameters:**
| Name | Type | Description |
|---|---|---|
| `location` | `str` | City name |

**Returns (top-level):**

| Field | Type | Description |
|---|---|---|
| `source` | `str` | Always `"agro_api"` |
| `location` | `str` | Resolved city name (Turkish) |
| `lat` | `float` | Latitude |
| `lon` | `float` | Longitude |
| `count` | `int` | Number of forecast periods |
| `forecasts` | `list[dict]` | List of 3-hour periods (see below) |

**Each forecast entry:**

| Field | Type | Description |
|---|---|---|
| `dt` | `int` | Forecast timestamp (Unix) |
| `temp` | `int` | Temperature (°C) |
| `feels_like` | `int` | Feels-like (°C) |
| `temp_min` | `int` | Min temperature (°C) |
| `temp_max` | `int` | Max temperature (°C) |
| `humidity` | `int` | Humidity (%) |
| `pressure_hpa` | `int` | Pressure (hPa) |
| `wind_kmh` | `int` | Wind speed (km/h) |
| `wind_deg` | `int` | Wind direction (degrees) |
| `cloud_pct` | `int` | Cloud cover (%) |
| `rain_3h_mm` | `float` | Rain volume 3h (mm) |
| `condition` | `str` | Simplified condition label |
| `description` | `str` | Detailed description |

---

### `get_location_report(location: str) -> dict`

All-in-one agricultural report. Combines weather, soil, UV, and NDVI in a single call. Internally manages polygon creation/caching.

**API calls made (up to 6):**
1. `get_weather()` — OWM weather + pollution + agro weather (3 calls)
2. `get_or_create_polygon()` — polygon cache or Agro polygon create
3. `_get_soil_data()` — Agro soil
4. `_get_uv_index()` — Agro UVI
5. `_get_ndvi_history()` — Agro NDVI

**Parameters:**
| Name | Type | Description |
|---|---|---|
| `location` | `str` | City name |

**Returns:**

| Field | Type | Description |
|---|---|---|
| `location` | `str` | City name |
| `weather` | `dict\|None` | Full weather data (same as `get_weather` output) |
| `polygon` | `dict\|None` | Polygon info: `id`, `lat`, `lon`, `name`, `area_ha`, `cached` |
| `soil` | `dict\|None` | Soil data (see below) |
| `uv` | `dict\|None` | UV index data (see below) |
| `ndvi_latest` | `dict\|None` | Most recent NDVI entry from last 30 days |
| `errors` | `list[dict]` | Any errors encountered (partial results still returned) |
| `note` | `str` | Present only for new polygons (NDVI ~24h delay warning) |

**Soil data fields (`report["soil"]`):**

| Field | Type | Description |
|---|---|---|
| `surface_temp_c` | `float` | Surface temperature (°C) |
| `depth_10cm_temp_c` | `float` | 10 cm depth temperature (°C) |
| `moisture` | `float` | Soil moisture (m³/m³) |
| `surface_temp_k` | `float` | Surface temperature (Kelvin, raw) |
| `depth_10cm_temp_k` | `float` | 10 cm depth temperature (Kelvin, raw) |

**UV data fields (`report["uv"]`):**

| Field | Type | Description |
|---|---|---|
| `uvi` | `float` | UV index value |
| `uv_level` | `str` | Risk level: Dusuk / Orta / Yuksek / Cok Yuksek / Asiri |

**NDVI latest fields (`report["ndvi_latest"]`):**

| Field | Type | Description |
|---|---|---|
| `dt` | `int` | Observation timestamp (Unix) |
| `ndvi_mean` | `float` | Mean NDVI (-1 to 1, healthy > 0.6) |
| `ndvi_median` | `float` | Median NDVI |
| `ndvi_max` | `float` | Max NDVI |
| `source` | `str` | Satellite source (Sentinel-2 / Landsat 8) |

---

### `get_treatment(disease_name: str) -> dict`

Looks up treatment information from a static database of 10 common plant diseases. Uses fuzzy substring matching.

**No API calls.** Pure local lookup.

**Parameters:**
| Name | Type | Description |
|---|---|---|
| `disease_name` | `str` | Disease identifier, e.g. `"early_blight"`, `"powdery_mildew"` |

**Returns:**

| Field | Type | Description |
|---|---|---|
| `name` | `str` | Full disease name (English + Turkish) |
| `chemical` | `str` | Chemical treatment options |
| `organic` | `str` | Organic treatment options |
| `interval` | `str` | Application interval |
| `notes` | `str` | Additional notes |

**Supported diseases:**

| Key | Name |
|---|---|
| `leaf_spot` | Leaf Spot (Yaprak Lekesi) |
| `early_blight` | Early Blight (Erken Yaniklik) |
| `late_blight` | Late Blight (Gec Yaniklik) |
| `powdery_mildew` | Powdery Mildew (Kulleme) |
| `downy_mildew` | Downy Mildew (Mildiyou) |
| `rust` | Rust (Pas Hastaligi) |
| `anthracnose` | Anthracnose (Antrakoz) |
| `bacterial_spot` | Bacterial Spot (Bakteriyel Leke) |
| `mosaic_virus` | Mosaic Virus (Mozaik Virusu) |
| `root_rot` | Root Rot (Kok Curumesi) |

---

## Internal Functions

These are **not** called directly by Gemma 4. They are used internally by `get_location_report`.

| Function | File | Description |
|---|---|---|
| `_geocode(location)` | `tarlai_tools.py` | City name -> lat/lon via OWM Geocoding API |
| `_get_soil_data(polyid)` | `tarlai_tools.py` | Soil temperature + moisture via Agro API |
| `_get_uv_index(polyid)` | `tarlai_tools.py` | UV index + risk level via Agro API |
| `_get_satellite_imagery(polyid, start, end)` | `tarlai_tools.py` | Sentinel-2 / Landsat 8 imagery search |
| `_get_ndvi_history(polyid, start, end)` | `tarlai_tools.py` | NDVI vegetation health history |
| `_has_agro_key()` | `tarlai_tools.py` | Check if AGRO_API_KEY is configured |
| `_kelvin_to_celsius(kelvin)` | `tarlai_tools.py` | Kelvin -> Celsius conversion |
| `_classify_uv(uvi)` | `tarlai_tools.py` | UV index -> Turkish risk label |

---

## Polygon Cache Module (`polygon_cache.py`)

Manages AgroMonitoring polygon creation and disk caching. Free plan allows max 10 polygons/month.

| Function | Description |
|---|---|
| `get_or_create_polygon(location)` | Returns cached polygon or creates new one. Auto-geocodes and builds 1 km² square. |
| `list_cached_polygons()` | Returns all cached polygons from `data/polygons.json`. |

**Cache file:** `data/polygons.json`

**Polygon entry fields:**

| Field | Type | Description |
|---|---|---|
| `id` | `str` | Agro API polygon ID |
| `lat` | `float` | Center latitude |
| `lon` | `float` | Center longitude |
| `name` | `str` | Turkish city name |
| `area_ha` | `float` | Polygon area (hectares) |
| `created_at` | `int` | Creation timestamp (Unix) |
| `cached` | `bool` | `true` if loaded from cache, `false` if just created |

---

## Constants

| Constant | Value | Description |
|---|---|---|
| `SECONDS_PER_DAY` | `86400` | Seconds in one day |
| `MS_TO_KMH` | `3.6` | m/s to km/h multiplier |
| `KELVIN_OFFSET` | `273.15` | Kelvin to Celsius offset |
| `DEFAULT_TIMEOUT` | `5` | HTTP timeout for most calls (seconds) |
| `LONG_TIMEOUT` | `10` | HTTP timeout for heavier calls (seconds) |
| `DEFAULT_SATELLITE_LOOKBACK_DAYS` | `30` | Default satellite image search window |
| `DEFAULT_NDVI_LOOKBACK_DAYS` | `90` | Default NDVI history window |
| `NDVI_REPORT_LOOKBACK_DAYS` | `30` | NDVI window used in location report |
| `UV_LOW_MAX` | `2` | UV index threshold: Low |
| `UV_MODERATE_MAX` | `5` | UV index threshold: Moderate |
| `UV_HIGH_MAX` | `7` | UV index threshold: High |
| `UV_VERY_HIGH_MAX` | `10` | UV index threshold: Very High |

---

## Error Handling

All functions return a dict with an `"error"` key on failure instead of raising exceptions. This allows partial results in composite calls like `get_location_report` — if soil API fails, weather data is still returned.

```python
result = get_weather("Antalya")
if "error" in result:
    print(result["error"])
else:
    print(result["temp"])
```

---

## Condition Mapping

OWM returns raw weather condition codes. TarlAI simplifies them:

| OWM Code | TarlAI Label |
|---|---|
| `Clear` | `Sunny` |
| `Clouds` | `Cloudy` |
| `Rain` | `Rainy` |
| `Drizzle` | `Rainy` |
| `Thunderstorm` | `Stormy` |
| `Snow` | `Snowy` |
| `Mist` | `Foggy` |
| `Fog` | `Foggy` |
| `Haze` | `Hazy` |
