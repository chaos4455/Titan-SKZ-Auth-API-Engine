# -*- coding: utf-8 -*-
"""
Titan Intra Service Auth Engine — Application entry point.
Roda Uvicorn com N workers; cada worker carrega app via fastapi_app:app (sem Manager).
Pipeline: 2 lanes (processos) × M threads crypto = 8 cores Ryzen; à prova de erro.
Elias Andrade — Replika AI Solutions
"""

import asyncio
import os
import sys

# Windows: avoid "too many file descriptors in select()" (limit 512)
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

import uvicorn
from colorama import Fore, init

from titan_intra_service_auth.config import get_settings

init(autoreset=True)

# String target para Uvicorn: cada worker importa o módulo e chama build_app_for_worker()
# (sem Manager no main → multi-worker estável no Windows)
APP_TARGET = "titan_intra_service_auth.infrastructure.http.fastapi_app:app"


def main() -> None:
    settings = get_settings()
    os.system("cls" if os.name == "nt" else "clear")
    print(f"{Fore.MAGENTA}[BOOT] Titan Intra Service Auth Engine - DDD Edition...")
    print(f"{Fore.CYAN}   {settings.APP_NAME} · {settings.AUTHOR}")

    workers = settings.UVCORN_WORKERS
    threads_pw = settings.THREADS_PER_WORKER
    slots_pw = threads_pw * settings.SEMAPHORE_MULTIPLIER
    total_slots = workers * slots_pw
    total_threads = workers * threads_pw

    print(f"{Fore.GREEN} >> System Health: All components operational.")
    print(f"{Fore.WHITE} >> Bind: {settings.SERVER_HOST}:{settings.SERVER_PORT}")
    print(
        f"{Fore.YELLOW} >> Orquestracao: {workers} proc x {threads_pw} threads crypto (ECDSA ES256) = {total_threads} threads | {slots_pw} slots = {total_slots} total"
    )

    try:
        uvicorn.run(
            APP_TARGET,
            host=settings.SERVER_HOST,
            port=settings.SERVER_PORT,
            workers=workers,
            log_level="error",
            access_log=False,
            timeout_keep_alive=settings.UVCORN_KEEP_ALIVE,
            backlog=settings.UVCORN_BACKLOG,
        )
    except OSError as e:
        if e.errno == 10048 or "10048" in str(e) or "address already in use" in str(e).lower():
            print(f"{Fore.RED}[ERRO] Porta {settings.SERVER_PORT} ja em uso.")
            print(f"{Fore.YELLOW} >> Libere a porta ou use outra: set TITAN_PORT=8001")
            print(f"{Fore.YELLOW} >> Windows: netstat -ano | findstr :{settings.SERVER_PORT}  depois  taskkill /PID <PID> /F")
        else:
            raise


if __name__ == "__main__":
    main()
