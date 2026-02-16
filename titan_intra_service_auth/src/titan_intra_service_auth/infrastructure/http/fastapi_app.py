# -*- coding: utf-8 -*-
"""
FastAPI application factory — wires routes, middleware, CORS (composition root).
Worker entry point: build_app_for_worker() cria app por processo (sem Manager) para multi-worker.
Elias Andrade — Replika AI Solutions
"""

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from titan_intra_service_auth.application.ports.metrics_port import MetricsPort
from titan_intra_service_auth.application.use_cases.mint_token import MintTokenUseCase
from titan_intra_service_auth.config import get_settings
from titan_intra_service_auth.domain import TokenMintingDomainService
from titan_intra_service_auth.infrastructure.crypto import EcdsaSignerAdapter
from titan_intra_service_auth.infrastructure.observability import (
    ConcurrencyAdapter,
    create_local_metrics_adapter,
)
from titan_intra_service_auth.infrastructure.http.middleware.telemetry_middleware import (
    TelemetryMiddleware,
)
from titan_intra_service_auth.infrastructure.ca import CARepository, CAService
from titan_intra_service_auth.infrastructure.zkp_metrics import ZKPMetricsStore
from titan_intra_service_auth.infrastructure.http.routes.auth_routes import register_auth_routes
from titan_intra_service_auth.infrastructure.http.routes.health_routes import register_health_routes
from titan_intra_service_auth.infrastructure.http.routes.stats_routes import register_stats_routes
from titan_intra_service_auth.infrastructure.http.routes.zkp_routes import register_zkp_routes


def create_app(
    metrics: MetricsPort,
    mint_use_case: MintTokenUseCase,
) -> FastAPI:
    """
    Creates and returns the FastAPI app. Dependencies injected (no global state for use case/metrics).
    Definida antes de build_app_for_worker para evitar NameError no import.
    """
    settings = get_settings()
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.VERSION,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
    )
    app.state.metrics = metrics
    app.state.mint_use_case = mint_use_case
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Performance-TPS", "X-Request-ID", "X-Engine-Lat"],
    )
    app.add_middleware(TelemetryMiddleware)

    router = APIRouter()
    ca_repository = CARepository()
    ca_service = CAService(repository=ca_repository)
    zkp_metrics = ZKPMetricsStore()

    register_health_routes(router, metrics)
    register_auth_routes(router, mint_use_case, metrics)
    register_stats_routes(router, metrics, zkp_metrics=zkp_metrics, ca_repository=ca_repository)
    register_zkp_routes(router, ca_service, mint_use_case, metrics, zkp_metrics)
    app.include_router(router)

    return app


def build_app_for_worker() -> FastAPI:
    """
    Cria a aplicação dentro de cada worker (Uvicorn carrega este módulo por processo).
    Sem Manager/shared state → permite 2+ workers no Windows (spawn).
    Pipeline: receive → mint (crypto em thread pool) → respond; métricas locais por worker.
    """
    settings = get_settings()
    metrics = create_local_metrics_adapter(settings.VERSION, settings.UVCORN_WORKERS)
    crypto = EcdsaSignerAdapter(algorithm=settings.JWT_ALGORITHM)
    slots = settings.THREADS_PER_WORKER * settings.SEMAPHORE_MULTIPLIER
    concurrency = ConcurrencyAdapter(
        num_threads=settings.THREADS_PER_WORKER,
        semaphore_slots=slots,
    )
    domain_service = TokenMintingDomainService(
        issuer=settings.JWT_ISSUER,
        exp_hours=settings.TOKEN_EXP_HOURS,
        default_scope="access_root",
    )
    mint_use_case = MintTokenUseCase(
        domain_service=domain_service,
        crypto=crypto,
        metrics=metrics,
        concurrency=concurrency,
        exp_hours=settings.TOKEN_EXP_HOURS,
        engine_version=settings.VERSION,
    )
    return create_app(metrics=metrics, mint_use_case=mint_use_case)


# Entry point para Uvicorn multi-worker: cada processo carrega o módulo e obtém app próprio
app = build_app_for_worker()
