import asyncio
import logging

from backend.database.db import (
    check_database_connection,
    close_database,
    engine,
)
from backend.models import Base

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


async def create_tables():

    logger.info("=" * 60)
    logger.info("Creating Database Tables")

    async with engine.begin() as conn:

        await conn.run_sync(Base.metadata.create_all)

    logger.info("Tables Created Successfully")


async def initialize_database():

    logger.info("=" * 60)
    logger.info("Initializing Database")

    connected = await check_database_connection()

    if not connected:

        logger.error("Database Connection Failed")

        return

    await create_tables()

    logger.info("Database Initialization Completed")


async def main():

    try:

        await initialize_database()

    except Exception as e:

        logger.exception("Database Initialization Failed")

        logger.exception(e)

    finally:

        await close_database()


if __name__ == "__main__":

    asyncio.run(main())