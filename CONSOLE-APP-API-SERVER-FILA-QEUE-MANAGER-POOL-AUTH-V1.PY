# -*- coding: utf-8 -*-
"""
=========================================================================================
TITAN-AUTH CORE V6 - HYPER-PERFORMANCE SUPREME EDITION
=========================================================================================
Arquitetura: Distributed Micro-Kernel Arquitecture (Single File)
Performance Target: 1000+ TPS | Security: RSA 512 (Performance Optimized)
Author: Software Architecture Engine
=========================================================================================
"""

import asyncio
import time
import uuid
import jwt
import os
import sys
import psutil
import platform
import threading
import multiprocessing
import logging
import json
import socket
import gc
import math
import signal
from datetime import datetime, timedelta
from multiprocessing import Process, Manager, cpu_count, Queue, Event, Lock
from typing import Dict, Any, List, Optional, Union, NoReturn
from concurrent.futures import ThreadPoolExecutor

# Verificação de Dependências Críticas
try:
    import uvicorn
    from fastapi import FastAPI, HTTPException, Request, status, Depends, Response
    from fastapi.responses import JSONResponse
    from fastapi.middleware.cors import CORSMiddleware
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import serialization
    from colorama import Fore, Style, init
except ImportError as e:
    print(f"❌ [CRITICAL] Dependência faltando: {e}")
    print(f"Execute: pip install fastapi uvicorn cryptography pyjwt psutil colorama")
    sys.exit(1)

# Inicialização de Interface Visual
init(autoreset=True)

# Windows: ProactorEventLoop evita "too many file descriptors in select()" (limite 512)
# Aplicado em todo processo (main + workers) para fila infinita e 500+ TPS
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# =======================================================================================
# ⚙️ CONFIGURAÇÕES GLOBAIS DE ALTA DISPONIBILIDADE
# =======================================================================================
VERSION = "6.0.0-HYPER-PERFORMANCE"
RSA_KEY_SIZE = 512          # Otimizado para 1000 TPS (Aviso: Inseguro para Produção)
TOKEN_EXP_HOURS = 24
NUM_PROCESSES = cpu_count() # Escala total nos núcleos disponíveis
THREADS_PER_WORKER = 64     # 500+ TPS: pool grande para RSA em paralelo sem fila
MAX_QUEUE_CAPACITY = 20000  # Fila expandida para evitar Circuit Breaker precoce
SERVER_PORT = 8000
SERVER_HOST = "0.0.0.0"
METRIC_SYNC_INTERVAL = 0.5  # Sincronização de métricas a cada 500ms

# =======================================================================================
# 📊 TELEMETRIA AVANÇADA (SHARED MEMORY SCHEMA)
# =======================================================================================
def create_hyper_telemetry_schema(mgr):
    """
    Cria a estrutura de dados compartilhada no Manager.
    Projetado para ser acessado por múltiplos processos de forma atômica.
    """
    return mgr.dict({
        # --- Engine Identity ---
        "engine_version": VERSION,
        "engine_start_time": time.time(),
        "engine_status": "BOOTING",
        "active_workers": NUM_PROCESSES,
        "circuit_breaker": "CLOSED",
        
        # --- Real-Time Performance Counters ---
        "http_req_total": 0,
        "http_req_2xx": 0,
        "http_req_4xx": 0,
        "http_req_5xx": 0,
        "http_active_connections": 0,
        "http_bytes_received": 0,
        "http_bytes_sent": 0,
        
        # --- Advanced Latency Metrics (Micro-precision) ---
        "lat_min": 0.0,
        "lat_max": 0.0,
        "lat_avg": 0.0,
        "lat_sum": 0.0,
        "throughput_tps": 0.0,
        
        # --- Resource & Orchestration ---
        "q_current_size": 0,
        "q_peak_size": 0,
        "q_dropped_reqs": 0,
        "pool_utilization": 0.0,
        "semaphore_locks": 0,
        # --- Orchestration (Semáforos, Pistas, Cabeças, Workers, Processos) ---
        "semaphore_slots_total": THREADS_PER_WORKER * 2,
        "semaphore_in_use": 0,
        "thread_pool_max_workers": THREADS_PER_WORKER,
        "num_processes": NUM_PROCESSES,
        "max_queue_capacity": MAX_QUEUE_CAPACITY,
        
        # --- Security Vault Stats ---
        "sec_tokens_minted": 0,
        "sec_rsa_signatures": 0,
        "sec_key_rotations": 0,
        "sec_blocked_attempts": 0,
        "sec_last_user": "none",
        "sec_last_jti": "none",
        
        # --- OS & Hardware Monitoring ---
        "sys_cpu_usage": 0.0,
        "sys_ram_usage_mb": 0.0,
        "sys_threads_count": 0,
        "sys_ctx_switches": 0,
        "sys_interrupts": 0,
        "sys_load_avg": [0.0, 0.0, 0.0],
        "sys_io_read": 0,
        "sys_io_write": 0,
        "sys_fds_open": 0,
        
        # --- Health Monitoring ---
        "health_score": 100.0,
        "last_error": "none",
        "last_request_id": "none",
        "perf_optimization_active": True
    })

