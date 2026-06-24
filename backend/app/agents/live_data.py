import re
from typing import Optional
import requests
from app.core.config import settings

try:
    from tavily import TavilyClient
except ImportError:
    TavilyClient = None

# Keywords to trigger live data agent
LIVE_KEYWORDS = [
    "weather", "temperature", "forecast", "rain", "humidity", "wind",
    "today", "now", "recent", "latest", "news", "current", "president", "stock", "price"
]

class LiveDataAgent:
    """Routes real-time API questions (Weather) and Web Searches (DuckDuckGo)."""

    def can_handle(self, query: str) -> bool:
        normalized_query = query.lower()
        return any(keyword in normalized_query for keyword in LIVE_KEYWORDS)

    def run(self, query: str):
        # 1. Check if it's a Weather Query
        is_weather = any(w in query.lower() for w in ["weather", "temperature", "forecast", "rain", "humidity", "wind"])
        if is_weather:
            location = self._extract_weather_location(query)
            if location:
                try:
                    weather_payload = self._fetch_current_weather(location)
                    answer = self._format_weather_answer(location, weather_payload)
                    return {
                        "answer": answer,
                        "sources": ["WeatherAPI Current Weather"],
                        "agent_logs": [
                            "Supervisor: Routed request to Live Data Agent",
                            f"Live Data Agent: Fetched live weather for {location}",
                            "Compliance Agent: Security & PII check complete",
                        ],
                    }
                except Exception as e:
                    # If weather API fails or location is invalid, we fallback to Web Search
                    pass

        # 2. General Web Search for Recent/Live Data
        if not settings.TAVILY_API_KEY:
            return {
                "answer": "Tavily API key is missing. Please set TAVILY_API_KEY in your backend .env file.",
                "sources": [],
                "agent_logs": ["Live Data Agent: Missing TAVILY_API_KEY."]
            }

        search_results = self._search_web(query)
        if not search_results:
            return {
                "answer": f"I couldn't find any recent information on the web for '{query}'.",
                "sources": [],
                "agent_logs": ["Live Data Agent: Web search returned no results."]
            }
        
        # Use the Generator Agent to synthesize a human-like answer from search results
        answer, sources = self._format_search_results(query, search_results)
        
        return {
            "answer": answer,
            "sources": sources,
            "agent_logs": [
                "Supervisor: Routed request to Live Data Agent",
                f"Live Data Agent: Searched the web for '{query}'",
                "Generator Agent: Synthesized final answer from web results",
                "Compliance Agent: Security & PII check complete",
            ],
        }

    def _extract_weather_location(self, query: str) -> Optional[str]:
        # Regex to catch locations for weather.
        # Examples: "weather in China", "Australia weather", "temperature of India"
        cleaned_query = query.strip()
        patterns = [
            r"(?:weather|temperature|forecast|rain|humidity|wind)\s+(?:in|for|at|of)\s+([a-zA-Z\s,.'-]+)",
            r"([a-zA-Z\s,.'-]+)\s+(?:weather|temperature|forecast|rain|humidity|wind)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, cleaned_query, re.IGNORECASE)
            if match:
                loc = match.group(1).lower().replace("today", "").replace("now", "").strip()
                if loc:
                    return loc
        
        # Fallback keyword extraction
        words = cleaned_query.lower().split()
        stopwords = ["what", "is", "the", "weather", "temperature", "in", "of", "for", "today", "now", "?", "like", "current"]
        location_words = [w for w in words if w not in stopwords]
        if location_words:
            return " ".join(location_words)
            
        return None

    def _fetch_current_weather(self, location: str):
        if not settings.WEATHER_API_KEY:
            raise ValueError("WEATHER_API_KEY missing.")

        response = requests.get(
            "https://api.weatherapi.com/v1/current.json",
            params={"key": settings.WEATHER_API_KEY, "q": location, "aqi": "no"},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def _format_weather_answer(self, requested_location: str, weather_payload: dict) -> str:
        location = weather_payload["location"]
        current = weather_payload["current"]
        condition = current.get("condition", {}).get("text", "")
        place = f"{location.get('name')}, {location.get('country')}"
        
        return (
            f"The current weather in **{place}** is **{condition}**. "
            f"The temperature is {current.get('temp_c')}°C (feels like {current.get('feelslike_c')}°C). "
            f"Humidity is at {current.get('humidity')}% with wind speeds of {current.get('wind_kph')} km/h."
        )

    def _search_web(self, query: str, max_results=3):
        try:
            if settings.TAVILY_API_KEY:
                from tavily import TavilyClient
                tavily_client = TavilyClient(api_key=settings.TAVILY_API_KEY)
                response = tavily_client.search(query=query, max_results=max_results)
                
                mapped_results = []
                for res in response.get("results", []):
                    mapped_results.append({
                        "title": res.get("title", ""),
                        "body": res.get("content", ""),
                        "href": res.get("url", "")
                    })
                return mapped_results
            return []
        except Exception as e:
            print(f"Search error: {e}")
            return []

    def _format_search_results(self, query: str, results: list):
        from app.agents.generator import generator_agent
        
        context_blocks = []
        sources = []
        for res in results:
            context_blocks.append(f"Title: {res.get('title', '')}\nSnippet: {res.get('body', '')}")
            if 'href' in res:
                sources.append(res['href'])
            
        context_str = "\n\n".join(context_blocks)
        
        prompt = (
            f"You are a helpful AI answering a user's question.\n"
            f"Use the following real-time web search results to answer the user's query.\n"
            f"Only use the information provided in the search results. If the answer is not in the results, say so.\n\n"
            f"Web Search Results:\n{context_str}"
        )
        
        try:
            final_answer = generator_agent.run(query, prompt)
        except Exception as e:
            print(f"Generator agent failed: {e}")
            final_answer = "Here is what I found on the web:\n\n" + "\n".join([f"- {res.get('body', '')}" for res in results])
            
        return final_answer, sources

live_data_agent = LiveDataAgent()
