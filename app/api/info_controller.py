from flask import Blueprint

from app.core.config import settings
from app.core.rate_limiter import limiter
from app.utils.response_utils import success_response


info_blueprint = Blueprint("info", __name__)


@info_blueprint.route("/info", methods=["GET"])
@limiter.exempt
def api_info():
    return success_response(
        message="Service information fetched successfully",
        data={
            "service": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.APP_ENV,
            "database": "SQLite",
            "llm_provider": "OpenAI",
            "openai_model": settings.OPENAI_MODEL,
            "safety_mode": "strict",
            "rate_limiting_enabled": settings.ENABLE_RATE_LIMITING,
            "api_key_auth_enabled": settings.ENABLE_API_KEY_AUTH,
            "max_query_rows": settings.MAX_QUERY_ROWS,
            "max_query_seconds": settings.MAX_QUERY_SECONDS,
        },
    )