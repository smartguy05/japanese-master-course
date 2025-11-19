"""
Application configuration management using Pydantic Settings.
"""

from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "Nihongo Sensei"
    app_version: str = "0.1.0"
    environment: str = Field(default="development", pattern="^(development|staging|production)$")
    log_level: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    debug: bool = Field(default=True)

    # Security
    secret_key: str = Field(
        default="INSECURE_DEV_KEY_CHANGE_IN_PRODUCTION",
        min_length=32,
    )
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Database
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "nihongo_sensei"
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"

    @property
    def database_url(self) -> str:
        """Construct async PostgreSQL database URL."""
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None

    @property
    def redis_url(self) -> str:
        """Construct Redis URL."""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    # AI Services
    anthropic_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    google_cloud_tts_key: Optional[str] = None

    ai_conversation_model: str = "claude-sonnet-4-20250514"
    ai_conversation_base_url: str = "https://api.anthropic.com"
    ai_stt_model: str = "whisper-1"
    ai_stt_base_url: str = "https://api.openai.com"
    ai_tts_model: str = "ja-JP-Neural2-B"

    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:3001"]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        """Parse CORS origins from comma-separated string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    # Content Generation
    content_generation_model: str = "claude-sonnet-4-20250514"
    enable_content_caching: bool = True


# Global settings instance
settings = Settings()
