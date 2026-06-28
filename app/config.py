from pathlib import Path

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