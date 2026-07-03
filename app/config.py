from pathlib import Path

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.llm.client import BaseLLMExtractor
from app.llm.schemas import TenderLLMExtraction


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

    LLM_FALLBACK_TO_FAKE_ON_ERROR: bool = True
    LLM_PROVIDER: str = "fake"
    LLM_API_KEY: str | None = None
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_MAX_INPUT_CHARS: int = 15000

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

class SafeLLMExtractor:
    def __init__(self, primary: BaseLLMExtractor, fallback: BaseLLMExtractor | None = None):
        self.primary = primary
        self.fallback = fallback

    def extract_tender_details(self, text: str) -> TenderLLMExtraction:
        try:
            return self.primary.extract_tender_details(text)
        except Exception:
            if self.fallback is not None:
                return self.fallback.extract_tender_details(text)
            raise


settings = Settings()