from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

DATABASE_URL = settings.DATABASE_URL

# SQLite needs special args; PostgreSQL does not
connect_args = {}
engine_kwargs = {}

if DATABASE_URL.startswith("sqlite"):
    import os
    # sqlite:///./data/app.db or sqlite:////path/to/app.db
    # extract path by stripping sqlite:/// prefix (allowing for varying slashes)
    db_path = DATABASE_URL.replace("sqlite:///", "").replace("sqlite://", "")
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    connect_args = {"check_same_thread": False}
else:
    # PostgreSQL / RDS: use connection pooling for production stability
    engine_kwargs = {
        "pool_size": 5,
        "max_overflow": 10,
        "pool_pre_ping": True,   # auto-reconnect if connection dropped
        "pool_recycle": 300,     # recycle connections every 5 minutes
    }

engine = create_engine(DATABASE_URL, connect_args=connect_args, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
