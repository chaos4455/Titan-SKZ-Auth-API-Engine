# -*- coding: utf-8 -*-
"""
Port: CryptoPort (Interface for token signing).
Application layer depends on this abstraction; infrastructure implements it.
Elias Andrade — Replika AI Solutions
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class CryptoPort(ABC):
    """
    Interface for signing a JWT payload. Implementations: ECDSA ES256 (default), RSA (legado).
    Single method (Interface Segregation).
    """

    @abstractmethod
    def sign(self, payload: Dict[str, Any]) -> str:
        """Returns a signed JWT string (e.g. ES256, RS256)."""
        ...
