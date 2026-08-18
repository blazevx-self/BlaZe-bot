from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    BOT_TOKEN: SecretStr
    ADMIN_ID: int

    TELEGRAPH_ACCESS_TOKEN: SecretStr
    TELEGRAPH_PAGE_PATH: str

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra="ignore",
    )

settings = Settings()
