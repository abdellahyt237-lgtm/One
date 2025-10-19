import aiosqlite
import asyncio
import os
from contextlib import asynccontextmanager
from typing import AsyncIterator

DB_PATH = os.getenv("DATABASE_PATH", "./iclinic.db")

INIT_SQL = """
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    tg_id INTEGER UNIQUE NOT NULL,
    language TEXT NOT NULL DEFAULT 'fr',
    created_at DATETIME DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type TEXT NOT NULL,
    started_at DATETIME NOT NULL,
    ended_at DATETIME,
    meta TEXT
);
"""

async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(INIT_SQL)
        await db.commit()

@asynccontextmanager
async def get_db() -> AsyncIterator[aiosqlite.Connection]:
    db = await aiosqlite.connect(DB_PATH)
    try:
        db.row_factory = aiosqlite.Row
        yield db
    finally:
        await db.close()

async def ensure_user(tg_id: int, language: str = "fr") -> None:
    async with get_db() as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (tg_id, language) VALUES (?, ?)",
            (tg_id, language),
        )
        await db.commit()

if __name__ == "__main__":
    asyncio.run(init_db())
