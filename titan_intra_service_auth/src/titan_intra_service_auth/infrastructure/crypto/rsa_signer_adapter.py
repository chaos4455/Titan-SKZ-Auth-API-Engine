# -*- coding: utf-8 -*-
"""
Adapter: RsaSignerAdapter — implements CryptoPort using RSA (PyJWT + cryptography).
Elias Andrade — Replika AI Solutions
"""

import sys
from typing import Any, Dict

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from titan_intra_service_auth.application.ports.crypto_port import CryptoPort

try:
    from colorama import Fore
except ImportError:
    Fore = type("F", (), {"CYAN": "", "RED": ""})()


class RsaSignerAdapter(CryptoPort):
    """
    Signs JWT payloads with RS256 using an in-memory RSA key pair.
    Single responsibility: implement CryptoPort (SOLID S).
    """

    def __init__(self, key_size: int = 512, algorithm: str = "RS256") -> None:
        self._key_size = key_size
        self._algorithm = algorithm
        self._pem_private: str = ""
        self._initialize()

    def _initialize(self) -> None:
        try:
            if sys.platform != "test":
                print(f"{Fore.CYAN}🔐 [SECURITY] Gerando Cold Storage Key RSA {self._key_size} bits...")
            private_key = rsa.generate_private_key(public_exponent=65537, key_size=self._key_size)
            self._pem_private = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            ).decode()
        except Exception as e:
            print(f"{Fore.RED}❌ [SECURITY] Falha ao gerar chaves: {e}")
            raise

    def sign(self, payload: Dict[str, Any]) -> str:
        return jwt.encode(payload, self._pem_private, algorithm=self._algorithm)
