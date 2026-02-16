# 🛡️ Titan-SKZ-Auth-API-Engine

<img width="1536" height="1024" alt="ChatGPT Image 15 de fev  de 2026, 23_08_34" src="https://github.com/user-attachments/assets/77bb56ed-e359-4016-87b8-99ce674030ff" />


<p align="center">
  <img src="https://img.shields.io/badge/Status-Production--Ready-blueviolet?style=for-the-badge&logo=checkmarx" alt="Status">
  <img src="https://img.shields.io/badge/Architecture-DDD%20%2F%20Hexagonal-9b59b6?style=for-the-badge&logo=architecture" alt="Architecture">
  <img src="https://img.shields.io/badge/Crypto-ECDSA--ES256%20%2F%20ZKP-a29bfe?style=for-the-badge&logo=esotericsoftware" alt="Cryptography">
  <img src="https://img.shields.io/badge/Performance-%3E117%20TPS-6c5ce7?style=for-the-badge&logo=speedtest" alt="Performance">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Security-Zero--Trust-8e44ad?style=flat-square&logo=shield" alt="Zero Trust">
  <img src="https://img.shields.io/badge/Identity-Autonomous%20CA-7d5fff?style=flat-square&logo=keybase" alt="Identity">
  <img src="https://img.shields.io/badge/Framework-FastAPI%20%2F%20Python-663399?style=flat-square&logo=fastapi" alt="Framework">
  <img src="https://img.shields.io/badge/Data%20Sovereignty-O2%20Data%20Solutions-purple?style=flat-square" alt="O2 Data Solutions">
</p>

---

## 📑 Sumário Executivo

O **Titan Intra Service Auth Engine** é um framework de autenticação de missão crítica projetado para ambientes onde a confiança mútua é inexistente (**Zero Trust**). Diferente de sistemas tradicionais baseados em segredos compartilhados (API Keys) ou senhas estáticas, o Titan implementa um protocolo de **Prova de Conhecimento Zero (ZKP)** customizado para comunicação *Service-to-Service* (S2S).

Utilizando o algoritmo **ECDSA (ES256)** sobre uma arquitetura **Domain-Driven Design (DDD)**, o motor garante que credenciais privadas jamais transitem pela rede, mitigando vetores de ataque como interceptação de tráfego, vazamento de base de dados de segredos e ataques de repetição.

---

## 🚀 O Que Faz?

*   **Autenticação Passwordless S2S:** Elimina a necessidade de armazenar "Client Secrets" em arquivos de configuração ou variáveis de ambiente.
*   **Emissão de Tokens JWT Stateless:** Gera tokens assinados via RSA/ECDSA de alta performance para autorização granular.
*   **Autoridade Certificadora (CA) Autônoma:** Gerencia o ciclo de vida de identidades (registro e revogação) de forma isolada.
*   **Pipeline Multi-Lane:** Processamento criptográfico paralelo que contorna o Global Interpreter Lock (GIL) para sustentar cargas industriais.

---

## 🧠 Por Que ZKP (Zero-Knowledge Proof)?

Em arquiteturas de microsserviços modernas, se uma chave de API estática é comprometida, o atacante ganha acesso total. O Titan resolve isso através da **Prova de Posse**:
1.  O serviço **não envia sua chave**.
2.  O serviço **prova que possui a chave** resolvendo um desafio matemático (Nonce) gerado pelo Titan.
3.  O Titan verifica a prova usando a **Chave Pública** previamente registrada na CA.

**Resultado:** Segurança criptográfica absoluta com overhead de latência desprezível.

---

## 🛠️ Arquitetura e Conceitos de Implementação

O projeto segue os rigorosos padrões da **Arquitetura Hexagonal (Ports & Adapters)**, garantindo que a lógica de negócio seja imune a mudanças tecnológicas na infraestrutura.

### 🏛️ Camadas de Domínio
*   **Domain Layer:** Define entidades puras (`UserIdentity`, `TokenClaim`) e a lógica de construção do payload criptográfico.
*   **Application Layer:** Orquestra os casos de uso, como o `MintTokenUseCase`, gerenciando o fluxo entre a prova e a emissão.
*   **Infrastructure Layer:** Implementa adaptadores concretos para `FastAPI`, persistência `SQLite` e telemetria em tempo real.

### 🔐 O Fluxo Criptográfico (3-Step Logic)
1.  **Challenge:** O cliente solicita um desafio (`/v6/zkp/challenge`). O Titan gera um Nonce de alta entropia.
2.  **Proof:** O cliente assina o Nonce localmente com sua **Chave Privada** (que nunca sai de sua memória).
3.  **Verification:** O cliente envia a assinatura. O Titan recupera a chave pública na CA e valida a autenticidade. Se válido, emite o JWT.

---

## 📊 Benchmarks & Performance (Mundo Real)

Baseado em testes de estresse empíricos com o dashboard **Titan Omniscience V9-ZKP**:

| Métrica | Valor | Icon |
| :--- | :--- | :---: |
| **Taxa de Sucesso** | 100,00% | ✅ |
| **Rendimento (Throughput)** | 117.04 TPS | ⚡ |
| **Latência Mínima** | 1.49 ms | ⏱️ |
| **Requisições Processadas** | 41.109 | 📈 |
| **Pegada de Memória (USS)** | 71.39 MB | 🧠 |
| **Threads Ativas** | 34 | 🧵 |

---

## 💼 Cenários de Aplicação S2S

