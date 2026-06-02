from functools import wraps

from flask import request

from app.core.config import settings
from app.core.exceptions import UnauthorizedException


def require_api_key(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not settings.ENABLE_API_KEY_AUTH:
            return func(*args, **kwargs)

        provided_key = request.headers.get("X-API-Key")

        if not provided_key or provided_key != settings.APP_API_KEY:
            raise UnauthorizedException("Invalid or missing API key")

        return func(*args, **kwargs)

    return wrapper