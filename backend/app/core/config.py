import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Nexus Intelligence"
    API_V1_STR: str = "/api/v1"
    
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "ollama")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GROK_API_KEY: str = os.getenv("GROK_API_KEY", "")
    WEATHER_API_KEY: str = os.getenv("WEATHER_API_KEY", "")
    
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.1")
    
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data/app.db")

    
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
    PINECONE_INDEX_NAME: str = os.getenv("PINECONE_INDEX_NAME", "enterprise-rag")
    
    UPLOADS_DIR: str = os.getenv("UPLOADS_DIR", "./uploads")

settings = Settings()