*   **🏦 Fintech & Open Banking:** Proteção de serviços de ledger e gateways de transação onde a identidade deve ser absoluta.
*   **🏭 IoT Industrial (IIoT):** Dispositivos de borda que precisam se autenticar na nuvem sem armazenar segredos vulneráveis em hardware local.
*   **🌐 Redes Zero Trust:** Proteção contra movimento lateral em Data Centers, exigindo prova criptográfica para cada chamada interna.

---

## 🛠️ Stack Tecnológica

*   **Linguagem:** Python 3.12+ (Asyncio/High-Concurrency)
*   **Web Framework:** FastAPI (Uvicorn/Gunicorn)
*   **Criptografia:** Cryptography.io (ECDSA P-256 / ES256)
*   **Persistência:** SQL Alchemy / SQLite (Caching de Identidade)
*   **Observabilidade:** SharedMetrics (Prometheus-like telemetry)

---

graph TB
    subgraph CLIENT_ZONE [Consumer Service / Edge Node]
        direction TB
        K_STORE[Client Private Key - Memory Only]
        SIGNER[Local ECDSA Signer]
    end

    subgraph TITAN_ENGINE [Titan Intra-Service Auth Engine]
        direction TB
        
        subgraph INFRA [Infrastructure Layer - Adapters]
            API_GW[FastAPI REST Gateway]
            TELEMETRY[Telemetry Middleware]
            CRYPTO_ADAPTER[EcdsaSignerAdapter]
            SQL_ADAPTER[SQLite / Persistence Adapter]
        end

        subgraph APP [Application Layer - Orchestration]
            direction LR
            CHALLENGE_UC[ChallengeUseCase]
            MINT_UC[MintTokenUseCase]
            PORT_AUTH[Authentication Ports]
        end

        subgraph DOMAIN [Domain Layer - Business Logic]
            IDENTITY[UserIdentity ENTITY]
            NONCE_GEN[Nonce / Challenge VO]
            JWT_ENTITY[TokenClaim ENTITY]
        end

        subgraph PIPELINE [Multi-Lane Performance Pipeline]
            ASYNC_LOOP((AsyncIO Event Loop))
            THREAD_POOL[[ThreadPoolExecutor - CPU Crypto]]
            SEMAPHORE{Async Semaphore}
        end
    end

    subgraph TRUST_ZONE [Autonomous CA - Root of Trust]
        CA_CORE[Autonomous CA Engine]
        PUB_STORE[(Public Key Registry)]
    end

    %% ZKP Handshake Logic
    SIGNER -- "1. Request Challenge (IdentityID)" --> API_GW
    API_GW --> CHALLENGE_UC
    CHALLENGE_UC --> NONCE_GEN
    NONCE_GEN -- "Return Nonce (High Entropy)" --> SIGNER

    SIGNER -- "2. Proof of Possession (Signature + Nonce)" --> API_GW
    API_GW --> SEMAPHORE
    SEMAPHORE --> MINT_UC
    MINT_UC --> PORT_AUTH
    PORT_AUTH -- "Verify Key Identity" --> CA_CORE
    CA_CORE <--> PUB_STORE

    MINT_UC -- "Offload Crypto to CPU Lane" --> THREAD_POOL
    THREAD_POOL --> CRYPTO_ADAPTER
    CRYPTO_ADAPTER -- "3. Validated Handshake" --> JWT_ENTITY
    JWT_ENTITY -- "Issue Stateless JWT" --> SIGNER

    %% Styling
    style TITAN_ENGINE fill:#fdfaff,stroke:#8e44ad,stroke-width:2px
    style DOMAIN fill:#fff9e6,stroke:#f1c40f,stroke-width:1px
    style TRUST_ZONE fill:#f0fff0,stroke:#27ae60,stroke-width:2px
    style CLIENT_ZONE fill:#f4f7ff,stroke:#2980b9,stroke-width:2px
    style PIPELINE fill:#fff5f5,stroke:#e74c3c,stroke-dasharray: 5 5
    
    classDef tech fill:#fff,stroke:#333,stroke-width:1px,font-size:10px;
    class ASYNC_LOOP,THREAD_POOL,SEMAPHORE tech;

---

## 📂 Estrutura de Pastas (DDD Standard)

```bash
titan_intra_service_auth/
├── src/
│   └── titan_intra_service_auth/
│       ├── domain/          # 🧩 Core Business Logic (Identidades, Claims)
│       ├── application/     # ⚙️ Use Cases (Minting, Challenge Orchestration)
│       └── infrastructure/  # 🔌 Adapters (ECDSA, FastAPI, Persistence)
├── docs/                    # 📖 Architecture, Runbook, Plans
├── tests/                   # 🧪 Unit & Integration Tests
└── requirements.txt         # 📦 Dependencies
```

---

## 🏁 Como Executar

1.  **Instalação:**
    ```bash
    pip install -r requirements.txt
    ```
2.  **Inicialização do Motor:**
    ```bash
    python -m titan_intra_service_auth.main
    ```
3.  **Documentação API:**
    Acesse `http://localhost:8000/api/docs` para o Swagger interativo.

---

## 👨‍💻 Autor & Visão

**Elias Andrade**  
*Lead Architect - Replika AI Solutions | O2 Data Solutions*

Este projeto faz parte da suíte de soluções proprietárias da o2 data solutions, focada em soberania criptográfica e resiliência de alta magnitude. A implementação prova que a "Ausência de Senhas" é o próximo passo evolutivo para infraestruturas digitais escaláveis.

---
<p align="center">
  <sub>© 2026 Replika AI Solutions - Maringá, PR, Brasil.</sub>
</p>
