from flask import Blueprint, request

from app.core.config import settings
from app.core.rate_limiter import limiter
from app.core.security import require_api_key
from app.core.service_container import service_container
from app.schemas.request_schema import QueryRequest
from app.utils.response_utils import error_response, success_response


query_blueprint = Blueprint("query", __name__)


@query_blueprint.route("/query", methods=["POST"])
@require_api_key
@limiter.limit(lambda: settings.RATE_LIMIT_QUERY)
def query_database():
    payload = QueryRequest(**request.get_json())

    result = service_container.nl_to_sql_service.process_question(
        question=payload.question,
        dry_run=payload.dry_run,
    )

    if result["safety"]["blocked"]:
        return error_response(
            message="Request blocked by safety controls",
            status_code=400,
            error_code="REQUEST_BLOCKED_BY_SAFETY",
            details=result,
        )

    return success_response(
        message="Query processed successfully",
        data=result,
    )