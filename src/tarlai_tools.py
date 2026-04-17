"""
TarlAI Tools — Public API facade.

All implementation lives in the dedicated modules:
    weather_api  -> get_weather, get_weather_forecast
    agro_api     -> get_location_report
    diseases     -> get_treatment

This module re-exports everything so existing imports continue to work:
    from tarlai_tools import get_weather, get_weather_forecast, get_location_report, get_treatment
"""

from weather_api import get_weather, get_weather_forecast
from agro_api import get_location_report
from diseases import get_treatment

__all__ = ["get_weather", "get_weather_forecast", "get_location_report", "get_treatment"]


# ═══════════════════════════════════════════════════════════════════════════
#  MANUAL TEST
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import json

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
