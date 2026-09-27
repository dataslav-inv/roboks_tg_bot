import os
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

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


def _missing_env() -> list[str]:
    keys = ("BOT_TOKEN", "ADMIN_CHAT_IDS", "DATABASE_URL")
    return [k for k in keys if not os.getenv(k)]


_missing = _missing_env()
if _missing:
    raise RuntimeError(
        "Немає змінних оточення: "
        + ", ".join(_missing)
        + ". Додайте їх у Railway → сервіс БОТА → Variables і зробіть Redeploy."
    )

settings = Settings()
