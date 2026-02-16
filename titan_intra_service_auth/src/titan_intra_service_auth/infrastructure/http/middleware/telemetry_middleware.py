# -*- coding: utf-8 -*-
"""
Telemetry middleware: records request/response and latency via MetricsPort (from app.state).
Never rejects; single lock section on entry and exit. Minimal work under lock.
Elias Andrade — Replika AI Solutions
"""

import time
import uuid
from typing import Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class TelemetryMiddleware(BaseHTTPMiddleware):
    """Reads MetricsPort from request.app.state.metrics (set in create_app)."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        metrics = getattr(request.app.state, "metrics", None)
        if not metrics:
            return await call_next(request)
        rid = str(uuid.uuid4())[:8]
        t_start = time.perf_counter()
        metrics.increment_active_connections()
        try:
            response = await call_next(request)
            sc = response.status_code
            duration_ms = (time.perf_counter() - t_start) * 1000
            status_class = "2xx" if sc < 400 else ("4xx" if sc < 500 else "5xx")
            metrics.record_http_request(status_class=status_class, latency_ms=duration_ms)
            metrics.decrement_active_connections()
            if response.headers.get("x-request-id") is None:
                response.headers["X-Request-ID"] = rid
            if "X-Engine-Lat" not in response.headers:
                response.headers["X-Engine-Lat"] = f"{duration_ms:.2f}ms"
            return response
        except Exception:
            metrics.record_http_request(status_class="5xx", latency_ms=(time.perf_counter() - t_start) * 1000)
            metrics.decrement_active_connections()
            raise


