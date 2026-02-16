# -*- coding: utf-8 -*-
"""
DTO: MintRequest — input for MintTokenUseCase.
Elias Andrade — Replika AI Solutions
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class MintRequestDTO:
    """Input for token minting (from HTTP body)."""

    user: str
    scope: Optional[str] = None
    entropy: Optional[str] = None  # optional client entropy (not used in JWT today)
