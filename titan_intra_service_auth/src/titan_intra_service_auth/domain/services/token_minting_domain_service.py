# -*- coding: utf-8 -*-
"""
Domain Service: TokenMintingDomainService.
Builds TokenClaim from raw input (user, scope) and config (issuer, exp).
No I/O; pure domain logic (KISS, SRP).
Elias Andrade — Replika AI Solutions
"""

from datetime import datetime

from ..entities.token_claim import TokenClaim
from ..value_objects.jti import Jti
from ..value_objects.user_identity import UserIdentity


class TokenMintingDomainService:
    """
    Creates a TokenClaim from user/scope and configuration.
    Single responsibility: build the claim entity; signing is done by a port.
    """

    def __init__(self, issuer: str, exp_hours: int, default_scope: str = "access_root") -> None:
        self.issuer = issuer
        self.exp_hours = exp_hours
        self.default_scope = default_scope

    def build_claim(self, user: str, scope: str | None = None) -> TokenClaim:
        """Builds a new TokenClaim with generated JTI and current time."""
        identity = UserIdentity(value=user)
        jti = Jti.generate()
        now = datetime.utcnow()
        return TokenClaim(
            subject=identity,
            jti=jti,
            scope=scope or self.default_scope,
            issuer=self.issuer,
            exp_hours=self.exp_hours,
            issued_at=now,
        )
