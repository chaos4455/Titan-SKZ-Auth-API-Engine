# -*- coding: utf-8 -*-
"""
Value Object: Jti (JWT ID).
Unique identifier for a single token instance; immutable.
Elias Andrade — Replika AI Solutions
"""

import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class Jti:
    """
    JWT ID — unique token identifier. Generated once per mint.
    DDD: value object, equality by value.
    """

    value: str

    def __post_init__(self) -> None:
        if not self.value or not isinstance(self.value, str):
            raise ValueError("Jti.value must be a non-empty string")

    @classmethod
    def generate(cls) -> "Jti":
        """Factory: new unique JTI (e.g. UUID4)."""
        return cls(value=str(uuid.uuid4()))

    def __str__(self) -> str:
        return self.value