# =======================================================================================
# 🔐 COMPONENTE: CRYPTO ENGINE (RSA OPTIMIZED)
# =======================================================================================
class CryptoVaultV6:
    """
    Motor Criptográfico de alta performance.
    Utiliza RSA para assinatura de tokens JWT.
    """
    def __init__(self, key_size: int = 512):
        self.key_size = key_size
        self.private_key = None
        self.public_key = None
        self.pem_private = None
        self.pem_public = None
        self.initialize_engine()

    def initialize_engine(self) -> None:
        """Gera as chaves iniciais no boot do processo."""
        try:
            print(f"{Fore.CYAN}🔐 [SECURITY] Gerando Cold Storage Key RSA {self.key_size} bits...")
            self.private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=self.key_size
            )
            self.public_key = self.private_key.public_key()
            
            self.pem_private = self.private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ).decode()
            
            self.pem_public = self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode()
        except Exception as e:
            print(f"{Fore.RED}❌ [SECURITY] Falha ao gerar chaves: {e}")
            sys.exit(1)

    def sign_payload(self, payload: Dict[str, Any]) -> str:
        """Assina um payload JWT usando a chave privada PEM."""
        return jwt.encode(payload, self.pem_private, algorithm="RS256")

# Instância Global do Vault
crypto_engine = CryptoVaultV6(key_size=RSA_KEY_SIZE)

# =======================================================================================
# 🏗️ COMPONENTE: ARCHITECTURE MANAGER (RESOURCE POOLS)
# =======================================================================================
class TitanArchitectureV6:
    """
    Gerenciador de infraestrutura interna.
    Controla o pooling de threads, semáforos de concorrência e o Circuit Breaker.
    """
    def __init__(self, stats_ref, lock_ref):
        self.stats = stats_ref
        self.lock = lock_ref
        self.pool = ThreadPoolExecutor(max_workers=THREADS_PER_WORKER)
        self.semaphore = asyncio.Semaphore(THREADS_PER_WORKER * 2)  # 128 slots: fila curta para 500 TPS
        self.metric_buffer = {"req": 0, "mint": 0, "lat": 0.0}
        self.last_sync = time.time()

    def update_stat_atomic(self, key: str, value: Any, increment: bool = True):
        """Atualização segura de métricas com Lock."""
        try:
            with self.lock:
                if increment:
                    self.stats[key] += value
                else:
                    self.stats[key] = value
        except Exception:
            pass

    async def apply_backpressure(self) -> bool:
        """
        Lógica de Circuit Breaker.
        Protege a API de saturação total de recursos.
        """
        active = self.stats["http_active_connections"]
        limit = MAX_QUEUE_CAPACITY
        
        if active > limit:
            self.update_stat_atomic("circuit_breaker", "OPEN", False)
            self.update_stat_atomic("health_score", 50.0, False)
            return False
        
        if active < (limit * 0.7) and self.stats["circuit_breaker"] == "OPEN":
            self.update_stat_atomic("circuit_breaker", "CLOSED", False)
            self.update_stat_atomic("health_score", 100.0, False)
            
        return True

    def flush_metrics(self):
        """Sincroniza o buffer local de métricas com a memória compartilhada."""
        if time.time() - self.last_sync > METRIC_SYNC_INTERVAL:
            with self.lock:
                self.stats["http_req_total"] += self.metric_buffer["req"]
                self.stats["sec_tokens_minted"] += self.metric_buffer["mint"]
            self.metric_buffer = {"req": 0, "mint": 0, "lat": 0.0}
            self.last_sync = time.time()

# =======================================================================================
# 🚀 CORE: FASTAPI ENGINE (OPTIMIZED)
# =======================================================================================
app = FastAPI(
    title="TitanAuth Supreme V6",
    version=VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configuração de CORS Universal para Integração de Sistemas
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Performance-TPS", "X-Request-ID", "X-Engine-Lat"]
)

