"""
Open-Meteo client for live external context (weather + geocoding).
"""

from typing import Optional

import httpx

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

DEFAULT_TIMEOUT_SECONDS = 8.0


class ExternalDataError(RuntimeError):
    """Raised when an external provider call fails or returns unusable data."""


async def get_coordinates(location_name: str) -> dict:
    params = {"name": location_name, "count": 1}
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT_SECONDS) as client:
        try:
            response = await client.get(GEOCODING_URL, params=params)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise ExternalDataError(f"Geocoding request failed: {exc}") from exc

    data = response.json()
    results = data.get("results")
    if not results:
        raise ExternalDataError(f"No geocoding match for '{location_name}'")

    top = results[0]
    return {
        "latitude": top["latitude"],
        "longitude": top["longitude"],
        "name": top.get("name", location_name),
    }


async def get_weather(latitude: float, longitude: float) -> dict:
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,precipitation,wind_speed_10m,weather_code",
    }
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT_SECONDS) as client:
        try:
            response = await client.get(WEATHER_URL, params=params)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise ExternalDataError(f"Weather request failed: {exc}") from exc

    data = response.json()
    current = data.get("current")
    if current is None:
        raise ExternalDataError("Weather response missing 'current' block")
    return current


async def get_weather_for_location(location_name: str) -> dict:
    coords = await get_coordinates(location_name)
    weather = await get_weather(coords["latitude"], coords["longitude"])
    weather["_resolved_location"] = coords
    return weather
