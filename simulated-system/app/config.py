from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "development"
    log_level: str = "INFO"

    # How often the background generator emits a new batch of logs and metrics.
    tick_interval_seconds: float = 2.0

    # How much log/metric history to keep in memory per service before old
    # entries get dropped. This is a live demo system, not a data store.
    log_buffer_size: int = 2000
    metric_buffer_size: int = 2000


@lru_cache
def get_settings() -> Settings:
    return Settings()
