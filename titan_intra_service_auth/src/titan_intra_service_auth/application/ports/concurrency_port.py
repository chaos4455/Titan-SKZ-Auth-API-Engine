# -*- coding: utf-8 -*-
"""
Port: ConcurrencyPort (Interface for limiting concurrent mints).
Application acquires a slot before minting; infrastructure provides semaphore/thread pool.
Elias Andrade — Replika AI Solutions
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, TypeVar

T = TypeVar("T")


class ConcurrencyPort(ABC):
    """
    Interface for running work with limited concurrency (e.g. semaphore + thread pool).
    run_with_slot(callable) runs the callable once a slot is available.
    """

    @abstractmethod
    async def run_with_slot(self, fn: Callable[[], T]) -> T:
        """
        Acquire a concurrency slot, run fn (possibly in executor), return result.
        Used to cap concurrent mints and offload CPU-bound sign to threads.
        """
        ...
