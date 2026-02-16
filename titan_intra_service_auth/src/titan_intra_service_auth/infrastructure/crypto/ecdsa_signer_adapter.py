# -*- coding: utf-8 -*-
"""
Adapter: EcdsaSignerAdapter — implements CryptoPort using ECDSA (PyJWT + cryptography).
Curva elíptica P-256 (SECP256R1) = ES256 — melhor performance e segurança que RSA 512.
Elias Andrade — Arquiteto de Soluções — Replika AI — Maringá Paraná
Micro-revisão: 000000001 — Pipeline multi-lane 1 proc + 2 threads por camada.
"""

import os
import sys
from typing import Any, Dict

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

from titan_intra_service_auth.application.ports.crypto_port import CryptoPort

try:
    from colorama import Fore
except ImportError:
    Fore = type("F", (), {"CYAN": "", "RED": ""})()


# ES256 = ECDSA com SHA-256 na curva P-256 (SECP256R1) — estado da arte para JWT
JWT_ALGORITHM_ES256 = "ES256"


class EcdsaSignerAdapter(CryptoPort):
    """
    Assina payloads JWT com ES256 usando par de chaves ECDSA P-256 em memória.
    Responsabilidade única: implementar CryptoPort (SOLID S).
    ECDSA é mais rápido que RSA para assinaturas e produz tokens menores.
    """

    def __init__(self, algorithm: str = JWT_ALGORITHM_ES256) -> None:
        self._algorithm = algorithm
        self._pem_private: str = ""
        self._initialize()

    def _initialize(self) -> None:
        try:
            if os.environ.get("TITAN_DEBUG", "").lower() in ("1", "true", "yes") and sys.platform != "test":
                print(f"{Fore.CYAN}🔐 [SECURITY] Gerando chave ECDSA P-256 (ES256)...")
            # SECP256R1 = curva P-256, usada pelo ES256 (RFC 7518)
            private_key = ec.generate_private_key(ec.SECP256R1())
            self._pem_private = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            ).decode()
        except Exception as e:
            print(f"{Fore.RED}❌ [SECURITY] Falha ao gerar chave ECDSA: {e}")
            raise

    def sign(self, payload: Dict[str, Any]) -> str:
        return jwt.encode(payload, self._pem_private, algorithm=self._algorithm)
