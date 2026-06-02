import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.core.config import settings


LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

settings.logs_dir.mkdir(parents=True, exist_ok=True)


def _create_file_handler(log_file: Path, level: int) -> RotatingFileHandler:
    handler = RotatingFileHandler(
        log_file,
        maxBytes=2_000_000,
        backupCount=5,
        encoding="utf-8",
    )
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
    return handler


def _create_console_handler(level: int = logging.INFO) -> logging.StreamHandler:
    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
    return handler


def _create_logger(name: str, file_name: str, level: int) -> logging.Logger:
    logger_instance = logging.getLogger(name)
    logger_instance.setLevel(level)
    logger_instance.propagate = False

    if not logger_instance.handlers:
        logger_instance.addHandler(
            _create_file_handler(settings.logs_dir / file_name, level)
        )

    return logger_instance


app_logger = _create_logger("safe_nl_sql.app", "app.log", logging.INFO)
request_logger = _create_logger("safe_nl_sql.requests", "requests.log", logging.INFO)
error_logger = _create_logger("safe_nl_sql.errors", "errors.log", logging.ERROR)
sql_logger = _create_logger("safe_nl_sql.sql", "sql.log", logging.INFO)
output_logger = _create_logger("safe_nl_sql.outputs", "outputs.log", logging.INFO)
openai_logger = _create_logger("safe_nl_sql.openai", "openai.log", logging.INFO)

if not any(isinstance(handler, logging.StreamHandler) for handler in app_logger.handlers):
    app_logger.addHandler(_create_console_handler())

logger = app_logger