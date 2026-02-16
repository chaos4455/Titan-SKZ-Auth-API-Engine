# -*- coding: utf-8 -*-
"""
Adapter: ConcurrencyAdapter — implements ConcurrencyPort with asyncio.Semaphore + ThreadPoolExecutor.
Pipeline multi-lane: pool dedicado a crypto (ECDSA libera GIL em C); semáforo controla fila in-memory.
Elias Andrade — Replika AI Solutions
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, TypeVar

from titan_intra_service_auth.application.ports.concurrency_port import ConcurrencyPort

T = TypeVar("T")


class ConcurrencyAdapter(ConcurrencyPort):
    """
    Pipeline único: acquire slot (semáforo) → run_in_executor(pool, fn) → release slot.
    Crypto (ECDSA) é CPU-bound e libera GIL; N threads em paralelo. Sem fila duplicada.
    """

    def __init__(self, num_threads: int, semaphore_slots: int | None = None) -> None:
        slots = semaphore_slots or num_threads * 2
        self._pool = ThreadPoolExecutor(
            max_workers=num_threads,
            thread_name_prefix="titan-crypto-",
        )
        self._semaphore = asyncio.Semaphore(slots)

    async def run_with_slot(self, fn: Callable[[], T]) -> T:
        async with self._semaphore:
            # get_running_loop() é obrigatório em contexto async (evita bug no Windows/Proactor)
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(self._pool, fn)
