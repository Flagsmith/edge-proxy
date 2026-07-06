import pytest
import starlette.status
from fastapi import FastAPI
from fastapi.testclient import TestClient
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)
from pytest_mock import MockerFixture

from edge_proxy.environments import EnvironmentService
from edge_proxy.settings import AppSettings
from edge_proxy.telemetry import (
    add_otel_trace_context,
    get_tracer,
    is_otel_enabled,
    setup_telemetry,
)
from tests.fixtures.response_data import environment_1, environment_1_api_key


def _reset_tracer_provider_lock() -> None:
    import opentelemetry.trace as otel_trace

    otel_trace._TRACER_PROVIDER_SET_ONCE._done = False


@pytest.fixture
def reset_telemetry(monkeypatch: pytest.MonkeyPatch):
    import edge_proxy.telemetry as telemetry_module

    _reset_tracer_provider_lock()
    telemetry_module._telemetry_setup = None
    monkeypatch.delenv("OTEL_EXPORTER_OTLP_ENDPOINT", raising=False)
    monkeypatch.delenv("OTEL_SDK_DISABLED", raising=False)
    monkeypatch.delenv("OTEL_TRACES_EXPORTER", raising=False)
    monkeypatch.delenv("OTEL_TRACING_EXCLUDED_URL_PATHS", raising=False)
    yield
    _reset_tracer_provider_lock()
    telemetry_module._telemetry_setup = None


@pytest.fixture
def span_exporter(monkeypatch: pytest.MonkeyPatch, reset_telemetry):
    monkeypatch.setenv(
        "OTEL_EXPORTER_OTLP_ENDPOINT",
        "http://localhost:4318",
    )
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    _reset_tracer_provider_lock()
    trace.set_tracer_provider(provider)

    import edge_proxy.telemetry as telemetry_module

    telemetry_module._telemetry_setup = telemetry_module.TelemetrySetup(
        enabled=True,
    )

    yield exporter

    provider.force_flush()
    exporter.clear()


def test_is_otel_enabled_by_default(reset_telemetry):
    assert is_otel_enabled() is False
    assert setup_telemetry().enabled is False


def test_is_otel_disabled_when_sdk_disabled(
    monkeypatch: pytest.MonkeyPatch,
    reset_telemetry,
):
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318")
    monkeypatch.setenv("OTEL_SDK_DISABLED", "true")

    assert is_otel_enabled() is False


def test_is_otel_disabled_when_traces_exporter_none(
    monkeypatch: pytest.MonkeyPatch,
    reset_telemetry,
):
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318")
    monkeypatch.setenv("OTEL_TRACES_EXPORTER", "none")

    assert is_otel_enabled() is False


def test_setup_telemetry_enables_when_endpoint_set(
    monkeypatch: pytest.MonkeyPatch,
    reset_telemetry,
    mocker: MockerFixture,
):
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318")
    mocker.patch(
        "opentelemetry.sdk.trace.export.BatchSpanProcessor",
    )

    assert setup_telemetry().enabled is True


@pytest.mark.asyncio
async def test_refresh_environment_caches_creates_poll_spans(
    mocker: MockerFixture,
    span_exporter: InMemorySpanExporter,
):
    mock_client = mocker.AsyncMock()
    mock_client.get.return_value = mocker.Mock(
        status_code=200,
        text='{"updated_at": "2024-01-01T00:00:00"}',
    )
    settings = AppSettings(
        api_url="http://127.0.0.1:8000/api/v1",
        environment_key_pairs=[
            {
                "server_side_key": "ser.key1",
                "client_side_key": environment_1_api_key,
            },
        ],
    )
    environment_service = EnvironmentService(
        client=mock_client,
        settings=settings,
    )

    await environment_service.refresh_environment_caches()

    trace.get_tracer_provider().force_flush()
    span_names = [span.name for span in span_exporter.get_finished_spans()]
    assert "poll.refresh_environment_caches" in span_names
    assert "poll.fetch_document" in span_names


