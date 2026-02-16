# 🔐 NOTAS — ZKP e Certificate Authority (CA)

**Autor:** Elias Andrade — Arquiteto de Soluções — Replika AI — Maringá Paraná  
**Produto:** Titan Intra Service Auth — Edição ZKP  
**Micro-revisão:** 000000001

---

## 1. VISÃO GERAL

A API Titan agora opera em modo **ZKP (Zero Knowledge Proof)**: ela autentica e emite tokens **sem conhecer a identidade real** do usuário. O CA (Certificate Authority) determina quem está autorizado a consumir a API.

### Princípio ZKP
- A API **não armazena** identidades em claro
- O cliente prova posse da chave privada **assinando um nonce**
- O CA verifica a assinatura e autoriza o mint
- O `subject` do JWT é o `identity_id` (UUID) — não revela quem é a pessoa

---

## 2. FLUXO COMPLETO

```
┌─────────────┐     POST /v6/zkp/identity      ┌─────────────┐     register      ┌─────────┐
│   Cliente   │ ─────────────────────────────► │     API     │ ────────────────► │   CA    │
│ (gera keys) │     { pubkey_pem }             │             │                   │ SQLite  │
└─────────────┘◄─────────────────────────────  └─────────────┘                   └────┬────┘
       │                { identity_id }                │                               │
       │                                               │                               │
       │ Salva em u-data/{entity}/                     │                               │
       │ (identity_id, pubkey, private_key)            │                               │
       │                                               │                               │
       │     GET /v6/zkp/challenge?identity_id=...     │                               │
       │ ─────────────────────────────────────────►   │     is_authorized?             │
       │ ◄────────────────────────────────────────    │ ─────────────────────────►    │
       │                { nonce }                      │                               │
       │                                               │                               │
       │ Assina nonce com private_key                  │                               │
       │                                               │                               │
       │     POST /v6/zkp/mint                         │     verify_signature           │
       │ ─────────────────────────────────────────►   │ ─────────────────────────►    │
       │     { identity_id, nonce, signature }         │                               │
       │ ◄────────────────────────────────────────    │     authorized: true           │
       │                { access_token }               │ ◄────────────────────────     │
```

---

## 3. COMPONENTES

### 3.1 API Principal (porta 8000)
- **POST /v6/auth/mint** — Legado: mint com user/scope (mantido para compatibilidade)
- **POST /v6/zkp/identity** — Cria identidade; cliente envia pubkey
- **GET /v6/zkp/challenge** — Retorna nonce para assinatura
- **POST /v6/zkp/mint** — Mint ZKP: valida assinatura via CA, emite token

### 3.2 CA (Certificate Authority)
- **Modo embarcado:** CAService injetado na API (padrão)
- **Modo separado:** Servidor FastAPI em porta 8001 (`ca_server.py`)
- **Persistência:** SQLite em `data/ca_zkp.db`
- **Tabela:** `identities` — identity_id, pubkey_pem, pubkey_fingerprint, scope, created_at, revoked

### 3.3 Stress Tester (u-data)
- Pasta `u-data/` na raiz do projeto do stress tester
- Cada entidade: `u-data/entity_{i}/identity.json`
- Contém: identity_id, pubkey_pem, private_key_pem, scope
- Fluxo: cria identidades → salva em u-data → usa para mint em loop de stress

---

## 4. SEGURANÇA

- **Chaves:** ECDSA P-256 (SECP256R1), SHA-256
- **Nonce:** secrets.token_urlsafe(32)
- **TTL do challenge:** nonce consumido após uso (one-time)
- **CA:** Único componente que conhece a relação identity_id ↔ pubkey

---

## 5. VARIÁVEIS DE AMBIENTE

| Variável        | Descrição                    | Padrão                |
|-----------------|------------------------------|------------------------|
| TITAN_CA_DB_PATH| Caminho do SQLite do CA      | `{projeto}/data/ca_zkp.db` |

---

## 6. COMO RODAR

1. **Subir a API:**
   ```powershell
   cd titan_intra_service_auth
   python run.py
   ```

2. **Subir o Stress Tester (ZKP):**
   ```powershell
   python CONSOLE-APP-API-SERVER-FILA-QEUE-MANAGER-POOL-AUTH-V1-STRESS-TEST.PY
   ```
   - Cria identidades em u-data na primeira execução
   - Usa identidades existentes nas próximas

---

*Documentação ZKP — Titan Auth — Elias Andrade — Replika AI.*
