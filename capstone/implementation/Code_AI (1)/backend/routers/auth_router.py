import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.db import get_db
from backend.schemas.user_schemas import (
    UserCreate,
    UserLogin,
    TokenResponse,
    UserResponse,
)
from backend.services.user_service import UserService
from backend.security.auth import create_access_token

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"],
)


@router.post("/signup", response_model=UserResponse)
async def signup(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    existing = await UserService.get_user_by_email(db, user_data.email)

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = await UserService.create_user(
        db,
        user_data.email,
        user_data.name,
        user_data.password,
    )

    return UserResponse.model_validate(user)


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    user = await UserService.authenticate_user(
        db,
        credentials.email,
        credentials.password,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    token = create_access_token(subject=user.email)

    return TokenResponse(access_token=token)