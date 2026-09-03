import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config import settings
from backend.database import init_db
from backend.routers.agent_router import router as agent_router
from backend.routers.auth_router import router as auth_router
from backend.routers.health_router import router as health_router
from backend.utils.logger import configure_logging
from backend.utils.llm_installer import detect_ram_gb

configure_logging()
logger = logging.getLogger(__name__)


# =====================================================
# Application Lifespan
# =====================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info("=" * 60)
    logger.info("Starting %s", settings.APP_NAME)

    try:
        await init_db()
        logger.info("Database initialized successfully")

        # Log local LLM availability and RAM recommendations
        try:
            from backend.services.agent_service import orchestrator
            ollama_ok = orchestrator.llm_engine.ollama.health()
            ram = detect_ram_gb()
            if ollama_ok:
                logger.info("Local Ollama detected at %s", settings.OLLAMA_HOST)
                logger.info("Installed Ollama models: %s", orchestrator.llm_engine.available_models())
            else:
                logger.warning("Ollama is not reachable at %s", settings.OLLAMA_HOST)

            logger.info("Detected system RAM: %s GB", ram)
        except Exception:
            pass

    except Exception:
        logger.exception("Database initialization failed")
        raise

    logger.info("Application started successfully")
    logger.info("=" * 60)

    yield

    logger.info("=" * 60)
    logger.info("Stopping %s", settings.APP_NAME)
    logger.info("=" * 60)


# =====================================================
# FastAPI Application
# =====================================================

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
# LLM Multi-Agent Software Engineering Platform

- Code Generation
- Code Review
- Vulnerability Detection
- Code Explanation
- Test Case Generation
- Multi-Agent Collaboration
""",
    debug=settings.DEBUG,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


# =====================================================
# CORS
# =====================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else ["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================================================
# Logging Middleware
# =====================================================

@app.middleware("http")
async def log_requests(request: Request, call_next):

    start = time.perf_counter()

    response = await call_next(request)

    process_time = round((time.perf_counter() - start) * 1000, 2)

    logger.info(
        "%s %s | %s | %.2f ms",
        request.method,
        request.url.path,
        response.status_code,
        process_time,
    )

    response.headers["X-Process-Time"] = str(process_time)

    return response


# =====================================================
# Routers
# =====================================================

app.include_router(
    health_router,
    tags=["Health"],
)

app.include_router(
    auth_router,
    prefix="/api/auth",
    tags=["Authentication"],
)

# IMPORTANT:
# agent_router already has:
# prefix="/api/v1/agents"
# Do NOT add another prefix here.

app.include_router(
    agent_router,
)


# =====================================================
# Validation Handler
# =====================================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "Validation Failed",
            "errors": exc.errors(),
            "body": exc.body,
        },
    )


# =====================================================
# Global Exception Handler
# =====================================================

@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception,
):

    logger.exception(exc)

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal Server Error",
            "detail": str(exc) if settings.DEBUG else "Unexpected server error",
        },
    )


# =====================================================
# Root Endpoint
# =====================================================

@app.get("/", tags=["System"])
async def root():

    return {
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "Running",
        "docs": "/docs",
        "health": "/health",
    }