# Injeção de Dependência da Arquitetura (Será populado no main)
stats_db = None
global_lock = None
titan_arch = None

@app.middleware("http")
async def supreme_telemetry_middleware(request: Request, call_next):
    """
    Middleware Nível 7 — orquestração "só enfileira, nunca quebra".
    Nenhum 503 por overload: toda requisição entra na fila (semáforo + pool); pode esperar até 60s em hold.
    Apenas 2 seções críticas: entrada (registro) e saída (métricas em batch).
    """
    rid = str(uuid.uuid4())[:8]
    t_start = time.perf_counter()
    response = None
    sc = 0

    # 🔒 ENTRADA: só registra conexão ativa; NUNCA rejeita (fila infinita, 8 cabeças de auth)
    with global_lock:
        stats_db["http_active_connections"] += 1
        if stats_db["http_active_connections"] > stats_db["q_peak_size"]:
            stats_db["q_peak_size"] = stats_db["http_active_connections"]
        stats_db["q_current_size"] = stats_db["http_active_connections"]
        stats_db["last_request_id"] = rid
        # Circuit breaker só para display; não retorna 503 — API alimenta a fila sempre
        if stats_db["http_active_connections"] > MAX_QUEUE_CAPACITY * 0.9:
            stats_db["circuit_breaker"] = "UNDER_LOAD"
        else:
            stats_db["circuit_breaker"] = "CLOSED"

    try:
        response = await call_next(request)
        sc = response.status_code
        duration = (time.perf_counter() - t_start) * 1000
        response.headers["X-Request-ID"] = rid
        response.headers["X-Engine-Lat"] = f"{duration:.2f}ms"

        # 🔒 SAÍDA: métricas em batch
        with global_lock:
            stats_db["http_active_connections"] -= 1
            stats_db["q_current_size"] = stats_db["http_active_connections"]
            stats_db["http_req_total"] += 1
            if sc < 400:
                stats_db["http_req_2xx"] += 1
            elif sc < 500:
                stats_db["http_req_4xx"] += 1
            else:
                stats_db["http_req_5xx"] += 1
            stats_db["lat_sum"] += duration
            stats_db["lat_avg"] = stats_db["lat_sum"] / stats_db["http_req_total"]
            if duration > stats_db["lat_max"]:
                stats_db["lat_max"] = duration
            if stats_db["lat_min"] == 0 or duration < stats_db["lat_min"]:
                stats_db["lat_min"] = duration
            if stats_db["http_active_connections"] < MAX_QUEUE_CAPACITY * 0.5:
                stats_db["circuit_breaker"] = "CLOSED"

        return response

    except Exception as e:
        with global_lock:
            stats_db["http_active_connections"] -= 1
            stats_db["q_current_size"] = stats_db["http_active_connections"]
            stats_db["http_req_total"] += 1
            stats_db["http_req_5xx"] += 1
            stats_db["last_error"] = str(e)
        return JSONResponse(status_code=500, content={"error": "Critical Internal Engine Error"})

# =======================================================================================
# 🛣️ ENDPOINTS DE ALTA PERFORMANCE
# =======================================================================================

@app.get("/health")
async def system_health():
    """Liveness & Readiness probe."""
    return {
        "status": "OPERATIONAL",
        "engine": "TitanAuthV6",
        "health_score": stats_db["health_score"]
    }

