import requests
from app.core.config import settings

class GeneratorAgent:
    def run(self, query: str, context: str):
        print("Generator Agent active...")
        if settings.LLM_PROVIDER == "openai":
            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {settings.OPENAI_API_KEY}"}
            payload = {
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": f"Context: {context}\n\nQuery: {query}"}]
            }
            response = requests.post(url, headers=headers, json=payload)
            return response.json()["choices"][0]["message"]["content"]
        elif settings.LLM_PROVIDER == "grok":
            url = "https://api.x.ai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {settings.GROK_API_KEY}"}
            payload = {
                "model": "grok-2-1212",
                "messages": [{"role": "user", "content": f"Context: {context}\n\nQuery: {query}"}]
            }
            response = requests.post(url, headers=headers, json=payload)
            return response.json()["choices"][0]["message"]["content"]
        else:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.GOOGLE_API_KEY}"
            payload = {"contents": [{"parts": [{"text": f"Context: {context}\n\nQuery: {query}"}]}]}
            response = requests.post(url, json=payload)
            return response.json()["contents"][0]["parts"][0]["text"]

generator_agent = GeneratorAgent()
