import atexit

from app.core.config import settings
from app.core.exceptions import ConfigurationException
from app.core.logger import app_logger
from app.core.mutex import enforce_single_instance, release_single_instance
from app.db.init_db import setup_database


def run_preflight_checks() -> None:
    app_logger.info("Running preflight checks")

    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.logs_dir.mkdir(parents=True, exist_ok=True)

    if settings.MAX_QUERY_ROWS <= 0:
        raise ConfigurationException("MAX_QUERY_ROWS must be greater than 0")

    if settings.MAX_QUERY_SECONDS <= 0:
        raise ConfigurationException("MAX_QUERY_SECONDS must be greater than 0")

    if settings.ENABLE_API_KEY_AUTH and not settings.APP_API_KEY:
        raise ConfigurationException(
            "APP_API_KEY is required when ENABLE_API_KEY_AUTH=True"
        )

    if not settings.OPENAI_API_KEY:
        app_logger.warning(
            "OPENAI_API_KEY is not configured. OpenAI SQL generation will fail until configured."
        )

    if settings.ENABLE_RATE_LIMITING and not settings.RATE_LIMIT_STORAGE_URI:
        raise ConfigurationException(
            "RATE_LIMIT_STORAGE_URI is required when ENABLE_RATE_LIMITING=True"
        )

    if settings.ENABLE_RATE_LIMITING and not settings.RATE_LIMIT_QUERY:
        raise ConfigurationException(
            "RATE_LIMIT_QUERY is required when ENABLE_RATE_LIMITING=True"
        )
    app_logger.info("Preflight checks completed")


def run_postflight_checks() -> None:
    app_logger.info("Running postflight checks")

    if not settings.database_full_path.exists():
        raise ConfigurationException("Database file was not created successfully")

    app_logger.info("Postflight checks completed")


def run_startup_checks() -> None:
    enforce_single_instance()
    atexit.register(release_single_instance)

    run_preflight_checks()
    setup_database()
    run_postflight_checks()