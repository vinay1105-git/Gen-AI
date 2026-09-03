from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"
DATABASE_DIR = BASE_DIR / "database"
REPORT_DIR = BASE_DIR / "reports"
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"
UPLOAD_DIR = BASE_DIR / "uploads"
EXPORT_DIR = BASE_DIR / "exports"
for directory in (LOG_DIR, DATABASE_DIR, REPORT_DIR, STATIC_DIR, TEMPLATES_DIR, UPLOAD_DIR, EXPORT_DIR):
    directory.mkdir(parents=True, exist_ok=True)


class Settings(BaseSettings):
    APP_NAME: str = "Code AI - LLM-Based Multi-Agent Code Generation, Review, and Vulnerability Explanation System"
    APP_VERSION: str = "2.0.0"
    ENV: str = "development"
    DEBUG: bool = True
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    API_PREFIX: str = "/api/v1"
    LOG_LEVEL: str = "INFO"

    DATABASE_URL: str = "sqlite+aiosqlite:///./database/app.db"

    JWT_SECRET_KEY: str = "change-this-development-secret"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Local LLM deployment — no cloud API key required.
    OLLAMA_ENABLED: bool = True
    OLLAMA_HOST: str = "http://127.0.0.1:11434"
    OLLAMA_MODEL: str = "llama3.2:latest"
    LOCAL_LLM_MODEL: str = "llama3.2:latest"

    MAX_TOKENS: int = 1024
    TEMPERATURE: float = 0.2
    TOP_P: float = 0.9

    ENABLE_PDF_REPORTS: bool = False
    ENABLE_MARKDOWN_EXPORT: bool = True
    ENABLE_HTML_EXPORT: bool = False
    ENABLE_BANDIT_SCAN: bool = True
    ENABLE_COMPLEXITY_ANALYSIS: bool = True
    ENABLE_CODE_REVIEW: bool = True
    ENABLE_REQUEST_LOGGING: bool = True
    ENABLE_RESPONSE_LOGGING: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


settings = Settings()
