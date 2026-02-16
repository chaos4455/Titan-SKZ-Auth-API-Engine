# -*- coding: utf-8 -*-
"""
Entity: TokenClaim.
Represents the set of claims (payload) for one JWT; built from domain value objects and config.
Elias Andrade — Replika AI Solutions
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict

from ..value_objects.jti import Jti
from ..value_objects.user_identity import UserIdentity


@dataclass
class TokenClaim:
    """
    Domain entity: the claim set for a single token.
    Issuer and expiration come from config; subject and jti from domain.
    """

    subject: UserIdentity
    jti: Jti
    scope: str
    issuer: str
    exp_hours: int
    issued_at: datetime

    def to_jwt_payload(self) -> Dict[str, Any]:
        """
        Serializes to a dict suitable for JWT encoding (iss, sub, iat, exp, jti, scope).
        Used by infrastructure (CryptoPort implementation) to sign.
        """
        exp = self.issued_at + timedelta(hours=self.exp_hours)
        return {
            "iss": self.issuer,
            "sub": self.subject.value,
            "iat": self.issued_at,
            "exp": exp,
            "jti": self.jti.value,
            "scope": self.scope,
        }
