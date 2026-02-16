# -*- coding: utf-8 -*-
"""
🔐 ZKP ROUTES — Rotas Zero Knowledge Proof
==========================================
/v6/zkp/identity  — Criar identidade (cliente envia pubkey, recebe identity_id)
/v6/zkp/challenge — Obter nonce para assinar (prova de posse)
/v6/zkp/mint      — Obter token após provar posse da chave privada

A API NUNCA sabe a identidade real. Apenas valida via CA.

CORREÇÃO RACE CONDITION: challenge_id único por challenge — permite N concurrent
requests por identity (antes: 1 nonce/identity = falhas em burst paralelo).
Autor: Elias Andrade — Arquiteto de Soluções — Replika AI — Maringá Paraná
Micro-revisão: 000000002
"""

import secrets
import threading
import uuid
from typing import Optional, Tuple

from fastapi import APIRouter, HTTPException, Request

from titan_intra_service_auth.application.ports.metrics_port import MetricsPort
from titan_intra_service_auth.application.use_cases.mint_token import MintTokenUseCase
from titan_intra_service_auth.infrastructure.ca.ca_service import CAService
from titan_intra_service_auth.infrastructure.zkp_metrics import ZKPMetricsStore


# Cache: challenge_id -> (identity_id, nonce) — múltiplos challenges por identity
# Em produção: Redis com TTL 60s
_challenge_store: dict[str, Tuple[str, str]] = {}
_challenge_lock = threading.Lock()
_MAX_CHALLENGES = 50000


def register_zkp_routes(
    router: APIRouter,
    ca_service: CAService,
    mint_use_case: MintTokenUseCase,
    metrics: MetricsPort,
    zkp_metrics: ZKPMetricsStore,
) -> None:
    """Registra rotas ZKP no router."""

    @router.post("/v6/zkp/identity", status_code=201)
    async def create_identity(request: Request):
        """
        Cria identidade ZKP. Cliente envia pubkey_pem gerada localmente.
        API repassa ao CA; CA registra e retorna identity_id.
        O cliente deve salvar (identity_id, pubkey, private_key) em u-data.
        """
        try:
            body = await request.json()
            pubkey_pem = body.get("pubkey_pem")
            scope = body.get("scope", "access_root")

            if not pubkey_pem or not isinstance(pubkey_pem, str):
                raise HTTPException(status_code=422, detail="pubkey_pem é obrigatório")

            identity_id, fingerprint = ca_service.register_identity(
                pubkey_pem=pubkey_pem,
                scope=scope,
            )
            zkp_metrics.record_identity_created(identity_id)

            return {
                "identity_id": identity_id,
                "pubkey_fingerprint": fingerprint,
                "scope": scope,
                "message": "Salve identity_id, pubkey_pem e private_key em u-data/{identity_id}/",
            }
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))

    @router.get("/v6/zkp/challenge")
    async def get_challenge(identity_id: Optional[str] = None):
        """
        Retorna challenge_id + nonce. Cliente assina nonce e envia challenge_id no mint.
        Permite N challenges simultâneos por identity (evita race em burst paralelo).
        """
        if not identity_id:
            raise HTTPException(status_code=422, detail="identity_id é obrigatório")

        if not ca_service.is_authorized(identity_id):
            raise HTTPException(status_code=403, detail="Identity não autorizada ou inexistente")

        nonce = secrets.token_urlsafe(32)
        challenge_id = str(uuid.uuid4())
        with _challenge_lock:
            _challenge_store[challenge_id] = (identity_id, nonce)
            if len(_challenge_store) > _MAX_CHALLENGES:
                for k in list(_challenge_store.keys())[:_MAX_CHALLENGES // 2]:
                    _challenge_store.pop(k, None)
        zkp_metrics.record_challenge_issued()

        return {"challenge_id": challenge_id, "nonce": nonce, "identity_id": identity_id}

    @router.post("/v6/zkp/mint", status_code=201)
    async def mint_token_zkp(request: Request):
        """
        Mint token ZKP. Cliente envia challenge_id, identity_id, nonce e signature.
        Lookup por challenge_id (evita race). API verifica assinatura via CA.
        Subject do token = identity_id (não identidade real).
        """
        try:
            body = await request.json()
            challenge_id = body.get("challenge_id")
            identity_id = body.get("identity_id")
            nonce = body.get("nonce")
            signature = body.get("signature")
            scope = body.get("scope", "access_root")

            if not all([challenge_id, identity_id, nonce, signature]):
                metrics.record_mint_failure()
                zkp_metrics.record_mint_failed()
                raise HTTPException(
                    status_code=422,
                    detail="challenge_id, identity_id, nonce e signature são obrigatórios",
                )

            # Lookup por challenge_id (permite N concurrent por identity)
            with _challenge_lock:
                stored = _challenge_store.pop(challenge_id, None)
            stored_identity_id, stored_nonce = stored if stored else (None, None)
            if not stored or stored_identity_id != identity_id or stored_nonce != nonce:
                metrics.record_mint_failure()
                zkp_metrics.record_mint_failed()
                raise HTTPException(status_code=403, detail="Challenge inválido ou expirado")

            # CA verifica assinatura (prova de posse da chave privada)
            if not ca_service.verify_signature(
                identity_id=identity_id,
                nonce=nonce,
                signature_b64=signature,
            ):
                metrics.record_mint_failure()
                zkp_metrics.record_mint_failed()
                raise HTTPException(status_code=403, detail="Assinatura inválida")

            # Subject = identity_id (API não sabe quem é a pessoa)
            from titan_intra_service_auth.application.dtos.mint_request import MintRequestDTO

            dto = MintRequestDTO(user=identity_id, scope=scope)
            response_dto = await mint_use_case.execute(dto)
            zkp_metrics.record_mint_success()

            return {
                "access_token": response_dto.access_token,
                "token_type": response_dto.token_type,
                "expires_in": response_dto.expires_in_seconds,
                "engine": response_dto.engine_version,
                "subject": identity_id,  # ZKP: subject é o id técnico, não identidade real
            }
        except HTTPException:
            raise
        except ValueError as e:
            metrics.record_mint_failure()
            zkp_metrics.record_mint_failed()
            raise HTTPException(status_code=422, detail=str(e))
        except Exception as e:
            metrics.record_mint_failure()
            zkp_metrics.record_mint_failed()
            raise HTTPException(status_code=500, detail=str(e))
