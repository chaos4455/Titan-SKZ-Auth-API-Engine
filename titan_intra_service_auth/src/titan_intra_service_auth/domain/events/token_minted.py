# -*- coding: utf-8 -*-
"""
Domain Event: TokenMinted.
Raised when a token is successfully minted (for future audit or integration).
Elias Andrade — Replika AI Solutions
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class TokenMinted:
    """
    Domain event: a token was minted.
    Attributes can be used by application or infrastructure for logging/audit.
    """

    jti: str
    subject: str
    issued_at: datetime
