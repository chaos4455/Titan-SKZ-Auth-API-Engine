# 🚀 RUNBOOK — TITAN INTRA SERVICE AUTH ENGINE

**Elias Andrade — Replika AI Solutions**

---

## Pré-requisitos

- Python 3.10+
- `pip install -r requirements.txt`

## Rodar a API (produto modular)

```bash
cd titan_intra_service_auth
pip install -e .
python -m titan_intra_service_auth.main
```

Ou, a partir da raiz do repositório:

```bash
pip install -r titan_intra_service_auth/requirements.txt
cd titan_intra_service_auth/src && python -m titan_intra_service_auth.main
```

## Rodar o teste de carga (monolito original)

O stress test continua usando os arquivos originais na raiz do projeto:

```bash
python CONSOLE-APP-API-SERVER-FILA-QEUE-MANAGER-POOL-AUTH-V1.PY
# Em outro terminal:
python CONSOLE-APP-API-SERVER-FILA-QEUE-MANAGER-POOL-AUTH-V1-STRESS-TEST.PY
```

Para testar o **produto modular**, suba o servidor com `python -m titan_intra_service_auth.main` (porta 8000) e aponte o stress test para `http://127.0.0.1:8000` (mesmos endpoints `/v6/auth/mint`, `/v6/engine/stats`, `/health`).

## Endpoints

| Método | Path | Descrição |
|--------|------|-----------|
| GET | /health | Liveness / readiness |
| POST | /v6/auth/mint | Emissão de token JWT (ECDSA ES256) |
| GET | /v6/engine/stats | Telemetria da engine |

## Variáveis de ambiente (opcional)

- `TITAN_HOST` — default `0.0.0.0`
- `TITAN_PORT` — default `8000`
- `TITAN_JWT_ALGORITHM` — default `ES256`
- `TITAN_TOKEN_EXP_HOURS` — default `24`
- `TITAN_UVCORN_WORKERS` — default `1` (pipeline multi-lane)
- `TITAN_THREADS_PER_WORKER` — default `32` (estilo V1, evita timeouts sob stress)
