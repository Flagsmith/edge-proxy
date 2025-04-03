import time
from typing import Any, Callable

import structlog
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = structlog.get_logger("edge_proxy.request")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Log all incoming HTTP requests and responses with timing information.
    """

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Any]
    ) -> Any:
        start_time = time.time()

        logger.debug(
            "request",
            method=request.method,
            url=request.url.path,
            client_host=request.client.host if request.client else None,
        )

        response = await call_next(request)

        duration = time.time() - start_time

        logger.debug(
            "response",
            method=request.method,
            url=request.url.path,
            status_code=response.status_code,
            size=int(response.headers.get("content-length", 0)),
            duration_ms=round(duration * 1000),
        )

        return response
