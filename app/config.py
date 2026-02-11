from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "VCF Backend"
    app_env: str = "development"

    vcf_base_url: str = Field(default="https://vcf.example.local", alias="VCF_BASE_URL")
    vcf_verify_ssl: bool = Field(default=True, alias="VCF_VERIFY_SSL")
    vcf_timeout_seconds: float = Field(default=10.0, alias="VCF_TIMEOUT_SECONDS")
    vcf_retry_count: int = Field(default=2, alias="VCF_RETRY_COUNT")

    cors_allow_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"], alias="CORS_ALLOW_ORIGINS")
    session_ttl_seconds: int = Field(default=3600, alias="SESSION_TTL_SECONDS")

    @field_validator("cors_allow_origins", mode="before")
    @classmethod
    def parse_cors_allow_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        raise ValueError("Invalid CORS_ALLOW_ORIGINS format")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
