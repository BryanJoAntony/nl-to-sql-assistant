from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from app.core.config import settings
from app.core.logger import app_logger


limiter = Limiter(
    key_func=get_remote_address,
    enabled=settings.ENABLE_RATE_LIMITING,
    storage_uri=settings.RATE_LIMIT_STORAGE_URI,
    default_limits=[settings.RATE_LIMIT_DEFAULT],
)


def register_rate_limiter(app: Flask) -> None:
    limiter.init_app(app)

    app_logger.info(
        "Rate limiter registered | enabled=%s | storage_uri=%s | default_limit=%s",
        settings.ENABLE_RATE_LIMITING,
        settings.RATE_LIMIT_STORAGE_URI,
        settings.RATE_LIMIT_DEFAULT,
    )