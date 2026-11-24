"""Privacy-conscious request logging and optional local OpenTelemetry spans.

Only route templates, response status, duration and generated request IDs are
recorded. Never log request bodies, query parameters, headers or credentials.
"""
from __future__ import annotations

import json
import logging
import os
import sys
import time
from uuid import uuid4

from fastapi import Request
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor
from starlette.middleware.base import BaseHTTPMiddleware

LOGGER = logging.getLogger("analyznow.api")
if not LOGGER.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))
    LOGGER.addHandler(handler)
LOGGER.setLevel(logging.INFO)
LOGGER.propagate = False

_tracing_initialized = False


def configure_tracing() -> None:
    """Explicit opt-in for local console spans, never external transmission."""
    global _tracing_initialized
    if _tracing_initialized or os.getenv("ANALYZNOW_TRACE_CONSOLE") != "1":
        return
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
    trace.set_tracer_provider(provider)
    _tracing_initialized = True


def safe_route(request: Request) -> str:
    """Use route templates, not raw URL paths that might include private data."""
    route = request.scope.get("route")
    template = getattr(route, "path", None)
    return template if isinstance(template, str) and template.startswith("/") else "<unmatched>"


class RequestObservabilityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = uuid4().hex
        started = time.perf_counter()
        response = None
        status = 500
        tracer = trace.get_tracer("analyznow.api")
        try:
            with tracer.start_as_current_span("http.request") as span:
                span.set_attribute("http.request.method", request.method)
                try:
                    response = await call_next(request)
                    status = response.status_code
                    return response
                except Exception:
                    span.record_exception(Exception("Unhandled API exception"))
                    raise
                finally:
                    route = safe_route(request)
                    elapsed = round((time.perf_counter() - started) * 1000, 2)
                    span.set_attribute("http.route", route)
                    span.set_attribute("http.response.status_code", status)
                    LOGGER.info(json.dumps({
                        "event": "http_request",
                        "request_id": request_id,
                        "method": request.method,
                        "route": route,
                        "status_code": status,
                        "duration_ms": elapsed,
                    }, separators=(",", ":")))
        finally:
            if response is not None:
                response.headers["X-Request-ID"] = request_id
