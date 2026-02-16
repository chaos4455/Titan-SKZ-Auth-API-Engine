# 📋 PLANO DE ARQUITETURA — TITAN INTRA SERVICE AUTH ENGINE

**Produto:** Titan Intra Service Auth Engine  
**Autor:** Elias Andrade — Replika AI Solutions  
**Objetivo:** Microserviço de autenticação intra-serviços, estado da arte, DDD/DRY/SOLID/KISS.

---

## 1. VISÃO GERAL DO PRODUTO

- **Nome:** Titan Intra Service Auth Engine  
- **Função:** Emissão de tokens JWT (RSA) para autenticação entre microserviços (service-to-service).  
- **Performance target:** 500+ TPS, fila infinita, sem 503 por overload.  
- **Referência comportamental:** API monolítica existente (arquivos `.PY` na raiz do repositório) permanecem **intactos**; este produto é uma reimplementação modular e profissional.

---

## 2. PRINCÍPIOS APLICADOS

| Princípio | Aplicação |
|-----------|-----------|
| **DDD** | Bounded Context: Identity & Access. Camadas Domain, Application, Infrastructure. Entidades, Value Objects, Domain Services, Domain Events. |
| **DRY** | Configuração única (`config/settings`), portas reutilizáveis, sem duplicação de lógica de negócio. |
| **SOLID** | **S** — Uma responsabilidade por classe. **O** — Extensão por portas/interfaces. **L** — Substituibilidade de adapters. **I** — Portas pequenas e específicas. **D** — Inversão: Application depende de portas; Infrastructure implementa. |
| **KISS** | Entradas/saídas simples (DTOs), use cases com um fluxo claro, sem over-engineering. |

---

## 3. ESTRUTURA DE PASTAS (NOMES EM INGLÊS)

```
titan_intra_service_auth/
├── .vscode/                          # VS Code workspace (opcional)
│   └── settings.json
├── docs/
│   ├── 00-PLAN.md                    # Este plano
│   ├── ARCHITECTURE.md                # Diagrama e decisões
│   └── RUNBOOK.md                     # Como rodar e operar
├── src/
│   └── titan_intra_service_auth/      # Pacote Python principal
│       ├── __init__.py
│       ├── main.py                    # Entrada da aplicação (wire + run)
│       ├── config/                    # Configuração centralizada
│       │   ├── __init__.py
│       │   └── settings.py
│       ├── domain/                    # Camada de domínio (DDD)
│       │   ├── __init__.py
│       │   ├── entities/
│       │   │   ├── __init__.py
│       │   │   └── token_claim.py
│       │   ├── value_objects/
│       │   │   ├── __init__.py
│       │   │   ├── user_identity.py
│       │   │   └── jti.py
│       │   ├── services/
│       │   │   ├── __init__.py
│       │   │   └── token_minting_domain_service.py
│       │   └── events/
│       │       ├── __init__.py
│       │       └── token_minted.py
│       ├── application/              # Camada de aplicação (use cases)
│       │   ├── __init__.py
│       │   ├── use_cases/
│       │   │   ├── __init__.py
│       │   │   └── mint_token.py
│       │   ├── ports/                 # Interfaces (abstrações)
│       │   │   ├── __init__.py
│       │   │   ├── crypto_port.py
│       │   │   ├── metrics_port.py
│       │   │   └── concurrency_port.py
│       │   └── dtos/
│       │       ├── __init__.py
│       │       ├── mint_request.py
│       │       └── mint_response.py
│       └── infrastructure/            # Adaptadores (implementações)
│           ├── __init__.py
│           ├── http/
│           │   ├── __init__.py
│           │   ├── fastapi_app.py
│           │   ├── routes/
│           │   │   ├── __init__.py
│           │   │   ├── auth_routes.py
│           │   │   ├── health_routes.py
│           │   │   └── stats_routes.py
│           │   └── middleware/
│           │       ├── __init__.py
│           │       └── telemetry_middleware.py
│           ├── crypto/
│           │   ├── __init__.py
│           │   └── rsa_signer_adapter.py
│           └── observability/
│               ├── __init__.py
│               ├── shared_metrics_adapter.py
│               └── concurrency_adapter.py
├── tests/
│   ├── __init__.py
│   ├── unit/
│   └── integration/
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

## 4. FLUXO DE DEPENDÊNCIAS (INVERSÃO)

- **main.py** → monta a aplicação: lê `config`, instancia **adapters** (infrastructure), instancia **use cases** (application) injetando **ports** (interfaces).
- **Application** não importa **Infrastructure**; **Infrastructure** implementa **Ports** definidas em **Application**.
- **Domain** não depende de nenhuma camada externa; pode ser testado em isolamento.

---

## 5. MAPEAMENTO FUNCIONAL (MONOLITO → PRODUTO)

| Monolito (V1.PY)           | Produto (DDD) |
|---------------------------|----------------|
| CryptoVaultV6              | `CryptoPort` → `RsaSignerAdapter` |
| TitanArchitectureV6 (pool, semaphore) | `ConcurrencyPort` → `ConcurrencyAdapter` |
| create_hyper_telemetry_schema + Lock | `MetricsPort` → `SharedMetricsAdapter` |
| /health                    | `health_routes.py` |
| /v6/auth/mint               | `MintTokenUseCase` + `auth_routes.py` |
| /v6/engine/stats            | `stats_routes.py` (lê MetricsPort) |
| supreme_telemetry_middleware | `telemetry_middleware.py` (usa MetricsPort) |
| Bootstrap (uvicorn, Manager, dashboard) | `main.py` + `fastapi_app.py` |

---

## 6. CONVENÇÕES E ICONES (VS CODE)

- Pastas com nomes em inglês e kebab-case ou snake_case conforme padrão Python (`value_objects`, `use_cases`).
- Para ícones no VS Code: usar extensão **vscode-icons** ou **Material Icon Theme**; pastas como `src`, `tests`, `docs` já possuem ícones padrão. Nenhum sufixo especial necessário.

---

## 7. ENTREGÁVEIS

1. Documentação: `00-PLAN.md`, `ARCHITECTURE.md`, `RUNBOOK.md`.  
2. Código modular em `src/titan_intra_service_auth/` com Domain, Application, Infrastructure.  
3. `main.py` como único ponto de entrada (wire + uvicorn).  
4. `README.md` do produto com créditos (Elias Andrade, Replika AI Solutions).  
5. `requirements.txt` e `pyproject.toml` para instalação e ambiente.

---

*Documento de planejamento — Titan Intra Service Auth Engine — Elias Andrade — Replika AI Solutions.*
