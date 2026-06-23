import requests
from app.core.config import settings

SYSTEM_PROMPT = (
    "You are Nexus Intelligence, an enterprise AI assistant. "
    "Answer the user's question based on the provided context. "
    "If the context does not contain enough information, say so clearly."
)

class GeneratorAgent:
    def run(self, query: str, context: str, provider: str = None):
        selected_provider = provider or settings.LLM_PROVIDER
        print(f"Generator Agent active using {selected_provider}...")
        
        try:
            return self._call_provider(selected_provider, query, context)
        except Exception as e:
            print(f"Error with {selected_provider}: {e}")
            raise e

    def _call_provider(self, provider: str, query: str, context: str):
        user_content = f"{SYSTEM_PROMPT}\n\nContext:\n{context}\n\nQuestion: {query}"

        if provider == "openai":
            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {settings.OPENAI_API_KEY}"}
            payload = {
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": user_content}]
            }
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

        elif provider == "grok":
            url = "https://api.x.ai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {settings.GROK_API_KEY}"}
            payload = {
                "model": "grok-2-1212",
                "messages": [{"role": "user", "content": user_content}]
            }
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

        elif provider == "bedrock":
            import boto3
            import json
            client = boto3.client("bedrock-runtime", region_name="us-east-1")
            model_id = "meta.llama3-70b-instruct-v1:0"
            payload = {
                "prompt": f"{user_content}\n\nAnswer:",
                "max_gen_len": 512,
                "temperature": 0.5,
                "top_p": 0.9
            }
            response = client.invoke_model(
                modelId=model_id,
                body=json.dumps(payload)
            )
            response_body = json.loads(response["body"].read())
            return response_body.get("generation", "No response generated.")

        else:
            # ✅ FIX: Gemini returns 'candidates', NOT 'contents'
            url = (
                f"https://generativelanguage.googleapis.com/v1beta/models/"
                f"gemini-1.5-flash:generateContent?key={settings.GOOGLE_API_KEY}"
            )
            payload = {
                "contents": [{"parts": [{"text": user_content}]}]
            }
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()

            # Gemini response structure: data["candidates"][0]["content"]["parts"][0]["text"]
            candidates = data.get("candidates", [])
            if not candidates:
                raise ValueError(f"Gemini returned no candidates. Full response: {data}")
            return candidates[0]["content"]["parts"][0]["text"]

generator_agent = GeneratorAgent()
