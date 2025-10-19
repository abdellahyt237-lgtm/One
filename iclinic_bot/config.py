from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv


def _get_env(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None or value == "":
        if default is None:
            raise RuntimeError(f"Missing required environment variable: {name}")
        return default
    return value


@dataclass(frozen=True)
class Settings:
    bot_token: str
    admin_id: int
    database_path: str


def load_settings() -> Settings:
    # Load .env if present
    load_dotenv()
    token = _get_env("BOT_TOKEN")
    admin_id = int(_get_env("ADMIN_ID"))
    database_path = _get_env("DATABASE_PATH", "data/iclinic.db")
    return Settings(bot_token=token, admin_id=admin_id, database_path=database_path)
