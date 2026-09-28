from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings

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


@app.get("/health")
def health() -> dict:
    """Liveness check: process is up."""
    return {"status": "ok"}


@app.get("/ready")
def ready() -> dict:
    """Readiness check: placeholder until DB connectivity is wired in Phase 1."""
    return {"status": "ready"}