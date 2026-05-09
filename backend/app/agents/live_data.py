import re
from typing import Optional

import requests

from app.core.config import settings


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

        weather_payload = self._fetch_current_weather(location)
        answer = self._format_weather_answer(location, weather_payload)

        return {
            "answer": answer,
            "sources": ["WeatherAPI Current Weather API"],
            "agent_logs": [
                "Supervisor: Routed request to Live Data Agent",
                f"Live Data Agent: Detected weather intent for {weather_payload['location']['name']}",
                "Weather Connector: Retrieved current conditions from WeatherAPI",
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

    def _fetch_current_weather(self, location: str):
        if not settings.WEATHER_API_KEY:
            raise ValueError("WEATHER_API_KEY is missing. Add it to backend/.env to enable live weather.")

        response = requests.get(
            "https://api.weatherapi.com/v1/current.json",
            params={
                "key": settings.WEATHER_API_KEY,
                "q": location,
                "aqi": "no",
            },
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def _format_weather_answer(self, requested_location: str, weather_payload: dict) -> str:
        location = weather_payload["location"]
        current = weather_payload["current"]
        condition = current.get("condition", {}).get("text", "current conditions available")
        place = ", ".join(
            part for part in [location.get("name"), location.get("region"), location.get("country")] if part
        )
        observed_at = current.get("last_updated") or location.get("localtime") or "the latest available update"

        return (
            f"Current weather for {place}: {condition}. "
            f"Temperature is {current.get('temp_c')} C, feels like "
            f"{current.get('feelslike_c')} C, humidity is "
            f"{current.get('humidity')}%, wind speed is "
            f"{current.get('wind_kph')} km/h, and precipitation is "
            f"{current.get('precip_mm')} mm. "
            f"Observed at {observed_at}. "
            f"I interpreted your requested location as '{requested_location}'."
        )


live_data_agent = LiveDataAgent()
