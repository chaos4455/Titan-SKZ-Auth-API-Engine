# 🏗️ ARQUITETURA — TITAN INTRA SERVICE AUTH ENGINE

**Produto:** Titan Intra Service Auth Engine  
**Autor:** Elias Andrade — Replika AI Solutions

---

## 1. VISÃO DE ALTO NÍVEL

```
                    ┌─────────────────────────────────────────────────────────┐
                    │                  PRESENTATION (HTTP)                     │
                    │  FastAPI App · Routes · Middleware (Telemetry)            │
                    └───────────────────────────┬───────────────────────────────┘
                                                │
                    ┌───────────────────────────▼───────────────────────────────┐
                    │                  APPLICATION (USE CASES)                   │
                    │  MintTokenUseCase  (orchestrates domain + ports)          │
                    └───────────────────────────┬───────────────────────────────┘
                                                │
         ┌──────────────────────────────────────┼──────────────────────────────────────┐
         │                                      │                                      │
         ▼                                      ▼                                      ▼
┌─────────────────┐                 ┌─────────────────┐                 ┌─────────────────┐
│   DOMAIN        │                 │  PORTS          │                 │  INFRASTRUCTURE  │
│   Entities      │                 │  CryptoPort     │◄────────────────│  RsaSignerAdapter│
│   Value Objects │                 │  MetricsPort    │◄────────────────│  SharedMetrics   │
│   Domain Svc    │                 │  ConcurrencyPort│◄────────────────│  Concurrency     │
│   Events        │                 │                 │                 │  Adapter         │
└─────────────────┘                 └─────────────────┘                 └─────────────────┘
```

- **Domain:** regras de negócio puras (claims, identidade, evento de token mintado).  
- **Application:** orquestração via use cases; depende apenas de **portas** (interfaces).  
- **Infrastructure:** implementações concretas (RSA, métricas compartilhadas, pool/semáforo).  
- **Presentation:** FastAPI, rotas e middleware; chama use cases e adapters injetados.

---

## 2. DDD — BOUNDED CONTEXT

- **Contexto:** Identity & Access (Intra-Service Auth).  
- **Agregados:** não persistência de domínio neste MVP; o “agregado” é a emissão de um token (Transaction Script / Domain Service).  
- **Entidades:** TokenClaim (claims + identidade).  
- **Value Objects:** UserIdentity, Jti.  
- **Domain Service:** TokenMintingDomainService (monta claims; assinatura delegada à porta).  
- **Domain Event:** TokenMinted (para futura auditoria ou integração).

---

## 3. SOLID

| Letra | Aplicação |
|-------|-----------|
| **S** | Cada classe um propósito: `MintTokenUseCase` só orquestra mint; `RsaSignerAdapter` só assina; `SharedMetricsAdapter` só grava métricas. |
| **O** | Novos algoritmos de assinatura = novo adapter implementando `CryptoPort`; novo backend de métricas = novo adapter para `MetricsPort`. |
| **L** | Qualquer implementação de `CryptoPort` pode ser trocada sem quebrar o use case. |
| **I** | Portas enxutas: `CryptoPort.sign(payload) -> str`; `MetricsPort.record_mint(...)`; sem interfaces “gordas”. |
| **D** | Use case recebe `CryptoPort`, `MetricsPort`, `ConcurrencyPort` por construtor; não conhece FastAPI nem multiprocessing. |

---

## 4. DRY E KISS

- Configuração única em `config/settings.py` (versão, portas, tamanho de chave, workers, etc.).  
- Lógica de “como montar claims” em um único lugar (domain service ou value objects).  
- Use case único para mint; rotas HTTP apenas traduzem request/response em DTOs e chamam o use case.  
- KISS: sem CQRS/Event Sourcing neste MVP; sem camada de repositório até haver persistência.

---

## 5. FLUXO DO MINT (SEQ)

1. Cliente POST `/v6/auth/mint` com `{ "user", "scope", ... }`.  
2. **auth_routes** → valida corpo, monta `MintRequestDTO` → chama `MintTokenUseCase.execute(dto)`.  
3. **MintTokenUseCase** → adquire slot de concorrência (`ConcurrencyPort`) → monta claims (domain) → chama `CryptoPort.sign(claims)` (async offload) → `MetricsPort.record_mint(...)` → retorna `MintResponseDTO`.  
4. **auth_routes** → converte DTO em JSON response.  
5. **Middleware** já terá registrado request/response (métricas de HTTP) via `MetricsPort`.

---

## 6. TECNOLOGIAS E DEPENDÊNCIAS

- **Runtime:** Python 3.10+.  
- **Web:** FastAPI, Uvicorn.  
- **Crypto:** PyJWT, cryptography (RSA).  
- **Observabilidade:** multiprocessing.Manager (shared dict + Lock), psutil.  
- **Windows:** ProactorEventLoop para evitar limite de 512 FDs em select().

---

---

## 7. ZKP — ZERO KNOWLEDGE PROOF (v6.0.0+)

A API suporta autenticação ZKP via rotas `/v6/zkp/*`:

- **POST /v6/zkp/identity** — Cliente envia pubkey, recebe identity_id
- **GET /v6/zkp/challenge** — Obtém nonce para assinar
- **POST /v6/zkp/mint** — Prova posse via assinatura, recebe token

O **CA (Certificate Authority)** é componente isolado (`infrastructure/ca/`) que:
- Persiste pubkeys em SQLite ZKP
- Verifica assinaturas (prova de posse)
- Determina quem pode obter token

A API **não conhece a identidade real** — apenas valida via CA. Subject do JWT = identity_id (UUID).

Ver `docs/NOTAS-ZKP-CA.md` para detalhes.

---

*Arquitetura — Titan Intra Service Auth Engine — Elias Andrade — Replika AI Solutions.*
