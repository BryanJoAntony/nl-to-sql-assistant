from flask import g, jsonify


def get_request_id() -> str:
    return getattr(g, "request_id", "unknown")


def success_response(
    data: dict | None = None,
    message: str = "Success",
    status_code: int = 200,
):
    return jsonify(
        {
            "success": True,
            "request_id": get_request_id(),
            "message": message,
            "data": data or {},
        }
    ), status_code


def error_response(
    message: str,
    status_code: int = 400,
    error_code: str = "ERROR",
    details: dict | None = None,
):
    return jsonify(
        {
            "success": False,
            "request_id": get_request_id(),
            "message": message,
            "error_code": error_code,
            "details": details or {},
        }
    ), status_code