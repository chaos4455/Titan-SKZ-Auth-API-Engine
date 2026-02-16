# -*- coding: utf-8 -*-
"""
Value Object: UserIdentity.
Identifies the subject of an intra-service token (immutable, comparable by value).
Elias Andrade — Replika AI Solutions
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class UserIdentity:
    """
    Immutable value object representing the authenticated identity (subject).
    DDD: equality by value, no identity field.
    """

    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str) or not self.value.strip():
            raise ValueError("UserIdentity.value must be a non-empty string")

    def __str__(self) -> str:
        return self.value
