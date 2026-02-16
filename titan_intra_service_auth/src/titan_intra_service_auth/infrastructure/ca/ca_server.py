# -*- coding: utf-8 -*-
"""
🏛️ CA SERVER — Servidor HTTP do Certificate Authority
=====================================================
Serviço separado, componentizado. Roda em porta própria (ex: 8001).
A API principal chama este serviço para registrar identidades e verificar assinaturas.
O CA nunca conhece a API — apenas recebe requests e responde.

Rotas:
  POST /ca/register  — Registra nova identidade (pubkey_pem)
  POST /ca/verify    — Verifica assinatura (identity_id, nonce, signature)

Autor: Elias Andrade — Arquiteto de Soluções — Replika AI — Maringá Paraná
Produto: Titan ZKP Auth — CA Server
Micro-revisão: 000000001
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from titan_intra_service_auth.infrastructure.ca.ca_repository import CARepository
from titan_intra_service_auth.infrastructure.ca.ca_service import CAService


class RegisterRequest(BaseModel):
    """Request para registro de identidade."""
    pubkey_pem: str
    scope: str = "access_root"


class RegisterResponse(BaseModel):
    """Resposta do registro."""
    identity_id: str
    pubkey_fingerprint: str
    scope: str


class VerifyRequest(BaseModel):
    """Request para verificação de assinatura."""
    identity_id: str
    nonce: str
    signature: str


class VerifyResponse(BaseModel):
    """Resposta da verificação."""
    authorized: bool
    identity_id: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicializa CA no startup."""
    app.state.ca_service = CAService(repository=CARepository())
    yield
    # cleanup se necessário


def create_ca_app() -> FastAPI:
    """Factory do app FastAPI do CA."""
    app = FastAPI(
        title="Titan CA — Certificate Authority (ZKP)",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/ca/docs",
        redoc_url="/ca/redoc",
    )

    @app.post("/ca/register", response_model=RegisterResponse)
    async def register_identity(request: RegisterRequest):
        """Registra nova identidade. Recebe apenas pubkey — ZKP."""
        try:
            identity_id, fingerprint = app.state.ca_service.register_identity(
                pubkey_pem=request.pubkey_pem,
                scope=request.scope,
            )
            return RegisterResponse(
                identity_id=identity_id,
                pubkey_fingerprint=fingerprint,
                scope=request.scope,
            )
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))

    @app.post("/ca/verify", response_model=VerifyResponse)
    async def verify_signature(request: VerifyRequest):
        """Verifica assinatura do nonce. Retorna authorized=True/False."""
        authorized = app.state.ca_service.verify_signature(
            identity_id=request.identity_id,
            nonce=request.nonce,
            signature_b64=request.signature,
        )
        return VerifyResponse(authorized=authorized, identity_id=request.identity_id)

    @app.get("/ca/health")
    async def health():
        """Health check do CA."""
        return {"status": "ok", "service": "titan-ca-zkp"}

    return app


# App instance para Uvicorn
ca_app = create_ca_app()
