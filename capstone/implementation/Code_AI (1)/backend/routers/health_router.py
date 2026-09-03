from fastapi import APIRouter
from backend.config import settings

router = APIRouter(prefix="/api/v1")


@router.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "env": settings.ENV,
        "debug": settings.DEBUG,
    }