@pytest.mark.asyncio
async def test_fetch_document_304_sets_cache_hit_attribute(
    mocker: MockerFixture,
    span_exporter: InMemorySpanExporter,
):
    mock_client = mocker.AsyncMock()
    mock_client.get.return_value = mocker.Mock(
        status_code=starlette.status.HTTP_304_NOT_MODIFIED,
        text="",
    )
    settings = AppSettings(
        api_url="http://127.0.0.1:8000/api/v1",
        environment_key_pairs=[
            {
                "server_side_key": "ser.key1",
                "client_side_key": environment_1_api_key,
            },
        ],
    )
    environment_service = EnvironmentService(
        client=mock_client,
        settings=settings,
    )
    environment_service.cache.put_environment(
        environment_1_api_key,
        {**environment_1, "updated_at": "2024-01-01T00:00:00"},
    )

    await environment_service.refresh_environment_caches()

    trace.get_tracer_provider().force_flush()
    fetch_spans = [
        span
        for span in span_exporter.get_finished_spans()
        if span.name == "poll.fetch_document"
    ]
    assert len(fetch_spans) == 1
    attributes = dict(fetch_spans[0].attributes)
    assert attributes["flagsmith.cache_hit"] is True
    assert attributes["http.status_code"] == 304


def test_fastapi_instrumentation_creates_http_span(
    span_exporter: InMemorySpanExporter,
):
    from edge_proxy.telemetry import instrument_fastapi

    test_app = FastAPI()

    @test_app.get("/api/v1/flags/")
    async def flags():
        return {"flags": []}

    instrument_fastapi(test_app)

    client = TestClient(test_app)
    response = client.get("/api/v1/flags/")
    assert response.status_code == 200

    trace.get_tracer_provider().force_flush()
    http_spans = [
        span
        for span in span_exporter.get_finished_spans()
        if span.attributes.get("http.method") == "GET"
    ]
    assert http_spans
    assert http_spans[0].attributes.get("http.status_code") == 200


def test_health_liveness_excluded_from_tracing(
    monkeypatch: pytest.MonkeyPatch,
    span_exporter: InMemorySpanExporter,
):
    from edge_proxy.telemetry import instrument_fastapi

    monkeypatch.setenv(
        "OTEL_TRACING_EXCLUDED_URL_PATHS",
        "proxy/health/liveness",
    )

    test_app = FastAPI()

    @test_app.get("/proxy/health/liveness")
    async def liveness():
        return {"status": "ok"}

    instrument_fastapi(
        test_app,
        excluded_urls="proxy/health/liveness",
    )

    client = TestClient(test_app)
    response = client.get("/proxy/health/liveness")
    assert response.status_code == 200

    trace.get_tracer_provider().force_flush()
    assert not span_exporter.get_finished_spans()


def test_add_otel_trace_context_injects_ids(
    monkeypatch: pytest.MonkeyPatch,
    span_exporter: InMemorySpanExporter,
):
    tracer = get_tracer()
    with tracer.start_as_current_span("test.span"):
        event_dict = add_otel_trace_context(None, "", {"message": "test"})

    assert "trace_id" in event_dict
    assert "span_id" in event_dict
    assert len(event_dict["trace_id"]) == 32
    assert len(event_dict["span_id"]) == 16


def test_add_otel_trace_context_noop_when_disabled(reset_telemetry):
    event_dict = add_otel_trace_context(None, "", {"message": "test"})
    assert event_dict == {"message": "test"}


def test_setup_telemetry_uses_grpc_exporter(
    monkeypatch: pytest.MonkeyPatch,
    reset_telemetry,
    mocker: MockerFixture,
):
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_PROTOCOL", "grpc")
    mock_grpc_exporter = mocker.patch(
        "opentelemetry.exporter.otlp.proto.grpc.trace_exporter."
        "OTLPSpanExporter",
    )
    mocker.patch(
        "opentelemetry.sdk.trace.export.BatchSpanProcessor",
    )

    setup_telemetry()

    mock_grpc_exporter.assert_called_once()


def test_setup_telemetry_uses_http_exporter_by_default(
    monkeypatch: pytest.MonkeyPatch,
    reset_telemetry,
    mocker: MockerFixture,
):
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318")
    mock_http_exporter = mocker.patch(
        "opentelemetry.exporter.otlp.proto.http.trace_exporter."
        "OTLPSpanExporter",
    )
    mocker.patch(
        "opentelemetry.sdk.trace.export.BatchSpanProcessor",
    )

    setup_telemetry()

    mock_http_exporter.assert_called_once()
