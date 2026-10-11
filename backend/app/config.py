import json
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Weather Drift Detection"
    database_url: str = "sqlite:///./weather_drift.db"
    jwt_secret_key: str = "replace-me-with-strong-secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    cors_origins: str = "http://localhost:5173"
    environment: str = "development"
    debug: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    @property
    def cors_origins_list(self) -> List[str]:
        value = (self.cors_origins or "").strip()
        if not value:
            return ["http://localhost:5173"]
        if value.startswith("["):
            return json.loads(value)
        if "," in value:
            return [item.strip() for item in value.split(",") if item.strip()]
        return [value]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
