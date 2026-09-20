from pydantic import SecretStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = Field(default=...)
    BOT_TOKEN: SecretStr = Field(default=...)
    ADMIN_IDS: list[int] = Field(default=...)

    TELEGRAPH_ACCESS_TOKEN: SecretStr = Field(default=...)
    TELEGRAPH_PAGE_PATH: str = Field(default=...)

    BACKUP_DIR: str = Field(default=...)
    BACKUP_CHANNEL_ID: int = Field(default=...)

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra="ignore",
    )

settings = Settings()