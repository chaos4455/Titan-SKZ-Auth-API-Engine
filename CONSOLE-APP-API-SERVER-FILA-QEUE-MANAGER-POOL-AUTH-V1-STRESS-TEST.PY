# -*- coding: utf-8 -*-
"""
=========================================================================================
TITAN-STRESSOR OVERLOAD V6-ZKP - INDUSTRIAL MAGNITUDE EDITION
=========================================================================================
Framework de Injeção de Carga Distribuída e Análise de Resiliência.
Projetado para APIs ZKP (Zero Knowledge Proof) com identidades isoladas.

Arquitetura: Multi-Process Master-Worker with Asyncio Injection
Target: TitanAuth V6 ZKP — fluxo identity -> challenge -> mint
u-data: Pasta isolada por entidade/usuário/serviço (como microserviços)

Autor: Elias Andrade — Arquiteto de Soluções — Replika AI — Maringá Paraná
Micro-revisão: 000000001
=========================================================================================
"""

import asyncio
import aiohttp
import time
import uuid
import os
import sys
import random
import statistics
import multiprocessing
import threading
import json
import base64
import platform
import socket
import signal
import psutil
from pathlib import Path
from datetime import datetime, timedelta
from multiprocessing import Process, Manager, cpu_count, Lock
from typing import Dict, Any, List, Optional, Tuple
from colorama import Fore, Style, init

# ZKP: cryptography para geração de chaves e assinatura
try:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import ec
    ZKP_AVAILABLE = True
except ImportError:
    ZKP_AVAILABLE = False

# Inicialização de ambiente visual
init(autoreset=True)

# =======================================================================================
# 🔐 ZKP HELPERS — Geração de Chaves e Assinatura (compatível com CA)
# =======================================================================================
def _zkp_generate_keys() -> Tuple[str, str]:
    """Gera par ECDSA P-256. Retorna (private_pem, public_pem)."""
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()
    return private_pem, public_pem


def _zkp_sign_nonce(private_key_pem: str, nonce: str) -> str:
    """Assina nonce com chave privada. Retorna base64url."""
    private_key = serialization.load_pem_private_key(
        private_key_pem.encode(), password=None
    )
    signature = private_key.sign(
        nonce.encode(), ec.ECDSA(hashes.SHA256())
    )
    return base64.urlsafe_b64encode(signature).decode().rstrip("=")

# =======================================================================================
# ⚙️ CONFIGURAÇÕES DE ALTA INTENSIDADE (TUNING)
# =======================================================================================
class StressConfig:
    VERSION = "6.0.0-ZKP-STRESSOR"
    
    # Endpoints Alvo (API ZKP)
    TARGET_HOST = "127.0.0.1"
    TARGET_PORT = 8000
    BASE_URL = f"http://{TARGET_HOST}:{TARGET_PORT}"
    ENDPOINT_IDENTITY = f"{BASE_URL}/v6/zkp/identity"
    ENDPOINT_CHALLENGE = f"{BASE_URL}/v6/zkp/challenge"
    ENDPOINT_MINT = f"{BASE_URL}/v6/zkp/mint"
    ENDPOINT_STATS = f"{BASE_URL}/v6/engine/stats"
    
    # u-data: Pasta por usuário/entidade/serviço (como microserviços isolados)
    U_DATA_DIR = "u-data"
    NUM_IDENTITIES = 100  # Quantas identidades pré-criar para o pool de stress
    
    # Carga controlada: 2 processos, 100 conexões totais, rajada a cada 0.5s
    # Evita loucura de 8×64 injetores que gera conn_errors e failures
    NUM_ATTACKER_PROCESSES = 4
    
    # 50 conn/processo = 100 conexões totais; suficiente para 500 TPS com latência ~200ms
    CONCURRENCY_PER_PROCESS = 50

    # Rajada a cada 0.5s: 50–125 req por processo = 100–250 req a cada 0.5s = 200–500 RPS
    BURST_INTERVAL = 0.1
    MIN_BURST_SIZE = 50
    MAX_BURST_SIZE = 225

    # 60s: request em hold no pool/fila é aceitável; API enfileira e nunca quebra
    TIMEOUT_HTTP = aiohttp.ClientTimeout(total=60, connect=10, sock_read=55)
    MAX_RETRIES = 2
    
    # Tempo de Simulação
    TEST_DURATION_SECONDS = 86400 # 24 horas de estresse se necessário
    WARM_UP_PERIOD = 3            # Segundos antes de iniciar o flood

