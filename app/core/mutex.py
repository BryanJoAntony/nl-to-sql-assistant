import os
import sys
from pathlib import Path

from app.core.config import settings
from app.core.logger import app_logger


LOCK_FILE: Path = settings.BASE_DIR / ".app.lock"


def enforce_single_instance() -> None:
    if not settings.ENABLE_MUTEX:
        app_logger.info("Mutex disabled")
        return

    if LOCK_FILE.exists():
        app_logger.error("Application lock file already exists: %s", LOCK_FILE)
        sys.exit(1)

    LOCK_FILE.write_text(str(os.getpid()), encoding="utf-8")
    app_logger.info("Application lock file created: %s", LOCK_FILE)


def release_single_instance() -> None:
    if LOCK_FILE.exists():
        LOCK_FILE.unlink()
        app_logger.info("Application lock file released")