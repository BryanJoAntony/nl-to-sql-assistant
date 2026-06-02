import time
import uuid

from flask import Flask, g, request

from app.core.logger import error_logger, output_logger, request_logger


def register_request_logging(app: Flask) -> None:
    @app.before_request
    def before_request():
        g.request_id = str(uuid.uuid4())
        g.start_time = time.time()

        request_logger.info(
            "REQUEST_STARTED | request_id=%s | method=%s | path=%s | remote_addr=%s",
            g.request_id,
            request.method,
            request.path,
            request.remote_addr,
        )

    @app.after_request
    def after_request(response):
        duration_ms = round((time.time() - g.start_time) * 1000, 2)

        output_logger.info(
            "REQUEST_COMPLETED | request_id=%s | method=%s | path=%s | status=%s | duration_ms=%s",
            g.request_id,
            request.method,
            request.path,
            response.status_code,
            duration_ms,
        )

        response.headers["X-Request-ID"] = g.request_id
        return response

    @app.teardown_request
    def teardown_request(exception):
        if exception:
            error_logger.exception(
                "REQUEST_FAILED | request_id=%s | method=%s | path=%s",
                getattr(g, "request_id", "unknown"),
                request.method,
                request.path,
            )