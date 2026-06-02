from app import create_app
from app.core.config import settings
from app.core.logger import app_logger
from app.core.startup import run_startup_checks


app = create_app()


if __name__ == "__main__":
    run_startup_checks()

    app_logger.info("Starting %s", settings.APP_NAME)
    app_logger.info(
        "Server running on http://%s:%s",
        settings.FLASK_HOST,
        settings.FLASK_PORT,
    )

    app.run(
        host=settings.FLASK_HOST,
        port=settings.FLASK_PORT,
        debug=settings.FLASK_DEBUG,
    )