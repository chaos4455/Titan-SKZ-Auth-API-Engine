# -*- coding: utf-8 -*-
"""
Centralized configuration for Titan Intra Service Auth Engine.
Single source of truth (DRY); env-based overrides for deployment.
Otimizado para multi-processo + multi-thread: orquestração real CPU/memória.
Elias Andrade — Replika AI Solutions
"""

import os
import sys
from multiprocessing import cpu_count
from typing import Optional

# Pipeline único: 1 worker, N threads crypto (ECDSA libera GIL), slots = 2× threads.
# 32 threads / 64 slots = 200+ TPS após correção do deadlock em record_mint.
_UVCORN_WORKERS_DEFAULT = 1
_THREADS_DEFAULT = 32


class Settings:
    """
    Application settings. Reads from environment with safe defaults.
    Performance: multi-process (Uvicorn workers) + multi-thread (pool de crypto por processo).
    """

    # Identity
    APP_NAME: str = "Titan Intra Service Auth Engine"
    VERSION: str = os.environ.get("TITAN_VERSION", "6.0.0-DDD")
    AUTHOR: str = "Elias Andrade — Replika AI Solutions"

    # HTTP
    SERVER_HOST: str = os.environ.get("TITAN_HOST", "0.0.0.0")
    SERVER_PORT: int = int(os.environ.get("TITAN_PORT", "8000"))

    # Crypto: ECDSA ES256 (curva P-256) — melhor performance que RSA, assinaturas menores
    TOKEN_EXP_HOURS: int = int(os.environ.get("TITAN_TOKEN_EXP_HOURS", "24"))
    JWT_ALGORITHM: str = os.environ.get("TITAN_JWT_ALGORITHM", "ES256")
    JWT_ISSUER: str = "titan-intra-service-auth-v6"

    # Orquestração estilo V1: 1 processo, N threads crypto, slots = THREADS * 2 (fila curta como no monólito)
    NUM_WORKERS: int = int(os.environ.get("TITAN_NUM_WORKERS", str(_UVCORN_WORKERS_DEFAULT)))
    UVCORN_WORKERS: int = int(os.environ.get("TITAN_UVCORN_WORKERS", str(_UVCORN_WORKERS_DEFAULT)))
    THREADS_PER_WORKER: int = int(os.environ.get("TITAN_THREADS_PER_WORKER", str(_THREADS_DEFAULT)))
    MAX_QUEUE_CAPACITY: int = int(os.environ.get("TITAN_MAX_QUEUE_CAPACITY", "20000"))
    SEMAPHORE_MULTIPLIER: int = 2  # slots = THREADS_PER_WORKER * 2 (ex.: 32*2 = 64)

    # Observability
    METRIC_SYNC_INTERVAL: float = 0.5
    UVCORN_BACKLOG: int = 2048 if os.name == "nt" else 4096
    UVCORN_KEEP_ALIVE: int = 60


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Singleton access to settings (KISS)."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
