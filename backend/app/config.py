from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_PATH = Path(__file__).resolve().parents[2] / ".env"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(ENV_PATH), extra="ignore")
    database_url: str
    gemini_api_key: str
    google_client_id: str
    # Signs our own session tokens (JWTs). Long random value, never committed.
    # Generate with: python -c "import secrets; print(secrets.token_urlsafe(48))"
    session_secret: str = Field(min_length=32)

settings = Settings()
