import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import chat, upload, scrape, admin, auth
from app.core.config import settings
from app.db.database import Base, engine
from app.db import models

# ─── Application ──────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Enterprise Multi-Agent RAG Platform",
    version="1.0.0"
)
Base.metadata.create_all(bind=engine)

# ─── Middleware ────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth.router,   prefix="/api/v1/auth", tags=["Auth"])
app.include_router(chat.router,   prefix="/api/v1", tags=["Chat"])
app.include_router(upload.router, prefix="/api/v1", tags=["Upload"])
app.include_router(scrape.router, prefix="/api/v1", tags=["Scrape"])
app.include_router(admin.router,  prefix="/api/v1", tags=["Admin"])

# ─── Health Check ──────────────────────────────────────────────────────────────
@app.get("/")
async def root():
    return {"status": "online", "project": settings.PROJECT_NAME}

# ─── Entry Point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"Starting {settings.PROJECT_NAME}...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
