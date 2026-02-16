# -*- coding: utf-8 -*-
"""
Adapter: SharedMetricsAdapter — implements MetricsPort using multiprocessing.Manager dict + Lock.
Buffer local para record_mint reduz IPC/lock entre processos (máxima performance).
Elias Andrade — Replika AI Solutions
"""

import threading
import time
from multiprocessing import Manager
from typing import Any, Dict

from titan_intra_service_auth.application.ports.metrics_port import MetricsPort

# Tamanho do buffer antes de flush no Manager (reduz contenção em multi-processo)
_MINT_FLUSH_THRESHOLD = 5


def _schema_dict(version: str, num_workers: int) -> Dict[str, Any]:
    """Schema base (DRY) para shared e local."""
    return {
        "engine_version": version,
        "engine_start_time": time.time(),
        "engine_status": "RUNNING",
        "active_workers": num_workers,
        "circuit_breaker": "CLOSED",
        "http_req_total": 0,
        "http_req_2xx": 0,
        "http_req_4xx": 0,
        "http_req_5xx": 0,
        "http_active_connections": 0,
        "lat_min": 0.0,
        "lat_max": 0.0,
        "lat_avg": 0.0,
        "lat_sum": 0.0,
        "sec_tokens_minted": 0,
        "sec_signatures": 0,
        "sec_blocked_attempts": 0,
        "sec_last_user": "none",
        "sec_last_jti": "none",
        "q_dropped_reqs": 0,
        "last_request_id": "none",
        "health_score": 100.0,
        "last_error": "none",
    }


def create_shared_metrics_schema(mgr: Manager, version: str, num_workers: int) -> Dict[str, Any]:
    """Creates the shared dict schema for telemetry (single source of truth, 1 worker)."""
    return mgr.dict(_schema_dict(version, num_workers))


def create_local_metrics_adapter(version: str, num_workers: int) -> "LocalMetricsAdapter":
    """Cria adapter de métricas por processo (multi-worker Windows, sem Manager)."""
    return LocalMetricsAdapter(version, num_workers)


def _do_flush_into(d: Dict[str, Any], lock: Any, n: int, u: str, j: str) -> None:
    """Atualiza dict sob lock com n mints (evita re-entrar em _local_lock)."""
    if n <= 0:
        return
    with lock:
        d["sec_tokens_minted"] = d["sec_tokens_minted"] + n
        d["sec_signatures"] = d["sec_signatures"] + n
        d["sec_last_user"] = u
        d["sec_last_jti"] = j


class LocalMetricsAdapter(MetricsPort):
    """
    Métricas por processo (sem Manager): cada worker tem seu próprio dict + Lock.
    Usado quando UVCORN_WORKERS > 1 no Windows (spawn não serializa Manager).
    Mesma interface que SharedMetricsAdapter; /stats reflete só este worker.
    SEM DEADLOCK: flush nunca adquire _local_lock de dentro de record_mint.
    """

    def __init__(self, version: str, num_workers: int) -> None:
        self._d = _schema_dict(version, num_workers)
        self._lock = threading.Lock()
        self._local_mint_buffer = 0
        self._local_lock = threading.Lock()
        self._last_user = "none"
        self._last_jti = "none"

    def _flush_mint_buffer(self) -> None:
        """Lê buffer sob _local_lock, depois atualiza dict (nunca segura os dois)."""
        with self._local_lock:
            n = self._local_mint_buffer
            u, j = self._last_user, self._last_jti
            self._local_mint_buffer = 0
        _do_flush_into(self._d, self._lock, n, u, j)

    def record_http_request(self, status_class: str, latency_ms: float) -> None:
        with self._lock:
            self._d["http_req_total"] = self._d["http_req_total"] + 1
            if status_class == "2xx":
                self._d["http_req_2xx"] = self._d["http_req_2xx"] + 1
            elif status_class == "4xx":
                self._d["http_req_4xx"] = self._d["http_req_4xx"] + 1
            else:
                self._d["http_req_5xx"] = self._d["http_req_5xx"] + 1
            self._d["lat_sum"] = self._d["lat_sum"] + latency_ms
            total = self._d["http_req_total"]
            self._d["lat_avg"] = self._d["lat_sum"] / total
            if latency_ms > self._d["lat_max"]:
                self._d["lat_max"] = latency_ms
            if self._d["lat_min"] == 0 or latency_ms < self._d["lat_min"]:
                self._d["lat_min"] = latency_ms
            if self._d["http_active_connections"] < 5000:
                self._d["circuit_breaker"] = "CLOSED"

    def record_mint(self, user: str, jti: str) -> None:
        need_flush = False
        n, u, j = 0, "none", "none"
        with self._local_lock:
            self._local_mint_buffer += 1
            self._last_user = user
            self._last_jti = jti
            if self._local_mint_buffer >= _MINT_FLUSH_THRESHOLD:
                n = self._local_mint_buffer
                u, j = self._last_user, self._last_jti
                self._local_mint_buffer = 0
                need_flush = True
        if need_flush:
            _do_flush_into(self._d, self._lock, n, u, j)

    def record_mint_failure(self) -> None:
        with self._lock:
            self._d["sec_blocked_attempts"] = self._d["sec_blocked_attempts"] + 1

    def get_snapshot(self) -> Dict[str, Any]:
        self._flush_mint_buffer()
        with self._lock:
            return dict(self._d)

    def increment_active_connections(self) -> int:
        with self._lock:
            self._d["http_active_connections"] = self._d["http_active_connections"] + 1
            active = self._d["http_active_connections"]
            if active > 18000:
                self._d["circuit_breaker"] = "UNDER_LOAD"
            return active

    def decrement_active_connections(self) -> None:
        with self._lock:
            self._d["http_active_connections"] = self._d["http_active_connections"] - 1


