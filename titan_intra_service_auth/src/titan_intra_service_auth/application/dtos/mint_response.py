# -*- coding: utf-8 -*-
"""
DTO: MintResponse — output of MintTokenUseCase.
Elias Andrade — Replika AI Solutions
"""

from dataclasses import dataclass


@dataclass
class MintResponseDTO:
    """Output of token minting (to HTTP response)."""

    access_token: str
    token_type: str = "Bearer"
    expires_in_seconds: int = 0
    engine_version: str = ""
