# Notas: Pipeline Multi-Lane e Migração RSA → ECDSA (ES256)

**Autor:** Elias Andrade — Arquiteto de Soluções — Replika AI — Maringá Paraná  
**Versão:** 6.0.0 — Micro-revisão 000000001  
**Objetivo:** Restaurar ~100 TPS com ECDSA ES256, replicando a **lógica do V1 monólito** (semáforo + pool de threads) em 1 processo.

---

## 1. Contexto do problema

- **Antes:** API com 1 processo e crypto RSA atingia ~100 TPS (lógica do CONSOLE-APP...V1.PY).
- **Depois (multi worker agressivo):** Vários processos + muitas threads **gargalaram** (TPS caiu para ~20, timeouts).
- **Causa:** Conteção em Manager/lock entre processos; 2 threads apenas gerou fila e timeout.
- **Solução:** Manter **1 processo**, aumentar **pool de threads** (16) e **slots** (32), mesma **lógica** do V1: semáforo → run_in_executor(pool, sign) → métricas.

---

## 2. Decisões de arquitetura

### 2.1 Orquestração estilo V1 (1 processo, N threads)

- **1 processo (Uvicorn worker):** Evita Manager e lock entre processos; uma lane receive → mint → respond.
- **32 threads no pool de crypto:** Metade do V1 (64); evita timeouts sob stress (4 proc × 50 conn).
- **64 slots de semáforo (THREADS × 2):** Fila curta como no monólito; quem passa do semáforo usa o executor.
- **ConcurrencyAdapter:** usa `asyncio.get_running_loop()` (não `get_event_loop()`) para evitar travamento no Windows/Proactor.

Configuração default em `config/settings.py`:

- `UVCORN_WORKERS = 1`
- `THREADS_PER_WORKER = 32`
- `SEMAPHORE_MULTIPLIER = 2` → 64 slots
- `_MINT_SLOT_TIMEOUT_SEC = 60` (alinhado ao keep_alive do V1)

### 2.2 Criptografia: ECDSA ES256 (curva P-256)

- **Algoritmo:** ES256 (ECDSA com SHA-256 na curva **P-256 / SECP256R1**).
- **Vantagens:** Melhor performance que RSA 512 para assinatura, tokens menores, segurança adequada para JWT.
- **Implementação:** `EcdsaSignerAdapter` em `infrastructure/crypto/ecdsa_signer_adapter.py`; implementa `CryptoPort` (mesma interface do antigo RSA).

---

## 3. Arquivos alterados / criados

| Arquivo | Alteração |
|--------|------------|
| `infrastructure/crypto/ecdsa_signer_adapter.py` | **Novo** — adapter ECDSA ES256 (P-256). |
| `infrastructure/crypto/__init__.py` | Exporta `EcdsaSignerAdapter`; mantém `RsaSignerAdapter` (legado). |
| `config/settings.py` | ES256 como algoritmo default; 1 worker, 2 threads; removido `RSA_KEY_SIZE`; `TITAN_JWT_ALGORITHM` via env. |
| `infrastructure/http/fastapi_app.py` | Wire com `EcdsaSignerAdapter(algorithm=settings.JWT_ALGORITHM)`. |
| `infrastructure/observability/shared_metrics_adapter.py` | Métrica `sec_rsa_signatures` renomeada para `sec_signatures` (genérico). |
| `infrastructure/http/routes/stats_routes.py` | Resposta de crypto: `algorithm: "ECDSA-ES256"`, `signatures_generated` usa `sec_signatures`. |
| `infrastructure/observability/concurrency_adapter.py` | Comentários atualizados para ECDSA e pipeline 1 proc + 2 threads. |
| `main.py` | Mensagem de boot: “Pipeline … ECDSA ES256”. |

---

## 4. Variáveis de ambiente relevantes

- `TITAN_JWT_ALGORITHM` — default `ES256`.
- `TITAN_UVCORN_WORKERS` — default `1`.
- `TITAN_THREADS_PER_WORKER` — default `32`.
- `TITAN_NUM_WORKERS` — espelha workers (default 1).

---

## 5. Produto / aplicação

- **Produto:** Microserviço de autenticação intra-serviços (Titan Intra Service Auth Engine).
- **Função:** Emissão de tokens JWT assinados com **ECDSA ES256** para autenticação service-to-service.
- **Performance alvo:** Pipeline enxuto para recuperar ~100 TPS, evitando gargalo por excesso de workers/threads.

---

## 6. Resumo

- **Pipeline:** 1 processo, 32 threads crypto (estilo V1), 64 slots; get_running_loop(); timeout mint 60s.
- **Crypto:** RSA substituído por **ECDSA ES256 (P-256)** como default.
- **Métricas:** `sec_signatures` (genérico); stats expõem `algorithm: "ECDSA-ES256"`.

Elias Andrade — Replika AI — Maringá Paraná