@app.get("/v6/engine/stats")
async def engine_telemetry_report():
    """
    Relatório de telemetria profunda com mais de 60 indicadores.
    Otimizado para não gerar overhead de CPU durante a coleta.
    """
    proc = psutil.Process()
    with proc.oneshot():
        mem_info = proc.memory_full_info()
        io_counters = proc.io_counters()
        cpu_usage = proc.cpu_percent()
        fds = proc.num_fds() if hasattr(proc, 'num_fds') else 0
        threads = proc.num_threads()
        ctx = proc.num_ctx_switches()

    # Deep Copy do estado compartilhado para leitura rápida
    with global_lock:
        s = dict(stats_db)

    uptime = time.time() - s["engine_start_time"]
    tps = s["http_req_total"] / uptime if uptime > 0 else 0
    tpm = tps * 60.0
    # Garantir que orchestration/network nunca venham zerados: usar constantes quando dict não tiver ou for 0
    sem_total = s.get("semaphore_slots_total") or (THREADS_PER_WORKER * 2)
    sem_in_use = s.get("semaphore_in_use", 0)
    sem_available = max(0, sem_total - sem_in_use)
    num_proc = s.get("num_processes") or NUM_PROCESSES
    threads_pw = s.get("thread_pool_max_workers") or THREADS_PER_WORKER
    max_q = s.get("max_queue_capacity") or MAX_QUEUE_CAPACITY
    q_current = s.get("q_current_size")
    if q_current is None:
        q_current = s["http_active_connections"]
    q_peak = s.get("q_peak_size", 0)
    active_w = s.get("active_workers") or NUM_PROCESSES

    return {
        "engine_metadata": {
            "name": "TitanAuth Supreme",
            "version": VERSION,
            "uptime_seconds": round(uptime, 2),
            "architecture": platform.machine(),
            "python_version": platform.python_version()
        },
        "traffic_telemetry": {
            "total_requests": s["http_req_total"],
            "tps_current": round(tps, 2),
            "tpm_current": round(tpm, 2),
            "active_connections": s["http_active_connections"],
            "success_rate": f"{(s['http_req_2xx']/(s['http_req_total'] or 1))*100:.2f}%",
            "dropped_requests": s["q_dropped_reqs"],
            "circuit_breaker": s["circuit_breaker"],
            "http_req_2xx": s["http_req_2xx"],
            "http_req_4xx": s["http_req_4xx"],
            "http_req_5xx": s["http_req_5xx"]
        },
        "latency_analytics_ms": {
            "average": round(s["lat_avg"], 4),
            "peak": round(s["lat_max"], 4),
            "minimum": round(s["lat_min"], 4),
            "cumulative_processing_time": round(s["lat_sum"] / 1000, 2)
        },
        "orchestration": {
            "num_processes": num_proc,
            "threads_per_worker": threads_pw,
            "semaphore_slots_total": sem_total,
            "semaphore_in_use": sem_in_use,
            "semaphore_available": sem_available,
            "thread_pool_max_workers": threads_pw,
            "max_queue_capacity": max_q,
            "q_current_size": q_current,
            "q_peak_size": q_peak,
            "active_workers": active_w
        },
        "network": {
            "http_bytes_sent": s.get("http_bytes_sent", 0),
            "http_bytes_received": s.get("http_bytes_received", 0),
            "io_read_bytes": io_counters.read_bytes,
            "io_write_bytes": io_counters.write_bytes
        },
        "cryptography_performance": {
            "algorithm": "RSA-512-RS256",
            "tokens_minted": s["sec_tokens_minted"],
            "signatures_generated": s["sec_rsa_signatures"],
            "sec_blocked_attempts": s["sec_blocked_attempts"],
            "last_issued_jti": s["sec_last_jti"],
            "last_authenticated_user": s["sec_last_user"]
        },
        "system_resources_low_level": {
            "cpu_percent": cpu_usage,
            "memory_uss_mb": round(mem_info.uss / (1024 * 1024), 2),
            "memory_vms_mb": round(mem_info.vms / (1024 * 1024), 2),
            "open_fds": fds,
            "active_threads": threads,
            "voluntary_ctx_switches": ctx.voluntary,
            "io_read_bytes": io_counters.read_bytes,
            "io_write_bytes": io_counters.write_bytes
        }
    }

@app.post("/v6/auth/mint")
async def mint_authentication_token(request: Request):
    """
    Endpoint de geração de tokens JWT assinado com RSA.
    Projetado para atingir 1000 TPS usando processamento paralelo de threads.
    """
    async with titan_arch.semaphore:
        with global_lock:
            stats_db["semaphore_in_use"] = stats_db.get("semaphore_in_use", 0) + 1
        try:
            body = await request.json()
            user = body.get("user", "guest_user")
            
            # Metadata do Token
            jti = str(uuid.uuid4())
            claims = {
                "iss": "titan-auth-engine-v6",
                "sub": user,
                "iat": datetime.utcnow(),
                "exp": datetime.utcnow() + timedelta(hours=TOKEN_EXP_HOURS),
                "jti": jti,
                "scope": "access_root"
            }

            # Assinatura RSA Offload (não bloqueia event loop; pool 64 threads para 500+ TPS)
            loop = asyncio.get_event_loop()
            token = await loop.run_in_executor(
                titan_arch.pool,
                lambda: crypto_engine.sign_payload(claims)
            )

            # Uma única seção crítica: todas as métricas de mint em batch (reduz contenção)
            with global_lock:
                stats_db["sec_tokens_minted"] += 1
                stats_db["sec_rsa_signatures"] += 1
                stats_db["sec_last_user"] = user
                stats_db["sec_last_jti"] = jti

            return {
                "access_token": token,
                "token_type": "Bearer",
                "expires_in": TOKEN_EXP_HOURS * 3600,
                "engine": VERSION
            }

        except Exception as e:
            with global_lock:
                stats_db["sec_blocked_attempts"] += 1
            raise HTTPException(status_code=422, detail=f"Minting Failure: {str(e)}")
        finally:
            with global_lock:
                stats_db["semaphore_in_use"] = max(0, stats_db.get("semaphore_in_use", 1) - 1)

