# -*- coding: utf-8 -*-
"""
🔐 KEYGEN — Geração de Chaves ECDSA e Assinatura de Nonces
==========================================================
Utilitário para clientes: gera par P-256, assina nonce com SHA-256.
Compatível com o CA (ca_service.verify_signature).

Autor: Elias Andrade — Arquiteto de Soluções — Replika AI — Maringá Paraná
Micro-revisão: 000000001
"""

import base64
from dataclasses import dataclass
from typing import Tuple

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec


@dataclass
class IdentityKeys:
    """Par de chaves + PEM para persistência."""

    identity_id: str
    private_key_pem: str
    public_key_pem: str
    scope: str = "access_root"


def generate_identity_keys(
    identity_id: str = "",
    scope: str = "access_root",
) -> Tuple[IdentityKeys, str, str]:
    """
    Gera par de chaves ECDSA P-256.
    Retorna (IdentityKeys, private_pem, public_pem).
    identity_id pode ser vazio — será preenchido após registro na API.
    """
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()

    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()

    keys = IdentityKeys(
        identity_id=identity_id,
        private_key_pem=private_pem,
        public_key_pem=public_pem,
        scope=scope,
    )
    return keys, private_pem, public_pem


def sign_nonce(private_key_pem: str, nonce: str) -> str:
    """
    Assina o nonce com a chave privada. Retorna assinatura em base64url.
    """
    private_key = serialization.load_pem_private_key(
        private_key_pem.encode(),
        password=None,
    )
    nonce_bytes = nonce.encode() if isinstance(nonce, str) else nonce
    signature = private_key.sign(nonce_bytes, ec.ECDSA(hashes.SHA256()))
    return base64.urlsafe_b64encode(signature).decode().rstrip("=")
