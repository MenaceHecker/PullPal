import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import get_settings
from app.generator import tick
from app.routers import deploys, logs, metrics, scenarios, services
from app.seed import seed_deploy_history
from app.state import store

settings = get_settings()


async def _tick_loop() -> None:
    while True:
        tick(store)
        await asyncio.sleep(settings.tick_interval_seconds)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    seed_deploy_history(store)
    tick(store)  # so the API has data to serve immediately, not just after the first interval
    task = asyncio.create_task(_tick_loop())
    yield
    task.cancel()


app = FastAPI(
    title="Sentra Simulated System",
    version="0.1.0",
    description="A small demo microservice stack that emits logs, metrics, and deploy "
    "history for Sentra to investigate. Not a real system, purely for the demo.",
    lifespan=lifespan,
)

app.include_router(services.router)
app.include_router(logs.router)
app.include_router(metrics.router)
app.include_router(deploys.router)
app.include_router(scenarios.router)


@app.get("/health")
def health() -> dict:
    """Liveness check: process is up."""
    return {"status": "ok"}
