from flask import Blueprint, request

from app.core.security import require_api_key
from app.db.connection import get_db_connection
from app.utils.response_utils import success_response


history_blueprint = Blueprint("history", __name__)


@history_blueprint.route("/query-history", methods=["GET"])
@require_api_key
def get_query_history():
    limit = request.args.get("limit", default=20, type=int)

    if limit <= 0:
        limit = 20

    if limit > 100:
        limit = 100

    conn = get_db_connection()

    rows = conn.execute(
        """
        SELECT
            query_history_id,
            question,
            generated_sql,
            final_sql,
            explanation,
            confidence,
            dry_run,
            was_blocked,
            blocked_reason,
            row_count,
            execution_time_ms,
            created_on
        FROM query_history
        ORDER BY query_history_id DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()

    conn.close()

    history = [dict(row) for row in rows]

    return success_response(
        message="Query history fetched successfully",
        data={
            "items": history,
            "count": len(history),
            "limit": limit,
        },
    )