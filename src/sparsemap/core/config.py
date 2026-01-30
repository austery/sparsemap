from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Application
    app_name: str = "SparseMap"
    environment: str = "development"

    # Database (must be provided via .env)
    database_url: str

    # LLM Configuration
    llm_provider: str = "gemini"  # Options: "gemini" or "deepseek"
    llm_api_key: str  # Required: API key for chosen provider
    llm_model: str = "gemini-2.0-flash-exp"  # Model name
    llm_temperature: float = 0.2
    llm_max_tokens: int = 4000  # Increased for complex prompts
    llm_max_retries: int = 2

    # DeepSeek specific (only used when llm_provider="deepseek")
    llm_base_url: str = "https://space.ai-builders.com/backend/v1"

    # Content Extractor
    extractor_max_chars: int = 8000
    extractor_min_chars: int = 200


@lru_cache
def get_settings() -> Settings:
    return Settings()
