from pathlib import Path

from decimal import Decimal
from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"

    DATABASE_URL: str | None = None

    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "gem_pipeline"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"

    DATA_DIR: str = "data"
    RAW_GEM_DIR: str = "data/raw/gem"

    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen3:4b"

    LLM_PROVIDER: str = "fake"
    LLM_API_KEY: str | None = None
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_MAX_INPUT_CHARS: int = 15000
    LLM_FALLBACK_TO_FAKE_ON_ERROR: bool = True
    LLM_INPUT_COST_PER_1K_TOKENS_INR: Decimal = Decimal("0")
    LLM_OUTPUT_COST_PER_1K_TOKENS_INR: Decimal = Decimal("0")

    @computed_field
    @property
    def sqlalchemy_database_uri(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @computed_field
    @property
    def data_dir_path(self) -> Path:
        return Path(self.DATA_DIR)

    @computed_field
    @property
    def raw_gem_dir_path(self) -> Path:
        return Path(self.RAW_GEM_DIR)

    def ensure_directories(self) -> None:
        self.data_dir_path.mkdir(parents=True, exist_ok=True)
        self.raw_gem_dir_path.mkdir(parents=True, exist_ok=True)


settings = Settings()