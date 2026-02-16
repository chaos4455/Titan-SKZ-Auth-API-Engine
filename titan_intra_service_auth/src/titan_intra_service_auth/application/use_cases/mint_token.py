# -*- coding: utf-8 -*-
"""
Use Case: MintTokenUseCase.
Orchestrates domain + ports to produce a signed JWT (single responsibility, dependency inversion).
Pipeline à prova de erro: timeout no slot libera semáforo; falha registrada em metrics.
Elias Andrade — Replika AI Solutions
"""

import asyncio

from ..dtos.mint_request import MintRequestDTO
from ..dtos.mint_response import MintResponseDTO
from ..ports.concurrency_port import ConcurrencyPort
from ..ports.crypto_port import CryptoPort
from ..ports.metrics_port import MetricsPort
from titan_intra_service_auth.domain import TokenMintingDomainService

# Timeout por request no slot (falha rápida se crypto travar; cliente stress 60s)
_MINT_SLOT_TIMEOUT_SEC = 30.0


class MintTokenUseCase:
    """
    Mint token use case: build claim (domain), acquire slot (concurrency), sign (crypto), record (metrics).
    Depends only on ports — no FastAPI, no multiprocessing.
    """

    def __init__(
        self,
        domain_service: TokenMintingDomainService,
        crypto: CryptoPort,
        metrics: MetricsPort,
        concurrency: ConcurrencyPort,
        exp_hours: int,
        engine_version: str,
    ) -> None:
        self._domain = domain_service
        self._crypto = crypto
        self._metrics = metrics
        self._concurrency = concurrency
        self._exp_hours = exp_hours
        self._engine_version = engine_version

    async def execute(self, dto: MintRequestDTO) -> MintResponseDTO:
        """
        Build claim from DTO, run signing inside concurrency slot (com timeout), record metrics.
        Semáforo é liberado pelo async with mesmo em timeout/exception (à prova de erro).
        """
        user = (dto.user or "guest_user").strip() or "guest_user"
        claim = self._domain.build_claim(user=user, scope=dto.scope)
        payload = claim.to_jwt_payload()

        def do_sign() -> str:
            return self._crypto.sign(payload)

        try:
            token = await asyncio.wait_for(
                self._concurrency.run_with_slot(do_sign),
                timeout=_MINT_SLOT_TIMEOUT_SEC,
            )
        except asyncio.TimeoutError:
            self._metrics.record_mint_failure()
            raise ValueError("Mint slot timeout") from None
        except Exception:
            self._metrics.record_mint_failure()
            raise

        self._metrics.record_mint(user=claim.subject.value, jti=claim.jti.value)

        return MintResponseDTO(
            access_token=token,
            token_type="Bearer",
            expires_in_seconds=self._exp_hours * 3600,
            engine_version=self._engine_version,
        )
