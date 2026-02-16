# -*- coding: utf-8 -*-
"""
Port: MetricsPort (Interface for observability).
Application records mint/success/failure and HTTP metrics via this abstraction.
Elias Andrade — Replika AI Solutions
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class MetricsPort(ABC):
    """
    Interface for recording metrics. Implementations: shared memory adapter, etc.
    Methods kept minimal (ISP).
    """

    @abstractmethod
    def record_http_request(self, status_class: str, latency_ms: float) -> None:
        """Record an HTTP request (2xx/4xx/5xx) and latency."""
        ...

    @abstractmethod
    def record_mint(self, user: str, jti: str) -> None:
        """Record a successful token mint."""
        ...

    @abstractmethod
    def record_mint_failure(self) -> None:
        """Record a failed mint attempt (e.g. validation error)."""
        ...

    @abstractmethod
    def get_snapshot(self) -> Dict[str, Any]:
        """Return a read-only snapshot of current metrics (for /stats endpoint)."""
        ...

    @abstractmethod
    def increment_active_connections(self) -> int:
        """Increment active connections; return new total (for middleware)."""
        ...

    @abstractmethod
    def decrement_active_connections(self) -> None:
        """Decrement active connections (on response or error)."""
        ...
