from flask import Flask
from pydantic import ValidationError
from werkzeug.exceptions import TooManyRequests

from app.core.exceptions import AppException
from app.core.logger import error_logger
from app.utils.response_utils import error_response


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(AppException)
    def handle_app_exception(exc: AppException):
        error_logger.error(
            "APP_EXCEPTION | error_code=%s | message=%s | details=%s",
            exc.error_code,
            exc.message,
            exc.details,
        )

        return error_response(
            message=exc.message,
            status_code=exc.status_code,
            error_code=exc.error_code,
            details=exc.details,
        )

    @app.errorhandler(ValidationError)
    def handle_validation_error(exc: ValidationError):
        error_logger.error("VALIDATION_ERROR | errors=%s", exc.errors())

        return error_response(
            message="Invalid request body",
            status_code=400,
            error_code="REQUEST_VALIDATION_ERROR",
            details={"errors": exc.errors()},
        )

    @app.errorhandler(TooManyRequests)
    def handle_rate_limit_error(exc: TooManyRequests):
        error_logger.warning("RATE_LIMIT_EXCEEDED | description=%s", exc.description)

        return error_response(
            message="Rate limit exceeded. Please try again later.",
            status_code=429,
            error_code="RATE_LIMIT_EXCEEDED",
            details={
                "description": exc.description,
            },
        )

    @app.errorhandler(Exception)
    def handle_unexpected_exception(exc: Exception):
        error_logger.exception("UNEXPECTED_EXCEPTION")

        return error_response(
            message="Internal server error",
            status_code=500,
            error_code="INTERNAL_SERVER_ERROR",
            details={},
        )