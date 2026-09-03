from backend.routers.auth_router import router as auth_router
from backend.routers.agent_router import router as agent_router
from backend.routers.health_router import router as health_router

__all__ = ["auth_router", "agent_router", "health_router"]