class SharedMetricsAdapter(MetricsPort):
    """
    Implementa MetricsPort com memória compartilhada (Manager).
    Buffer local para record_mint: acumula N mints e faz um único flush (menos lock/IPC).
    SEM DEADLOCK: flush nunca adquire _local_lock de dentro de record_mint.
    """

    def __init__(self, shared_dict: Dict[str, Any], lock: Any) -> None:
        self._d = shared_dict
        self._lock = lock
        self._local_mint_buffer = 0
        self._local_lock = threading.Lock()
        self._last_user = "none"
        self._last_jti = "none"

    def _flush_mint_buffer(self) -> None:
        with self._local_lock:
            n = self._local_mint_buffer
            u, j = self._last_user, self._last_jti
            self._local_mint_buffer = 0
        _do_flush_into(self._d, self._lock, n, u, j)

    def record_http_request(self, status_class: str, latency_ms: float) -> None:
        with self._lock:
            self._d["http_req_total"] = self._d["http_req_total"] + 1
            if status_class == "2xx":
                self._d["http_req_2xx"] = self._d["http_req_2xx"] + 1
            elif status_class == "4xx":
                self._d["http_req_4xx"] = self._d["http_req_4xx"] + 1
            else:
                self._d["http_req_5xx"] = self._d["http_req_5xx"] + 1
            self._d["lat_sum"] = self._d["lat_sum"] + latency_ms
            total = self._d["http_req_total"]
            self._d["lat_avg"] = self._d["lat_sum"] / total
            if latency_ms > self._d["lat_max"]:
                self._d["lat_max"] = latency_ms
            if self._d["lat_min"] == 0 or latency_ms < self._d["lat_min"]:
                self._d["lat_min"] = latency_ms
            if self._d["http_active_connections"] < 5000:
                self._d["circuit_breaker"] = "CLOSED"

    def record_mint(self, user: str, jti: str) -> None:
        need_flush = False
        n, u, j = 0, "none", "none"
        with self._local_lock:
            self._local_mint_buffer += 1
            self._last_user = user
            self._last_jti = jti
            if self._local_mint_buffer >= _MINT_FLUSH_THRESHOLD:
                n = self._local_mint_buffer
                u, j = self._last_user, self._last_jti
                self._local_mint_buffer = 0
                need_flush = True
        if need_flush:
            _do_flush_into(self._d, self._lock, n, u, j)

    def record_mint_failure(self) -> None:
        with self._lock:
            self._d["sec_blocked_attempts"] = self._d["sec_blocked_attempts"] + 1

    def get_snapshot(self) -> Dict[str, Any]:
        self._flush_mint_buffer()
        with self._lock:
            return dict(self._d)

    def increment_active_connections(self) -> int:
        with self._lock:
            self._d["http_active_connections"] = self._d["http_active_connections"] + 1
            active = self._d["http_active_connections"]
            if active > 18000:
                self._d["circuit_breaker"] = "UNDER_LOAD"
            return active

    def decrement_active_connections(self) -> None:
        with self._lock:
            self._d["http_active_connections"] = self._d["http_active_connections"] - 1
