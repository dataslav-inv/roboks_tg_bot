from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    BOT_TOKEN: str
    ADMIN_CHAT_IDS: str
    DATABASE_URL: str

    @property
    def admin_ids(self) -> List[int]:
        return [int(x.strip()) for x in self.ADMIN_CHAT_IDS.split(",") if x.strip()]

    @property
    def pg_dsn(self) -> str:
        url = self.DATABASE_URL
        if url.startswith("postgres://"):
            url = "postgresql://" + url[len("postgres://") :]
        return url


settings = Settings()
