# Titan-SKZ-Auth-API-Engine
Titan is an ZKP auth engine for api with CA and JWT for zero-trusth enviroinments

# Titan Intra Service Auth Engine

**Microserviço de autenticação intra-serviços** — emissão de tokens JWT (RSA) para autenticação entre serviços (service-to-service).

**Criado por:** Elias Andrade — **Replika AI Solutions**  
**Arquitetura:** DDD · DRY · SOLID · KISS · estado da arte, altamente modular.

---

## Visão geral

- **Produto:** Titan Intra Service Auth Engine  
- **Função:** Expor endpoints REST para emissão de tokens JWT assinados com RSA (RS256), destinados a autenticação intra-serviços.  
- **Performance:** Projetado para 500+ TPS, fila infinita (sem 503 por overload).  
- **Referência:** Comportamento alinhado à API monolítica existente na raiz do repositório; os arquivos `.PY` originais permanecem **intactos**. Este produto é uma reimplementação modular e profissional.

---

## Estrutura do projeto (inglês, DDD)

```
titan_intra_service_auth/
├── docs/           # 00-PLAN.md, ARCHITECTURE.md, RUNBOOK.md
├── src/
│   └── titan_intra_service_auth/
│       ├── config/           # Configuração centralizada
│       ├── domain/           # Entidades, value objects, domain services, events
│       ├── application/       # Use cases, ports (interfaces), DTOs
│       └── infrastructure/   # HTTP (FastAPI), crypto (RSA), observability (métricas, concorrência)
├── tests/
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

## Como rodar

```bash
cd titan_intra_service_auth
pip install -r requirements.txt
pip install -e .   # opcional: instala o pacote em modo editável
python -m titan_intra_service_auth.main
```

Ou a partir da raiz do repositório:

```bash
pip install -r titan_intra_service_auth/requirements.txt
cd titan_intra_service_auth/src && python -m titan_intra_service_auth.main
```

Servidor em **http://0.0.0.0:8000** (porta e host configuráveis por variáveis de ambiente; ver `docs/RUNBOOK.md`).

---

## Endpoints

| Método | Path | Descrição |
|--------|------|-----------|
| GET | `/health` | Liveness / readiness |
| POST | `/v6/auth/mint` | Emissão de token JWT (RSA) |
| GET | `/v6/engine/stats` | Telemetria da engine |

Documentação interativa: `/api/docs` (Swagger), `/api/redoc` (ReDoc).

---

## Princípios aplicados

- **DDD:** Bounded Context Identity & Access; camadas Domain, Application, Infrastructure; entidades, value objects, domain services, events.  
- **DRY:** Configuração única; portas reutilizáveis; sem duplicação de regras de negócio.  
- **SOLID:** Uma responsabilidade por classe; extensão por interfaces (ports); inversão de dependência (application depende de portas; infrastructure implementa).  
- **KISS:** DTOs e use cases simples; sem over-engineering.

---

## Documentação adicional

- **docs/00-PLAN.md** — Plano de arquitetura e estrutura de pastas.  
- **docs/ARCHITECTURE.md** — Diagrama de camadas e decisões (DDD, SOLID).  
- **docs/RUNBOOK.md** — Como rodar, variáveis de ambiente e operação.

---

*Titan Intra Service Auth Engine — Elias Andrade — Replika AI Solutions*
