from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    database_url: str = Field(validation_alias="DATABASE_URL")

    CORS_ORIGINS: str = "http://localhost:8800,https://moisesmayyer.github.io"

    @property
    def cors_origins(self) -> list[str]:
        return [
            origem.strip()
            for origem in self.CORS_ORIGINS.split(",")
            if origem.strip()
        ]


settings = Settings()  # type: ignore[call-arg]  # valores vindos do .env