# =======================================================================================
# 📁 u-data — Identidades Isoladas por Entidade/Serviço
# =======================================================================================
async def ensure_identities(session: aiohttp.ClientSession) -> List[Dict[str, str]]:
    """
    Garante que existam NUM_IDENTITIES em u-data. Cria via API se necessário.
    Cada entidade = pasta u-data/entity_{idx}/ com identity.json.
    Retorna lista de identidades carregadas.
    """
    Path(StressConfig.U_DATA_DIR).mkdir(parents=True, exist_ok=True)
    identities = []
    
    for i in range(StressConfig.NUM_IDENTITIES):
        entity_dir = Path(StressConfig.U_DATA_DIR) / f"entity_{i}"
        identity_file = entity_dir / "identity.json"
        
        if identity_file.exists():
            try:
                with open(identity_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                identities.append(data)
                continue
            except Exception:
                pass
        
        if not ZKP_AVAILABLE:
            raise RuntimeError("cryptography não instalado. pip install cryptography")
        
        private_pem, public_pem = _zkp_generate_keys()
        
        try:
            async with session.post(
                StressConfig.ENDPOINT_IDENTITY,
                json={"pubkey_pem": public_pem, "scope": "internal.stress.test"},
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status not in (200, 201):
                    raise RuntimeError(f"Falha ao criar identidade: {resp.status}")
                data = await resp.json()
        except Exception as e:
            print(f"{Fore.RED}Erro ao criar identidade {i}: {e}")
            continue
        
        identity_id = data["identity_id"]
        entity_dir.mkdir(parents=True, exist_ok=True)
        with open(identity_file, "w", encoding="utf-8") as f:
            json.dump({
                "identity_id": identity_id,
                "pubkey_pem": public_pem,
                "private_key_pem": private_pem,
                "scope": "internal.stress.test",
                "entity_index": i,
            }, f, indent=2)
        identities.append({
            "identity_id": identity_id,
            "private_key_pem": private_pem,
            "scope": "internal.stress.test",
        })
    
    return identities


def load_identities_from_udata() -> List[Dict[str, str]]:
    """Carrega identidades da pasta u-data."""
    identities = []
    udata = Path(StressConfig.U_DATA_DIR)
    if not udata.exists():
        return identities
    for d in sorted(udata.iterdir()):
        if d.is_dir():
            f = d / "identity.json"
            if f.exists():
                try:
                    with open(f, "r", encoding="utf-8") as fp:
                        data = json.load(fp)
                    identities.append({
                        "identity_id": data["identity_id"],
                        "private_key_pem": data["private_key_pem"],
                        "scope": data.get("scope", "internal.stress.test"),
                    })
                except Exception:
                    pass
    return identities


# =======================================================================================
# 📊 TELEMETRIA COMPARTILHADA (INTER-PROCESS STATE)
# =======================================================================================
def create_industrial_stats(mgr):
    """Estrutura de dados centralizada para consolidar métricas de todos os cores."""
    return mgr.dict({
        # Contadores de Requisição
        "total_requests": 0,
        "success_2xx": 0,
        "failed_4xx": 0,
        "failed_5xx": 0,
        "conn_errors": 0,
        "timeout_errors": 0,
        
        # Monitoramento de Rede
        "bytes_sent": 0,
        "bytes_received": 0,
        "active_injectors": 0,
        
        # Telemetria de Latência (Percentis)
        "latencies": mgr.list(),
        "p95_latency": 0.0,
        "p99_latency": 0.0,
        "avg_latency": 0.0,
        
        # Controle de Estado
        "is_active": True,
        "start_time": time.time(),
        "peak_rps": 0.0,
        "current_rps": 0.0,
        "current_burst_total": 0,
        
        # Hardware do Stressor
        "stressor_cpu": 0.0,
        "stressor_ram_mb": 0.0
    })

# =======================================================================================
# ⚡ MOTOR DE INJEÇÃO (ATTACKER CORE)
# =======================================================================================
class IndustrialAttacker:
    """Motor de injeção assíncrona — fluxo ZKP: challenge -> sign -> mint."""
    
    def __init__(self, stats, lock, process_id, identities: List[Dict[str, str]]):
        self.stats = stats
        self.lock = lock
        self.process_id = process_id
        self.pid = os.getpid()
        self.identities = identities or load_identities_from_udata()
        
        self.user_agents = [
            f"TitanStressor/{StressConfig.VERSION} (ZKP-Engine; Node-{process_id})",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Golang-HttpClient/1.1",
            "Titan-Load-Injetor/V6-ZKP (Security-Audit-Mode)"
        ]

    async def execute_mint_request(self, session: aiohttp.ClientSession):
        """Fluxo ZKP: 1) GET challenge 2) assinar 3) POST mint."""
        if not self.identities:
            with self.lock:
                self.stats["total_requests"] += 1
                self.stats["conn_errors"] += 1
            return
        
        identity = random.choice(self.identities)
        identity_id = identity["identity_id"]
        private_key_pem = identity["private_key_pem"]
        scope = identity.get("scope", "internal.stress.test")
        
        headers = {
            "Content-Type": "application/json",
            "X-Titan-Stressor-ID": str(uuid.uuid4()),
            "User-Agent": random.choice(self.user_agents),
            "Connection": "keep-alive"
        }
        
        t_start = time.perf_counter()
        bytes_sent = 0
        try:
            # 1) Obter challenge (challenge_id + nonce)
            async with session.get(
                f"{StressConfig.ENDPOINT_CHALLENGE}?identity_id={identity_id}",
                headers=headers,
                timeout=StressConfig.TIMEOUT_HTTP
            ) as resp_challenge:
                if resp_challenge.status != 200:
                    raise Exception(f"Challenge failed: {resp_challenge.status}")
                ch_data = await resp_challenge.json()
                challenge_id = ch_data["challenge_id"]
                nonce = ch_data["nonce"]
            
            # 2) Assinar nonce com chave privada
            signature = _zkp_sign_nonce(private_key_pem, nonce)
            
            # 3) Mint com challenge_id + identity_id + nonce + signature
            payload = {
                "challenge_id": challenge_id,
                "identity_id": identity_id,
                "nonce": nonce,
                "signature": signature,
                "scope": scope,
            }
            bytes_sent = len(json.dumps(payload))
            
            async with session.post(
                StressConfig.ENDPOINT_MINT,
                json=payload,
                headers=headers,
                timeout=StressConfig.TIMEOUT_HTTP
            ) as response:
                resp_data = await response.read()
                latency = (time.perf_counter() - t_start) * 1000
                
                with self.lock:
                    self.stats["total_requests"] += 1
                    self.stats["bytes_sent"] += bytes_sent
                    self.stats["bytes_received"] += len(resp_data)
                    
                    if response.status in (200, 201):
                        self.stats["success_2xx"] += 1
                    elif 400 <= response.status < 500:
                        self.stats["failed_4xx"] += 1
                    else:
                        self.stats["failed_5xx"] += 1
                    
                    if len(self.stats["latencies"]) < 30000:
                        self.stats["latencies"].append(latency)

        except asyncio.TimeoutError:
            with self.lock:
                self.stats["total_requests"] += 1
                self.stats["timeout_errors"] += 1
        except Exception:
            with self.lock:
                self.stats["total_requests"] += 1
                self.stats["conn_errors"] += 1

    async def run_injection_worker(self):
        """Loop principal do worker de injeção."""
        # Otimização do TCP Connector para alta reciclagem de sockets
        connector = aiohttp.TCPConnector(
            limit=StressConfig.CONCURRENCY_PER_PROCESS,
            ttl_dns_cache=600,
            use_dns_cache=True,
            ssl=False # Desativado para maximizar RPS puro em teste local
        )
        
        async with aiohttp.ClientSession(connector=connector) as session:
            with self.lock:
                self.stats["active_injectors"] += 1
            
            while self.stats["is_active"]:
                # Definição do tamanho da rajada atual
                burst = random.randint(StressConfig.MIN_BURST_SIZE, StressConfig.MAX_BURST_SIZE)
                
                with self.lock:
                    self.stats["current_burst_total"] = burst
                
                # Disparo paralelo massivo
                injection_tasks = [self.execute_mint_request(session) for _ in range(burst)]
                await asyncio.gather(*injection_tasks)
                
                # Controle de cadência (Requisito de 0.1s)
                await asyncio.sleep(StressConfig.BURST_INTERVAL)

def start_attacker_process(shared_stats, shared_lock, proc_id, identities=None):
    """Entry point para cada processo. Carrega identidades de u-data se identities=None."""
    attacker = IndustrialAttacker(shared_stats, shared_lock, proc_id, identities or [])
    try:
        asyncio.run(attacker.run_injection_worker())
    except KeyboardInterrupt:
        pass

# =======================================================================================
# 🖥️ COMPONENTE: INDUSTRIAL DASHBOARD (REAL-TIME KPI)
# =======================================================================================
class IndustrialStressDashboard:
    """Dashboard de console para visualização de dados de alta densidade."""
    
    def __init__(self, stats, lock):
        self.stats = stats
        self.lock = lock
        self.start_time = time.time()
        self.proc_monitor = psutil.Process()

    def calculate_percentiles(self, latencies):
        """Calcula P95 e P99 para análise de cauda de latência."""
        if not latencies:
            return 0.0, 0.0, 0.0
        
        # Pega as últimas 5000 amostras para velocidade de cálculo
        sample = list(latencies)[-5000:]
        avg = statistics.mean(sample)
        
        if len(sample) > 20:
            q = statistics.quantiles(sample, n=100)
            return avg, q[94], q[98] # P95 e P99
        return avg, avg, avg

    def render_loop(self):
        """Thread de renderização da UI."""
        while self.stats["is_active"]:
            try:
                time.sleep(1) # Refresh rate: 1Hz
                
                with self.lock:
                    s = dict(self.stats)
                    lats = list(self.stats["latencies"])
                
                elapsed = time.time() - self.start_time
                current_rps = s["total_requests"] / elapsed if elapsed > 0 else 0
                
                # Hardware do Stressor
                with self.proc_monitor.oneshot():
                    self.stats["stressor_cpu"] = psutil.cpu_percent()
                    self.stats["stressor_ram_mb"] = self.proc_monitor.memory_info().rss / 1024 / 1024
                
                avg_l, p95, p99 = self.calculate_percentiles(lats)
                
                # Atualização de Recordes
                if current_rps > s["peak_rps"]:
                    with self.lock:
                        self.stats["peak_rps"] = current_rps

                # Limpeza de Tela (Cross-platform)
                os.system('cls' if os.name == 'nt' else 'clear')
                
                # --- CABEÇALHO ---
                print(f"{Fore.RED}{Style.BRIGHT}TITAN-STRESSOR OVERLOAD V6-ZKP {Fore.WHITE}| {Fore.YELLOW}STRESS LEVEL: INDUSTRIAL")
                print(f"{Fore.RED}═" * 90)
                
                # --- INFRAESTRUTURA DE CARGA ---
                print(f"{Fore.RED}║ {Fore.WHITE}LOAD ARCHITECTURE: {StressConfig.NUM_ATTACKER_PROCESSES} Processes | {StressConfig.CONCURRENCY_PER_PROCESS} Conns/Proc | {Fore.GREEN}STATUS: FLOODING")
                print(f"{Fore.RED}║ {Fore.WHITE}TARGET ENDPOINT:   {StressConfig.ENDPOINT_MINT}")
                print(f"{Fore.RED}╠" + "═" * 88 + "╣")
                
                # --- CONTADORES HTTP ---
                print(f"{Fore.RED}║ {Fore.WHITE}HTTP METRICS:{' ':<75}{Fore.RED}║")
                print(f"{Fore.RED}║  {Fore.WHITE}Requests Total: {s['total_requests']:<12} | {Fore.GREEN}Success 2xx: {s['success_2xx']:<10} | {Fore.RED}Failures: {s['conn_errors'] + s['failed_5xx']:<10} {Fore.RED}║")
                print(f"{Fore.RED}║  {Fore.CYAN}RPS CURRENT: {current_rps:>12.2f} | {Fore.YELLOW}RPS PEAK: {s['peak_rps']:>12.2f} | {Fore.RED}Timeouts: {s['timeout_errors']:<10} {Fore.RED}║")
                
                # --- TELEMETRIA DE LATÊNCIA ---
                print(f"{Fore.RED}╠" + "═" * 88 + "╣")
                print(f"{Fore.RED}║ {Fore.WHITE}LATENCY TELEMETRY (ms):{' ':<64}{Fore.RED}║")
                print(f"{Fore.RED}║  {Fore.CYAN}Avg Latency: {avg_l:>10.2f}ms | {Fore.YELLOW}P95 (Tail): {p95:>10.2f}ms | {Fore.RED}P99 (Worst): {p99:>10.2f}ms {Fore.RED}║")
                
                # --- NETWORK & BANDWIDTH ---
                mb_sent = s["bytes_sent"] / (1024 * 1024)
                mb_recv = s["bytes_received"] / (1024 * 1024)
                print(f"{Fore.RED}║  {Fore.WHITE}Network Sent: {mb_sent:>10.2f} MB | Network Received: {mb_recv:>10.2f} MB {' ':<26}{Fore.RED}║")
                
                # --- HEALTH BAR DA API ALVO ---
                success_rate = (s["success_2xx"] / (s["total_requests"] or 1)) * 100
                bar_len = int(success_rate / 2.5)
                h_color = Fore.GREEN if success_rate > 90 else Fore.YELLOW if success_rate > 60 else Fore.RED
                bar = "█" * bar_len + "░" * (40 - bar_len)
                
                print(f"{Fore.RED}╠" + "═" * 88 + "╣")
                print(f"{Fore.RED}║ {Fore.WHITE}TARGET RESILIENCE: [{h_color}{bar}{Fore.WHITE}] {success_rate:>6.2f}% {' ':<25}{Fore.RED}║")
                
                # --- HARDWARE DO STRESSOR ---
                print(f"{Fore.RED}║ {Fore.WHITE}STRESSOR LOCAL LOAD: CPU {s['stressor_cpu']:>5}% | RAM {s['stressor_ram_mb']:>8.2f} MB {' ':<32}{Fore.RED}║")
                print(f"{Fore.RED}╚" + "═" * 88 + "╝")
                
                # --- LOGS DE EVENTO ---
                print(f"{Fore.WHITE} >> {Fore.LIGHTBLACK_EX}Worker Event: Injection Burst of {s['current_burst_total']} packets from {StressConfig.NUM_ATTACKER_PROCESSES} cores.")
                print(f"{Fore.WHITE} >> {Fore.LIGHTBLACK_EX}Test Duration: {str(timedelta(seconds=int(elapsed)))} | Protocol: RSA-512-V6")

            except Exception as e:
                pass

# =======================================================================================
# 🏁 BOOTSTRAP: INICIALIZAÇÃO DO FRAMEWORK
# =======================================================================================

async def preflight_api_check():
    """Valida se o alvo está online e qual versão está rodando."""
    print(f"{Fore.CYAN}🔍 [PREFLIGHT] Investigando alvo em {StressConfig.BASE_URL}...")
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(StressConfig.ENDPOINT_STATS, timeout=5) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    version = data.get("engine_metadata", {}).get("version", "Unknown")
                    print(f"{Fore.GREEN}✅ [ALVO ONLINE] Engine: {version} detectada.")
                    return True
                else:
                    print(f"{Fore.RED}❌ [ERRO] API respondeu com status {resp.status}.")
                    return False
        except Exception as e:
            print(f"{Fore.RED}❌ [FALHA] Não foi possível conectar ao TitanAuth V6. Verifique o servidor.")
            return False

def main():
    """Função principal de orquestração do estresse."""
    # Limpeza de Buffer Inicial
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Banner ASCII Industrial
    print(f"{Fore.RED}{Style.BRIGHT}" + r"""
  _______ _____ _______       _   _    _____ _______ _____  ______  _____ _____  ____  _____  
 |__   __|_   _|__   __|     | \ | |  / ____|__   __|  __ \|  ____|/ ____/ ____|/ __ \|  __ \ 
    | |    | |    | |   ____ |  \| | | (___    | |  | |__) | |__  | (___| (___ | |  | | |__) |
    | |    | |    | |  |____|| . ` |  \___ \   | |  |  _  /|  __|  \___ \\___ \| |  | |  _  / 
    | |   _| |_   | |        | |\  |  ____) |  | |  | | \ \| |____ ____) |___) | |__| | | \ \ 
    |_|  |_____|  |_|        |_| \_| |_____/   |_|  |_|  \_\______|_____/_____/ \____/|_|  \_\
    """)
    print(f"{Fore.WHITE} >> Version: {StressConfig.VERSION} | Core: Industrial Load Injection | Protocol: RSA-512")
    print(f"{Fore.WHITE} >> System: {platform.system()} {platform.release()} | Cores: {cpu_count()}")
    print("-" * 90)

    # 1. Verificação de Disponibilidade
    if not asyncio.run(preflight_api_check()):
        sys.exit(1)

    print(f"{Fore.YELLOW}🚀 [WARM-UP] Preparando motores de injeção... ({StressConfig.WARM_UP_PERIOD}s)")
    time.sleep(StressConfig.WARM_UP_PERIOD)

    # 1.5. ZKP: Garantir identidades em u-data (criar via API se necessário)
    print(f"{Fore.CYAN}🔐 [ZKP] Garantindo {StressConfig.NUM_IDENTITIES} identidades em u-data/...")
    try:
        async def bootstrap_identities():
            async with aiohttp.ClientSession() as sess:
                return await ensure_identities(sess)
        ids = asyncio.run(bootstrap_identities())
        print(f"{Fore.GREEN}✅ [ZKP] {len(ids)} identidades prontas em u-data/")
    except Exception as e:
        print(f"{Fore.RED}❌ [ZKP] Erro ao criar identidades: {e}")
        print(f"{Fore.YELLOW}   Verifique se a API está rodando e se /v6/zkp/identity existe.")
        sys.exit(1)

    # 2. Setup de Estado Compartilhado (Manager)
    manager = Manager()
    industrial_stats = create_industrial_stats(manager)
    industrial_lock = manager.Lock()

    # 3. Inicialização dos Injetores de Carga (Workers)
    injectors = []
    for i in range(StressConfig.NUM_ATTACKER_PROCESSES):
        p = Process(
            target=start_attacker_process, 
            args=(industrial_stats, industrial_lock, i)
        )
        p.daemon = True # Garante que os filhos morram com o pai
        p.start()
        injectors.append(p)

    # 4. Inicialização do Monitor de Telemetria (Dashboard)
    dashboard = IndustrialStressDashboard(industrial_stats, industrial_lock)
    ui_thread = threading.Thread(target=dashboard.render_loop, daemon=True)
    ui_thread.start()

    # 5. Loop de Monitoramento de Vida do Processo
    try:
        # Mantém o processo principal vivo enquanto o teste ocorre
        while True:
            time.sleep(10)
            # Verifica se algum processo worker morreu inesperadamente
            for i, p in enumerate(injectors):
                if not p.is_alive():
                    print(f"{Fore.RED}⚠️ [ALERTA] Injetor de carga {i} falhou. Reiniciando...")
                    new_p = Process(
                        target=start_attacker_process, 
                        args=(industrial_stats, industrial_lock, i)
                    )
                    new_p.start()
                    injectors[i] = new_p

    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}🛑 [SHUTDOWN] Interrupção detectada. Encerrando injeção de carga...")
    finally:
        # Finalização Limpa
        industrial_stats["is_active"] = False
        for p in injectors:
            p.terminate()
            p.join(timeout=2)
        
        # Relatório de Sumário Final
        print(f"\n{Fore.GREEN}🏁 [TESTE CONCLUÍDO]")
        print(f"{Fore.WHITE}Duração Total: {str(timedelta(seconds=int(time.time() - industrial_stats['start_time'])))}")
        print(f"{Fore.WHITE}Requisições Disparadas: {industrial_stats['total_requests']}")
        print(f"{Fore.WHITE}RPS Médio Alcançado: {industrial_stats['total_requests'] / (time.time() - industrial_stats['start_time']):.2f}")
        print(f"{Fore.WHITE}Sucesso (2xx): {Fore.GREEN}{industrial_stats['success_2xx']}")
        print(f"{Fore.WHITE}Falhas/Timeouts: {Fore.RED}{industrial_stats['total_requests'] - industrial_stats['success_2xx']}")
        print(f"{Fore.CYAN}Obrigado por usar o Titan-Stressor Overload V6.")

if __name__ == "__main__":
    # Garante suporte a Multiprocessing no Windows
    multiprocessing.freeze_support()
    main()