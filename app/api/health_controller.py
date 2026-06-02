from flask import Blueprint

from app.core.config import settings
from app.db.connection import get_db_connection
from app.db.schema import ALLOWED_SCHEMA
from app.utils.response_utils import success_response
from app.core.rate_limiter import limiter

health_blueprint = Blueprint("health", __name__)


@health_blueprint.route("/health", methods=["GET"])
@limiter.exempt
def api_health():
    return success_response(
        message="API is healthy",
        data={
            "service": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.APP_ENV,
            "status": "ok",
        },
    )


@health_blueprint.route("/ready", methods=["GET"])
@limiter.exempt
def api_ready():
    checks = {
        "database": "unknown",
        "openai_api_key": "configured" if settings.OPENAI_API_KEY else "missing",
        "allowed_schema": "loaded" if ALLOWED_SCHEMA else "missing",
    }

    try:
        conn = get_db_connection()
        conn.execute("SELECT 1")
        conn.close()
        checks["database"] = "ok"
    except Exception:
        checks["database"] = "failed"

    is_ready = checks["database"] == "ok" and checks["allowed_schema"] == "loaded"

    return success_response(
        message="Service readiness checked",
        data={
            "service": settings.APP_NAME,
            "status": "ready" if is_ready else "not_ready",
            "checks": checks,
        },
        status_code=200 if is_ready else 503,
    )