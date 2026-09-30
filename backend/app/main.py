from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import get_settings
from app.db import engine
from app.routers import auth, incidents

settings = get_settings()

app = FastAPI(
    title="Sentra API",
    version="0.1.0",
    description="AI incident copilot — evidence-grounded triage with a hard human approval gate.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(incidents.router)


@app.get("/health")
def health() -> dict:
    """Liveness check: process is up."""
    return {"status": "ok"}


@app.get("/ready")
def ready() -> dict:
    """Readiness check: confirms the database is reachable."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception:
        return {"status": "not_ready"}