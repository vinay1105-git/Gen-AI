import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.models import User
from backend.security.auth import get_password_hash, verify_password

logger = logging.getLogger(__name__)


class UserService:
    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
        result = await db.execute(select(User).filter(User.email == email))
        return result.scalars().first()

    @staticmethod
    async def create_user(db: AsyncSession, email: str, name: str, password: str, role: str = "user") -> User:
        hashed_password = get_password_hash(password)
        user = User(email=email, name=name, hashed_password=hashed_password, role=role)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        logger.info("Created user %s", email)
        return user

    @staticmethod
    async def authenticate_user(db: AsyncSession, email: str, password: str) -> User | None:
        user = await UserService.get_user_by_email(db, email)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user
