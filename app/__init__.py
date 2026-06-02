from flask import Flask

from app.api.routes import register_routes
from app.core.error_handlers import register_error_handlers
from app.core.logger import app_logger
from app.core.rate_limiter import register_rate_limiter
from app.core.request_logging import register_request_logging


def create_app() -> Flask:
    app = Flask(__name__)

    register_request_logging(app)
    register_error_handlers(app)
    register_rate_limiter(app)
    register_routes(app)

    app_logger.info("Flask application created successfully")

    return app