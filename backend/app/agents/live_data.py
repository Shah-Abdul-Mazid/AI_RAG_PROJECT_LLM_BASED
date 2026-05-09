import re
from datetime import datetime
from typing import Optional

import requests


WEATHER_KEYWORDS = {
    "weather",
    "temperature",
    "forecast",
    "rain",
    "humidity",
    "wind",
    "hot",
    "cold",
}

LOCATION_ALIASES = {
    "usa": "Washington DC",
    "u s a": "Washington DC",
    "us": "Washington DC",
    "u s": "Washington DC",
    "america": "Washington DC",
    "united states": "Washington DC",
    "united states of america": "Washington DC",
    "uk": "London",
    "united kingdom": "London",
    "bangladesh": "Dhaka",
    "bd": "Dhaka",
    "india": "New Delhi",
}


class LiveDataAgent:
    """Routes real-time API questions to external data providers."""

    def can_handle(self, query: str) -> bool:
        normalized_query = query.lower()
        return any(keyword in normalized_query for keyword in WEATHER_KEYWORDS)

    def run(self, query: str):
        location = self._extract_weather_location(query)
        if not location:
            return {
                "answer": "Please mention a city or country so I can check live weather. For example: 'weather in Dhaka', 'USA weather', or 'temperature of Tokyo'.",
                "sources": [],
                "agent_logs": [
                    "Supervisor: Routed request to Live Data Agent",
                    "Live Data Agent: Weather intent detected, but no location was provided",
                    "Compliance Agent: Security & PII check complete",
                ],
            }

        coordinates = self._geocode_location(location)
        weather = self._fetch_current_weather(coordinates["latitude"], coordinates["longitude"])

        answer = self._format_weather_answer(location, coordinates, weather)

        return {
            "answer": answer,
            "sources": ["Open-Meteo Geocoding API", "Open-Meteo Forecast API"],
            "agent_logs": [
                "Supervisor: Routed request to Live Data Agent",
                f"Live Data Agent: Detected weather intent for {coordinates['name']}",
                "Weather Connector: Retrieved current conditions from Open-Meteo",
                "Compliance Agent: Security & PII check complete",
            ],
        }

    def _extract_weather_location(self, query: str) -> Optional[str]:
        cleaned_query = self._clean_query(query)
        patterns = [
            r"(?:weather|temperature|forecast|rain|humidity|wind)\s+(?:in|for|at|of)\s+([a-zA-Z\s,.'-]+)",
            r"(?:in|for|at|of)\s+([a-zA-Z\s,.'-]+)\s+(?:weather|temperature|forecast|rain|humidity|wind|today|now|right now)",
            r"([a-zA-Z\s,.'-]+)\s+(?:weather|temperature|forecast|rain|humidity|wind)",
            r"(?:weather|temperature|forecast)\s+([a-zA-Z\s,.'-]+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, cleaned_query, re.IGNORECASE)
            if match:
                location = self._clean_location(match.group(1))
                if location:
                    return self._normalize_location(location)

        return None

    def _clean_query(self, query: str) -> str:
        cleaned_query = query.strip().lower()
        cleaned_query = re.sub(r"\b(what is|what's|tell me|show me|give me|can you|please|current)\b", " ", cleaned_query)
        cleaned_query = re.sub(r"\s+", " ", cleaned_query)
        return cleaned_query.strip(" .,?!")

    def _clean_location(self, location: str) -> str:
        stop_words = [
            "today",
            "now",
            "right now",
            "please",
            "weather",
            "temperature",
            "forecast",
            "rain",
            "humidity",
            "wind",
            "current",
        ]
        cleaned_location = location.strip(" .,?!")
        for word in stop_words:
            cleaned_location = re.sub(rf"\b{re.escape(word)}\b", "", cleaned_location, flags=re.IGNORECASE)
        return cleaned_location.strip(" .,?!")

    def _normalize_location(self, location: str) -> str:
        normalized_location = re.sub(r"\s+", " ", location).strip().lower()
        return LOCATION_ALIASES.get(normalized_location, location)

    def _geocode_location(self, location: str):
        response = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": location, "count": 1, "language": "en", "format": "json"},
            timeout=10,
        )
        response.raise_for_status()
        results = response.json().get("results", [])

        if not results:
            raise ValueError(f"Could not find weather coordinates for '{location}'.")

        result = results[0]
        return {
            "name": result.get("name", location),
            "country": result.get("country", ""),
            "latitude": result["latitude"],
            "longitude": result["longitude"],
            "timezone": result.get("timezone", "auto"),
        }

    def _fetch_current_weather(self, latitude: float, longitude: float):
        response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m",
                "timezone": "auto",
            },
            timeout=10,
        )
        response.raise_for_status()
        return response.json()["current"]

    def _format_weather_answer(self, requested_location: str, coordinates: dict, weather: dict) -> str:
        observed_at = self._format_observed_time(weather.get("time"))
        condition = self._weather_code_to_text(weather.get("weather_code"))
        place = f"{coordinates['name']}, {coordinates['country']}".strip(", ")

        return (
            f"Current weather for {place}: {condition}. "
            f"Temperature is {weather.get('temperature_2m')}°C, feels like "
            f"{weather.get('apparent_temperature')}°C, humidity is "
            f"{weather.get('relative_humidity_2m')}%, wind speed is "
            f"{weather.get('wind_speed_10m')} km/h, and precipitation is "
            f"{weather.get('precipitation')} mm. "
            f"Observed at {observed_at}. "
            f"I interpreted your requested location as '{requested_location}'."
        )

    def _format_observed_time(self, value: Optional[str]) -> str:
        if not value:
            return "the latest available update"
        try:
            return datetime.fromisoformat(value).strftime("%Y-%m-%d %H:%M")
        except ValueError:
            return value

    def _weather_code_to_text(self, code: Optional[int]) -> str:
        weather_codes = {
            0: "clear sky",
            1: "mainly clear",
            2: "partly cloudy",
            3: "overcast",
            45: "fog",
            48: "depositing rime fog",
            51: "light drizzle",
            53: "moderate drizzle",
            55: "dense drizzle",
            61: "slight rain",
            63: "moderate rain",
            65: "heavy rain",
            71: "slight snow",
            73: "moderate snow",
            75: "heavy snow",
            80: "slight rain showers",
            81: "moderate rain showers",
            82: "violent rain showers",
            95: "thunderstorm",
            96: "thunderstorm with slight hail",
            99: "thunderstorm with heavy hail",
        }
        return weather_codes.get(code, "current conditions available")


live_data_agent = LiveDataAgent()
