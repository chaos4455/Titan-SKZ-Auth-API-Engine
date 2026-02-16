# -*- coding: utf-8 -*-
"""
📊 ZKP METRICS — Métricas Zero Knowledge Proof
==============================================
Contadores para identidades criadas, challenges emitidos, mints ZKP (sucesso/falha).
Usado por zkp_routes e stats_routes para observabilidade ZKP.

Autor: Elias Andrade — Arquiteto de Soluções — Replika AI — Maringá Paraná
Micro-revisão: 000000001
"""

import threading
import time
from typing import Any, Dict


class ZKPMetricsStore:
    """
    Store de métricas ZKP com lock para thread-safety.
    Não usa Manager (cada worker tem sua cópia); em multi-worker o dashboard
    verá apenas o worker que respondeu à última requisição /stats.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._identities_created = 0
        self._challenges_issued = 0
        self._mints_success = 0
        self._mints_failed = 0
        self._last_identity_id = "none"
        self._last_challenge_ts = 0.0
        self._last_mint_ts = 0.0
        self._start_time = time.time()

    def record_identity_created(self, identity_id: str) -> None:
        with self._lock:
            self._identities_created += 1
            self._last_identity_id = identity_id[:36] if identity_id else "none"

    def record_challenge_issued(self) -> None:
        with self._lock:
            self._challenges_issued += 1
            self._last_challenge_ts = time.time()

    def record_mint_success(self) -> None:
        with self._lock:
            self._mints_success += 1
            self._last_mint_ts = time.time()

    def record_mint_failed(self) -> None:
        with self._lock:
            self._mints_failed += 1

    def get_snapshot(self) -> Dict[str, Any]:
        with self._lock:
            total_mints = self._mints_success + self._mints_failed
            success_rate = (
                (self._mints_success / total_mints * 100) if total_mints > 0 else 100.0
            )
            uptime = time.time() - self._start_time
            zkp_tps = self._mints_success / uptime if uptime > 0 else 0.0
            return {
                "zkp_identities_created": self._identities_created,
                "zkp_challenges_issued": self._challenges_issued,
                "zkp_mints_success": self._mints_success,
                "zkp_mints_failed": self._mints_failed,
                "zkp_mints_total": total_mints,
                "zkp_mint_success_rate_pct": round(success_rate, 2),
                "zkp_tps": round(zkp_tps, 2),
                "zkp_last_identity_id": self._last_identity_id,
                "zkp_uptime_seconds": round(uptime, 2),
            }
