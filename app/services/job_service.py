import aiosqlite
from datetime import datetime, timezone
from typing import Optional

from app.utils.logger import get_logger

logger = get_logger(__name__)
DB_PATH = "research.db"


async def init_db():
    """Create jobs table if it doesn't exist."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                job_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                query TEXT NOT NULL,
                depth TEXT DEFAULT 'standard',
                report_path TEXT,
                sources_count INTEGER DEFAULT 0,
                error TEXT,
                created_at TEXT NOT NULL,
                completed_at TEXT,
                duration_seconds REAL
            )
            """
        )
        await db.commit()
    logger.info("Database initialized.")


async def create_job(job_id: str, query: str, depth: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO jobs (job_id, status, query, depth, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (job_id, "queued", query, depth, datetime.now(timezone.utc).isoformat()),
        )
        await db.commit()


async def update_job(job_id: str, **kwargs):
    """Dynamically update any job fields."""
    if not kwargs:
        return
    fields = ", ".join(f"{k} = ?" for k in kwargs)
    values = list(kwargs.values()) + [job_id]
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"UPDATE jobs SET {fields} WHERE job_id = ?", values)
        await db.commit()


async def get_job(job_id: str) -> Optional[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def get_all_jobs(limit: int = 20) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM jobs ORDER BY created_at DESC LIMIT ?", (limit,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]
