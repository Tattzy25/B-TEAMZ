import asyncpg
import logging
from config import DATABASE_URL

logger = logging.getLogger(__name__)
db_pool = None

async def init_db_pool(min_size: int = 10, max_size: int = 50):
    global db_pool
    if not db_pool:
        try:
            db_pool = await asyncpg.create_pool(DATABASE_URL, min_size=min_size, max_size=max_size)
            logger.info("✅ Database connection pool created")
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise
    return db_pool

async def close_db_pool():
    global db_pool
    if db_pool:
        await db_pool.close()
        db_pool = None