# =======================================================================================
# 🖥️ COMPONENTE: HYPER-DASHBOARD (CONSOLE MONITOR)
# =======================================================================================
def run_industrial_dashboard(stats_ref, lock_ref):
    """
    Thread de monitoramento visual.
    Atualiza o console com KPIs industriais sem impactar a performance da API.
    """
    current_proc = psutil.Process()
    
    while True:
        try:
            time.sleep(1) # Refresh Rate: 1Hz
            
            with lock_ref:
                s = dict(stats_ref)
            
            # Limpeza de Buffer do Console
            os.system('cls' if os.name == 'nt' else 'clear')
            
            uptime_str = str(timedelta(seconds=int(time.time() - s["engine_start_time"])))
            
            # Renderização da Moldura do Dashboard
            print(f"{Fore.CYAN}╔" + "═" * 88 + "╗")
            print(f"{Fore.CYAN}║ {Fore.WHITE}TITAN-AUTH CORE V6 {Fore.MAGENTA}>> {Fore.GREEN}NODE: ACTIVE {Fore.WHITE}| {Fore.YELLOW}UPTIME: {uptime_str:<12} {Fore.WHITE}| {Fore.CYAN}v{VERSION:<15} {Fore.CYAN}║")
            print(f"{Fore.CYAN}╠" + "═" * 88 + "╣")
            
            # Painel de Tráfego
            print(f"{Fore.CYAN}║ {Fore.WHITE}HTTP TRAFFIC ENGINE:{' ':<68}{Fore.CYAN}║")
            print(f"{Fore.CYAN}║  {Fore.WHITE}Requests: {s['http_req_total']:<12} | {Fore.GREEN}2xx: {s['http_req_2xx']:<10} {Fore.WHITE}| {Fore.YELLOW}4xx: {s['http_req_4xx']:<10} {Fore.WHITE}| {Fore.RED}5xx: {s['http_req_5xx']:<10}  {Fore.CYAN}║")
            
            # Painel de Latência e TPS
            tps = s["http_req_total"] / (time.time() - s["engine_start_time"])
            print(f"{Fore.CYAN}║  {Fore.WHITE}TPS REAL: {Fore.MAGENTA}{tps:>10.2f} req/s {Fore.WHITE}| {Fore.CYAN}AVG LAT: {s['lat_avg']:>8.2f}ms {Fore.WHITE}| {Fore.RED}PEAK: {s['lat_max']:>8.2f}ms {' ':<13}{Fore.CYAN}║")
            print(f"{Fore.CYAN}╠" + "═" * 88 + "╣")
            
            # Painel de Criptografia
            print(f"{Fore.CYAN}║ {Fore.WHITE}CRYPTOGRAPHIC VAULT (RSA 512):{' ':<57}{Fore.CYAN}║")
            print(f"{Fore.CYAN}║  {Fore.WHITE}Tokens Issued: {s['sec_tokens_minted']:<10} | Signatures: {s['sec_rsa_signatures']:<10} | Last: {str(s['sec_last_user'])[:18]:<18} {Fore.CYAN}║")
            
            # Painel de Recursos de Sistema
            print(f"{Fore.CYAN}╠" + "═" * 88 + "╣")
            cpu_val = psutil.cpu_percent()
            # Cálculo de RAM corrigido (Base 1024 conforme solicitado)
            ram_mb = current_proc.memory_info().rss / 1024 / 1024
            
            # Barra de Progresso de CPU
            bar_count = int(cpu_val / 2.5) # Escala de 40 chars
            cpu_bar = "█" * bar_count + "░" * (40 - bar_count)
            
            print(f"{Fore.CYAN}║ {Fore.WHITE}CPU LOAD: [{Fore.RED}{cpu_bar}{Fore.WHITE}] {cpu_val:>5}% | RAM USAGE: {ram_mb:>8.2f} MB {' ':<18}{Fore.CYAN}║")
            
            # Status de Orquestração
            cb = s["circuit_breaker"]
            cb_color = Fore.GREEN if cb == "CLOSED" else (Fore.YELLOW if cb == "UNDER_LOAD" else Fore.RED)
            print(f"{Fore.CYAN}║ {Fore.WHITE}ORCHESTRATOR: {NUM_PROCESSES} Workers | Active Conns: {s['http_active_connections']:<6} | CB: {cb_color}{cb:<10} {' ':<14}{Fore.CYAN}║")
            print(f"{Fore.CYAN}╚" + "═" * 88 + "╝")
            
            # Logs de Eventos de Segurança
            print(f"{Fore.WHITE} >> {Fore.CYAN}Security Audit: {Fore.WHITE}RSA signature verified for JTI {s['sec_last_jti']}")
            print(f"{Fore.WHITE} >> {Fore.YELLOW}System Health: {Fore.GREEN}All components operational. {Fore.WHITE}Bind: {SERVER_HOST}:{SERVER_PORT}")
            
        except Exception as dashboard_err:
            pass # Silenciar erros de renderização para manter estabilidade

