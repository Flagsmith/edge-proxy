import os
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi import FastAPI

DEFAULT_SERVICE_NAME = "flagsmith-edge-proxy"
_TRACER_NAME = "edge_proxy"

_telemetry_setup: "TelemetrySetup | None" = None


@dataclass(frozen=True)
class TelemetrySetup:
    enabled: bool


def is_otel_enabled() -> bool:
    if os.environ.get("OTEL_SDK_DISABLED", "").lower() == "true":
        return False
    if os.environ.get("OTEL_TRACES_EXPORTER", "otlp").lower() == "none":
        return False
    return bool(os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT"))


def setup_telemetry() -> TelemetrySetup:
    global _telemetry_setup
    if _telemetry_setup is not None:
        return _telemetry_setup

    if not is_otel_enabled():
        _telemetry_setup = TelemetrySetup(enabled=False)
        return _telemetry_setup

    from opentelemetry import trace
    from opentelemetry.baggage.propagation import W3CBaggagePropagator
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
        OTLPSpanExporter as GrpcOTLPSpanExporter,
    )
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
        OTLPSpanExporter as HttpOTLPSpanExporter,
    )
    from opentelemetry.propagate import set_global_textmap
    from opentelemetry.propagators.composite import CompositePropagator
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.semconv.resource import ResourceAttributes
    from opentelemetry.trace.propagation.tracecontext import (
        TraceContextTextMapPropagator,
    )

    service_name = os.environ.get("OTEL_SERVICE_NAME", DEFAULT_SERVICE_NAME)
    resource = Resource.create(
        {ResourceAttributes.SERVICE_NAME: service_name},
    )
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)

    protocol = os.environ.get("OTEL_EXPORTER_OTLP_PROTOCOL", "http/protobuf")
    if protocol == "grpc":
        exporter = GrpcOTLPSpanExporter()
    else:
        exporter = HttpOTLPSpanExporter()

    provider.add_span_processor(BatchSpanProcessor(exporter))
    set_global_textmap(
        CompositePropagator(
            [TraceContextTextMapPropagator(), W3CBaggagePropagator()],
        ),
    )

    _telemetry_setup = TelemetrySetup(enabled=True)
    return _telemetry_setup


class _NoOpSpan:
    def set_attribute(self, *args, **kwargs) -> None:
        pass

    def record_exception(self, *args, **kwargs) -> None:
        pass


class _NoOpSpanContext:
    def __enter__(self) -> _NoOpSpan:
        return _NoOpSpan()

    def __exit__(self, *args) -> None:
        pass


class _NoOpTracer:
    def start_as_current_span(self, name: str) -> _NoOpSpanContext:
        return _NoOpSpanContext()


_no_op_tracer = _NoOpTracer()


def get_tracer():
    if not is_otel_enabled():
        return _no_op_tracer

    setup_telemetry()
    from opentelemetry import trace

    return trace.get_tracer(_TRACER_NAME)


def instrument_fastapi(app: "FastAPI", excluded_urls: str | None = None) -> None:
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

    FastAPIInstrumentor.instrument_app(app, excluded_urls=excluded_urls)


def instrument_httpx() -> None:
    from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

    HTTPXClientInstrumentor().instrument()


def add_otel_trace_context(
    logger: object,
    method_name: str,
    event_dict: dict,
) -> dict:
    if not is_otel_enabled():
        return event_dict

    from opentelemetry import trace

    span = trace.get_current_span()
    if not span or not span.is_recording():
        return event_dict

    ctx = span.get_span_context()
    event_dict["trace_id"] = format(ctx.trace_id, "032x")
    event_dict["span_id"] = format(ctx.span_id, "016x")
    return event_dict
