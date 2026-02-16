# -*- coding: utf-8 -*-
"""
Stats routes: GET /v6/engine/stats — telemetry snapshot + ZKP/CA.
Elias Andrade — Replika AI Solutions — Micro-revisão 000000002
"""

import platform
import time
from typing import Optional

import psutil
from fastapi import APIRouter

from titan_intra_service_auth.application.ports.metrics_port import MetricsPort
from titan_intra_service_auth.infrastructure.ca.ca_repository import CARepository
from titan_intra_service_auth.infrastructure.zkp_metrics import ZKPMetricsStore


def register_stats_routes(
    router: APIRouter,
    metrics: MetricsPort,
    zkp_metrics: Optional[ZKPMetricsStore] = None,
    ca_repository: Optional[CARepository] = None,
) -> None:
    @router.get("/v6/engine/stats")
    async def engine_stats():
        proc = psutil.Process()
        with proc.oneshot():
            mem_info = proc.memory_full_info()
            io_counters = proc.io_counters()
            cpu_usage = proc.cpu_percent()
            fds = getattr(proc, "num_fds", lambda: 0)()
            threads = proc.num_threads()
            ctx = proc.num_ctx_switches()
        s = metrics.get_snapshot()
        uptime = time.time() - s["engine_start_time"]
        tps = s["http_req_total"] / uptime if uptime > 0 else 0
        total = s["http_req_total"] or 1

        # ZKP + CA (opcional)
        zkp_data = {}
        ca_data = {}
        if zkp_metrics:
            zkp_data = zkp_metrics.get_snapshot()
        if ca_repository:
            try:
                ca_data = {
                    "ca_identities_total": ca_repository.count_identities(include_revoked=False),
                    "ca_identities_revoked": ca_repository.count_revoked(),
                    "ca_status": "ok",
                }
            except Exception:
                ca_data = {"ca_identities_total": 0, "ca_identities_revoked": 0, "ca_status": "error"}

        return {
            "engine_metadata": {
                "name": "Titan Intra Service Auth Engine",
                "version": s["engine_version"],
                "uptime_seconds": round(uptime, 2),
                "architecture": platform.machine(),
                "python_version": platform.python_version(),
            },
            "traffic_telemetry": {
                "total_requests": s["http_req_total"],
                "tps_current": round(tps, 2),
                "active_connections": s["http_active_connections"],
                "success_rate": f"{(s['http_req_2xx'] / total) * 100:.2f}%",
                "dropped_requests": s["q_dropped_reqs"],
                "circuit_breaker": s["circuit_breaker"],
            },
            "latency_analytics_ms": {
                "average": round(s["lat_avg"], 4),
                "peak": round(s["lat_max"], 4),
                "minimum": round(s["lat_min"], 4),
                "cumulative_processing_time": round(s["lat_sum"] / 1000, 2),
            },
            "cryptography_performance": {
                "algorithm": "ECDSA-ES256",
                "tokens_minted": s["sec_tokens_minted"],
                "signatures_generated": s["sec_signatures"],
                "sec_blocked_attempts": s.get("sec_blocked_attempts", 0),
                "last_issued_jti": s["sec_last_jti"],
                "last_authenticated_user": s["sec_last_user"],
            },
            "system_resources_low_level": {
                "cpu_percent": cpu_usage,
                "memory_uss_mb": round(mem_info.uss / (1024 * 1024), 2),
                "memory_vms_mb": round(mem_info.vms / (1024 * 1024), 2),
                "open_fds": fds,
                "active_threads": threads,
                "voluntary_ctx_switches": ctx.voluntary,
                "io_read_bytes": io_counters.read_bytes,
                "io_write_bytes": io_counters.write_bytes,
            },
            "zkp_performance": zkp_data,
            "ca_status": ca_data,
        }
