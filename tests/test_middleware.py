import json

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture

from edge_proxy.middleware import RequestLoggingMiddleware


def test_request_logging_middleware(mocker: MockerFixture) -> None:
    # Given
    mock_logger = mocker.patch("edge_proxy.middleware.logger")

    app = FastAPI()
    app.add_middleware(RequestLoggingMiddleware)
    response = "ok"

    @app.get("/test")
    async def test_endpoint():
        return response

    client = TestClient(app)

    # When
    client.get("/test")

    # Then
    mock_logger.debug.assert_any_call(
        "request",
        method="GET",
        url="/test",
        client_host="testclient",
    )
    mock_logger.debug.assert_any_call(
        "response",
        method="GET",
        url="/test",
        status_code=200,
        size=len(json.dumps(response)),
        duration_ms=mocker.ANY,
    )
