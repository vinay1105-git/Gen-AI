import logging
from contextlib import asynccontextmanager

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from backend.config import settings
from backend.models import Base

logger = logging.getLogger(__name__)

DATABASE_URL = settings.DATABASE_URL

# ==========================================================
# Database Engine
# ==========================================================

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# ==========================================================
# Session Factory
# ==========================================================

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

# ==========================================================
# Dependency
# ==========================================================

async def get_db():

    async with AsyncSessionLocal() as session:

        try:

            yield session

        finally:

            await session.close()

# ==========================================================
# Context Manager
# ==========================================================

@asynccontextmanager
async def get_db_session():

    async with AsyncSessionLocal() as session:

        try:

            yield session

            await session.commit()

        except Exception:

            await session.rollback()

            raise

        finally:

            await session.close()

# ==========================================================
# Database Initialization
# ==========================================================

async def init_db():

    logger.info("=" * 60)
    logger.info("Initializing Database")

    async with engine.begin() as conn:

        await conn.run_sync(Base.metadata.create_all)

    logger.info("Database Initialized Successfully")

# ==========================================================
# Health Check
# ==========================================================

async def check_database_connection() -> bool:

    try:

        async with engine.connect() as connection:

            await connection.execute(
                text("SELECT 1")
            )

        logger.info("Database Connection Successful")

        return True

    except Exception as e:

        logger.exception(e)

        return False

# ==========================================================
# Close Engine
# ==========================================================

async def close_database():

    logger.info("Closing Database Engine")

    await engine.dispose()

    logger.info("Database Engine Closed")