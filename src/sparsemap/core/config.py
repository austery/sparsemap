from functools import lru_cache

from pydantic import AnyUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Application
    app_name: str = "SparseMap"
    environment: str = "development"

    # Database (must be provided via .env)
    database_url: str

    # LLM Configuration (must be provided via .env)
    llm_api_key: str
    llm_model: str = "gemini-2.0-flash-exp"
    llm_temperature: float = 0.2
    llm_max_tokens: int = 2000
    llm_max_retries: int = 2

    # Content Extractor
    extractor_max_chars: int = 8000
    extractor_min_chars: int = 200


@lru_cache
def get_settings() -> Settings:
    return Settings()
