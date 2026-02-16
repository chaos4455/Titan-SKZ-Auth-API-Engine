# -*- coding: utf-8 -*-
"""
Auth routes: POST /v6/auth/mint — delegates to MintTokenUseCase.
Elias Andrade — Replika AI Solutions
"""

from fastapi import APIRouter, HTTPException, Request

from titan_intra_service_auth.application.dtos.mint_request import MintRequestDTO
from titan_intra_service_auth.application.use_cases.mint_token import MintTokenUseCase
from titan_intra_service_auth.application.ports.metrics_port import MetricsPort


def register_auth_routes(router: APIRouter, use_case: MintTokenUseCase, metrics: MetricsPort) -> None:
    """Registers mint endpoint; use_case and metrics injected (DIP)."""

    @router.post("/v6/auth/mint", status_code=201)
    async def mint_token(request: Request):
        try:
            body = await request.json()
            dto = MintRequestDTO(
                user=body.get("user", "guest_user"),
                scope=body.get("scope"),
                entropy=body.get("entropy"),
            )
            response_dto = await use_case.execute(dto)
            return {
                "access_token": response_dto.access_token,
                "token_type": response_dto.token_type,
                "expires_in": response_dto.expires_in_seconds,
                "engine": response_dto.engine_version,
            }
        except ValueError as e:
            metrics.record_mint_failure()
            raise HTTPException(status_code=422, detail=f"Minting Failure: {str(e)}")
        except Exception as e:
            metrics.record_mint_failure()
            raise HTTPException(status_code=422, detail=f"Minting Failure: {str(e)}")
