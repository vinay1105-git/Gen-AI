import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from backend.models import Base
from backend.services.user_service import UserService


@pytest.mark.asyncio
async def test_create_and_authenticate_user():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    AsyncSessionLocal = sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
    async with AsyncSessionLocal() as session:
        user = await UserService.create_user(session, "test@example.com", "Test User", "password123")
        assert user.email == "test@example.com"
        assert user.id is not None

        authenticated = await UserService.authenticate_user(session, "test@example.com", "password123")
        assert authenticated is not None
        assert authenticated.email == "test@example.com"

