import os
from pymongo import MongoClient
from pymongo.database import Database
from dotenv import load_dotenv

load_dotenv()  # Load .env file before reading environment variables

MONGODB_URL = os.getenv("DATABASE_URL")  # Default to a placeholder if not set

# ─── Derive the database name ──────────────────────────────────────────────────
# For  mongodb+srv://user:pass@cluster/dbname  → extract "dbname"
# For  mongodb://localhost:27017/nexus_db      → extract "nexus_db"
def _get_db_name(url: str) -> str:
    path = url.split("/")[-1]
    name = path.split("?")[0].strip()
    return name if name else "nexus_db"

_client: MongoClient = None

def get_client() -> MongoClient:
    global _client
    if _client is None:
        _client = MongoClient(MONGODB_URL)
    return _client

def get_database() -> Database:
    client = get_client()
    db_name = _get_db_name(MONGODB_URL)
    return client[db_name]

# FastAPI dependency — yields a MongoDB Database instance
def get_db():
    db = get_database()
    try:
        yield db
    finally:
        pass  # MongoClient is persistent; no per-request teardown needed

# Create indexes on startup (called from main.py)
def init_db():
    db = get_database()
    db["users"].create_index("email", unique=True)
    db["chats"].create_index("user_id")
    db["messages"].create_index("chat_id")
    print("[OK] MongoDB indexes ensured.")

