import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


load_dotenv(override=False)


@dataclass(frozen=True)
class Settings:
    nba_api_key: str | None
    database_url: str


def get_settings() -> Settings:
    api_key = os.getenv("NBA_API_KEY")
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        # default to sqlite in project root
        db_url = f"sqlite:///{Path.cwd() / 'nba.sqlite3'}"
    return Settings(nba_api_key=api_key, database_url=db_url)
