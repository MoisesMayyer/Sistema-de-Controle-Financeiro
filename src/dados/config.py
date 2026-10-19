from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, env_file_encoding="utf-8")

    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    banco_dados: str = Field(default="sqlite:///./financeiro.db", validation_alias="BANCODADOS")


settings = Settings()  # type: ignore[call-arg]  # valores vindos do .env
