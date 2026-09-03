import logging
from logging.handlers import RotatingFileHandler

from backend.config import LOG_DIR, settings


def configure_logging() -> None:
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s"
    )
    handler = RotatingFileHandler(
        LOG_DIR / "app.log", maxBytes=5_000_000, backupCount=5
    )
    handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.setLevel(settings.LOG_LEVEL)
    logger.addHandler(handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
