from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    app_env: str = "development"
    api_prefix: str = "/api/v1"
    data_store_backend: str = "memory"
    google_cloud_project: str = "heart-alignment-local"
    firestore_database: str = "(default)"
    firestore_emulator_host: str | None = None
    admin_api_token: str | None = None
    admin_auth_mode: str = "token"
    admin_firebase_claim: str = "admin"
    cors_origins: list[str] = ["http://localhost:5173"]

    # OpenAI
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    openai_max_tokens: int = 1024

    model_config = SettingsConfigDict(
        env_file=REPOSITORY_ROOT / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("api_prefix")
    @classmethod
    def normalize_api_prefix(cls, value: str) -> str:
        value = value.strip()
        if not value.startswith("/"):
            value = f"/{value}"
        return value.rstrip("/")


@lru_cache
def get_settings() -> Settings:
    return Settings()
