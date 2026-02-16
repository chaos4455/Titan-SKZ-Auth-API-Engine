# -*- coding: utf-8 -*-
"""
Health routes: GET /health — liveness/readiness.
Elias Andrade — Replika AI Solutions
"""

from fastapi import APIRouter

from titan_intra_service_auth.application.ports.metrics_port import MetricsPort


def register_health_routes(router: APIRouter, metrics: MetricsPort) -> None:
    @router.get("/health")
    async def health():
        snap = metrics.get_snapshot()
        return {
            "status": "OPERATIONAL",
            "engine": "TitanIntraServiceAuth",
            "health_score": snap.get("health_score", 100.0),
        }
