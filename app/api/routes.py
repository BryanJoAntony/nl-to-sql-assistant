from flask import Flask

from app.api.health_controller import health_blueprint
from app.api.history_controller import history_blueprint
from app.api.info_controller import info_blueprint
from app.api.query_controller import query_blueprint
from app.core.config import settings
from app.core.rate_limiter import limiter


def register_routes(app: Flask) -> None:
    app.register_blueprint(health_blueprint, url_prefix="/api")
    app.register_blueprint(query_blueprint, url_prefix="/api")
    app.register_blueprint(history_blueprint, url_prefix="/api")
    app.register_blueprint(info_blueprint, url_prefix="/api")

    @app.route("/health", methods=["GET"])
    @limiter.exempt
    def root_health():
        return {
            "success": True,
            "service": settings.APP_NAME,
            "status": "ok",
        }