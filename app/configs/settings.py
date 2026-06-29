from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///database.db"
    BOT_TOKEN: SecretStr
    ADMIN_ID: int

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra="ignore",
    )

settings = Settings()