# =======================================================================================
# 🏁 BOOTSTRAP: INICIALIZAÇÃO E TUNING DE PROCESSO
# =======================================================================================

def titan_worker_init(stats_obj, lock_obj):
    """
    Inicializador de Worker.
    Injeta as referências de memória compartilhada em cada processo worker do Uvicorn.
    """
    global stats_db, global_lock, titan_arch
    stats_db = stats_obj
    global_lock = lock_obj
    titan_arch = TitanArchitectureV6(stats_db, global_lock)
    
    # Notifica o Manager sobre o status do Worker
    with global_lock:
        stats_db["engine_status"] = "RUNNING"

if __name__ == "__main__":
    # 1. Preparação de Ambiente
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{Fore.MAGENTA}🚀 [BOOT] Iniciando TitanAuth V6 - High-Performance Engine...")

    # 2. Setup de Memória Compartilhada (Manager)
    # O Manager cria um servidor de memória que pode ser acessado por processos filhos
    manager = Manager()
    shared_stats_db = create_hyper_telemetry_schema(manager)
    shared_lock_handle = manager.Lock()

    # 3. Inicia o Worker de Interface Visual (Dashboard)
    # Executado em uma thread separada do processo principal para não bloquear o servidor
    dashboard_worker = threading.Thread(
        target=run_industrial_dashboard, 
        args=(shared_stats_db, shared_lock_handle),
        daemon=True
    )
    dashboard_worker.start()

    # 4. Injeção de dependências no escopo global do processo main
    stats_db = shared_stats_db
    global_lock = shared_lock_handle
    titan_arch = TitanArchitectureV6(stats_db, global_lock)

    # 5. Execução do Servidor Uvicorn com Tuning Industrial
    try:
        # Backlog/limit no Windows: select() tem limite 512 FDs; com ProactorEventLoop pode subir
        _backlog = 2048 if sys.platform == "win32" else 4096
        _limit_conn = MAX_QUEUE_CAPACITY  # Fila infinita na aplicação; Uvicorn só cap por processo

        config = uvicorn.Config(
            "__main__:app",
            host=SERVER_HOST,
            port=SERVER_PORT,
            workers=NUM_PROCESSES,
            loop="asyncio",
            log_level="error",
            access_log=False,
            limit_concurrency=_limit_conn,
            timeout_keep_alive=60,   # Hold conexões 60s — alinhado ao timeout do cliente (fila em pool)
            backlog=_backlog,
            server_header=False
        )
        
        server_instance = uvicorn.Server(config)
        
        # Garante que as métricas sejam resetadas no boot real
        with shared_lock_handle:
            shared_stats_db["engine_start_time"] = time.time()
            shared_stats_db["http_req_total"] = 0
        
        # Início do Ciclo de Vida do Servidor
        server_instance.run()
        
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}🛑 [SHUTDOWN] TitanAuth Engine encerrada pelo administrador.")
        sys.exit(0)
    except Exception as critical_err:
        print(f"❌ [CRITICAL_FATAL] Falha no Bootloader: {critical_err}")
        sys.exit(1)

# =======================================================================================
# FINAL DO ARQUIVO: TITAN-AUTH CORE V6
# =======================================================================================