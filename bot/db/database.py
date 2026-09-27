from datetime import datetime, timezone
from typing import List, Optional

import asyncpg

from config import settings
from bot.db.models import Lead

_pool: Optional[asyncpg.Pool] = None

DEFAULT_COURSE_PRICES = {
    "wedo": (350, 1200),
    "radio": (400, 1400),
    "scratch": (400, 1400),
    "python": (400, 1400),
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _row_to_lead(row: asyncpg.Record) -> Lead:
    data = dict(row)
    for key in ("created_at", "updated_at"):
        val = data.get(key)
        if hasattr(val, "isoformat"):
            data[key] = val.isoformat()
    return Lead(**data)


async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        raise RuntimeError("DB pool is not initialized. Call init_db() first.")
    return _pool


async def init_db():
    global _pool
    _pool = await asyncpg.create_pool(settings.pg_dsn, min_size=1, max_size=5)
    async with _pool.acquire() as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS leads (
                id SERIAL PRIMARY KEY,
                tg_user_id BIGINT NOT NULL,
                tg_username TEXT,
                parent_name TEXT NOT NULL,
                child_name TEXT NOT NULL,
                child_age INTEGER NOT NULL,
                course TEXT NOT NULL,
                phone TEXT NOT NULL,
                preferred_time TEXT,
                status TEXT NOT NULL DEFAULT 'new',
                created_at TIMESTAMPTZ NOT NULL,
                updated_at TIMESTAMPTZ NOT NULL
            )
            """
        )
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                tg_user_id BIGINT PRIMARY KEY,
                username TEXT,
                first_seen TIMESTAMPTZ NOT NULL,
                last_seen TIMESTAMPTZ NOT NULL
            )
            """
        )
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS course_prices (
                course TEXT PRIMARY KEY,
                single_price INTEGER NOT NULL,
                monthly_price INTEGER NOT NULL,
                updated_at TIMESTAMPTZ NOT NULL
            )
            """
        )
        now = datetime.now(timezone.utc)
        await db.executemany(
            """
            INSERT INTO course_prices (course, single_price, monthly_price, updated_at)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (course) DO NOTHING
            """,
            [
                (course, single_price, monthly_price, now)
                for course, (single_price, monthly_price) in DEFAULT_COURSE_PRICES.items()
            ],
        )
        await db.execute(
            """
            UPDATE leads
            SET course = 'Робототехніка'
            WHERE course IN ('WeDo', 'LEGO WeDo 2.0', 'wedo')
            """
        )


async def upsert_user(tg_user_id: int, username: Optional[str] = None):
    now = datetime.now(timezone.utc)
    pool = await get_pool()
    async with pool.acquire() as db:
        await db.execute(
            """
            INSERT INTO users (tg_user_id, username, first_seen, last_seen)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (tg_user_id) DO UPDATE SET
                username = EXCLUDED.username,
                last_seen = EXCLUDED.last_seen
            """,
            tg_user_id,
            username,
            now,
            now,
        )


async def create_lead(
    tg_user_id: int,
    tg_username: Optional[str],
    parent_name: str,
    child_name: str,
    child_age: int,
    course: str,
    phone: str,
    preferred_time: Optional[str] = None,
) -> int:
    now = datetime.now(timezone.utc)
    pool = await get_pool()
    async with pool.acquire() as db:
        row = await db.fetchrow(
            """
            INSERT INTO leads (
                tg_user_id, tg_username, parent_name, child_name, child_age,
                course, phone, preferred_time, status, created_at, updated_at
            ) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,'new',$9,$10)
            RETURNING id
            """,
            tg_user_id,
            tg_username,
            parent_name,
            child_name,
            child_age,
            course,
            phone,
            preferred_time,
            now,
            now,
        )
        return int(row["id"])


async def get_lead(lead_id: int) -> Optional[Lead]:
    pool = await get_pool()
    async with pool.acquire() as db:
        row = await db.fetchrow("SELECT * FROM leads WHERE id = $1", lead_id)
        return _row_to_lead(row) if row else None


async def get_recent_leads(limit: int = 10) -> List[Lead]:
    pool = await get_pool()
    async with pool.acquire() as db:
        rows = await db.fetch(
            "SELECT * FROM leads ORDER BY created_at DESC LIMIT $1", limit
        )
        return [_row_to_lead(r) for r in rows]


async def update_lead_status(lead_id: int, status: str) -> bool:
    now = datetime.now(timezone.utc)
    pool = await get_pool()
    async with pool.acquire() as db:
        result = await db.execute(
            "UPDATE leads SET status = $1, updated_at = $2 WHERE id = $3",
            status,
            now,
            lead_id,
        )
        return result.endswith("1")


async def get_stats() -> dict:
    pool = await get_pool()
    async with pool.acquire() as db:
        today = await db.fetchval(
            "SELECT COUNT(*) FROM leads WHERE created_at::date = CURRENT_DATE"
        )
        week = await db.fetchval(
            "SELECT COUNT(*) FROM leads WHERE created_at >= NOW() - INTERVAL '7 days'"
        )
        new_count = await db.fetchval(
            "SELECT COUNT(*) FROM leads WHERE status = 'new'"
        )
        return {"today": today, "week": week, "new": new_count}


async def get_course_prices() -> dict:
    pool = await get_pool()
    async with pool.acquire() as db:
        rows = await db.fetch(
            "SELECT course, single_price, monthly_price FROM course_prices"
        )
        return {row["course"]: dict(row) for row in rows}


async def update_course_price(course: str, single_price: int, monthly_price: int) -> bool:
    now = datetime.now(timezone.utc)
    pool = await get_pool()
    async with pool.acquire() as db:
        result = await db.execute(
            """
            UPDATE course_prices
            SET single_price = $1, monthly_price = $2, updated_at = $3
            WHERE course = $4
            """,
            single_price,
            monthly_price,
            now,
            course,
        )
        return result.endswith("1")
