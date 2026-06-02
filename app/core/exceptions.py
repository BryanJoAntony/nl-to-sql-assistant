class AppException(Exception):
    status_code = 500
    error_code = "APP_ERROR"

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        error_code: str | None = None,
        details: dict | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code or self.status_code
        self.error_code = error_code or self.error_code
        self.details = details or {}


class BadRequestException(AppException):
    status_code = 400
    error_code = "BAD_REQUEST"


class UnauthorizedException(AppException):
    status_code = 401
    error_code = "UNAUTHORIZED"


class ConfigurationException(AppException):
    status_code = 500
    error_code = "CONFIGURATION_ERROR"


class DatabaseException(AppException):
    status_code = 500
    error_code = "DATABASE_ERROR"


class SQLValidationException(AppException):
    status_code = 400
    error_code = "SQL_VALIDATION_FAILED"


class OpenAIServiceException(AppException):
    status_code = 502
    error_code = "OPENAI_SERVICE_ERROR"