# -*- coding: utf-8 -*-
"""
📦 CA REPOSITORY — Persistência ZKP em SQLite
=============================================
Repositório que armazena apenas fingerprints e chaves públicas.
NUNCA armazena identidades em claro — Zero Knowledge para a API.

O CA é o único componente que conhece a relação identity_id <-> pubkey.
A API apenas pergunta "este identity_id está autorizado?" e "esta assinatura é válida?".

Autor: Elias Andrade — Arquiteto de Soluções — Replika AI — Maringá Paraná
Produto: Titan ZKP Auth — CA Repository
Micro-revisão: 000000001
"""

import hashlib
import os
import sqlite3
import uuid
from pathlib import Path
from typing import Optional, Tuple


class CARepository:
    """
    Persistência SQLite ZKP para o Certificate Authority.
    Tabela: identities — apenas identity_id, pubkey_pem, pubkey_fingerprint, created_at.
    Nenhum dado de identificação pessoal.
    """

    def __init__(self, db_path: Optional[str] = None) -> None:
        # data/ na raiz do pacote titan_intra_service_auth
        _base = Path(__file__).resolve().parent.parent.parent.parent.parent
        self._db_path = db_path or os.environ.get(
            "TITAN_CA_DB_PATH",
            str(_base / "data" / "ca_zkp.db"),
        )
        Path(self._db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        """Cria tabela identities se não existir."""
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS identities (
                    identity_id TEXT PRIMARY KEY,
                    pubkey_pem TEXT NOT NULL,
                    pubkey_fingerprint TEXT NOT NULL UNIQUE,
                    scope TEXT DEFAULT 'access_root',
                    created_at TEXT NOT NULL,
                    revoked INTEGER DEFAULT 0
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_identities_fingerprint 
                ON identities(pubkey_fingerprint)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_identities_revoked 
                ON identities(revoked)
            """)

    @staticmethod
    def _fingerprint(pubkey_pem: str) -> str:
        """Gera fingerprint SHA-256 da chave pública (identificador único sem revelar conteúdo)."""
        normalized = pubkey_pem.strip().replace("\r\n", "\n")
        return hashlib.sha256(normalized.encode()).hexdigest()

    def register(self, pubkey_pem: str, scope: str = "access_root") -> Tuple[str, str]:
        """
        Registra nova identidade. Retorna (identity_id, fingerprint).
        Levanta ValueError se pubkey já existir (fingerprint duplicado).
        """
        fingerprint = self._fingerprint(pubkey_pem)
        identity_id = str(uuid.uuid4())
        created_at = __import__("datetime").datetime.utcnow().isoformat() + "Z"

        with self._get_conn() as conn:
            try:
                conn.execute(
                    """
                    INSERT INTO identities (identity_id, pubkey_pem, pubkey_fingerprint, scope, created_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (identity_id, pubkey_pem, fingerprint, scope, created_at),
                )
                conn.commit()
            except sqlite3.IntegrityError as e:
                if "UNIQUE" in str(e):
                    raise ValueError(f"Pubkey já registrada (fingerprint: {fingerprint[:16]}...)") from e
                raise

        return identity_id, fingerprint

    def get_pubkey(self, identity_id: str) -> Optional[str]:
        """Retorna pubkey_pem se identity_id existir e não estiver revogado."""
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT pubkey_pem FROM identities WHERE identity_id = ? AND revoked = 0",
                (identity_id,),
            ).fetchone()
        return row["pubkey_pem"] if row else None

    def is_authorized(self, identity_id: str) -> bool:
        """Verifica se identity_id está autorizado (existe e não revogado)."""
        return self.get_pubkey(identity_id) is not None

    def revoke(self, identity_id: str) -> bool:
        """Revoga identidade. Retorna True se revogou, False se não encontrou."""
        with self._get_conn() as conn:
            cur = conn.execute(
                "UPDATE identities SET revoked = 1 WHERE identity_id = ? AND revoked = 0",
                (identity_id,),
            )
            conn.commit()
        return cur.rowcount > 0

    def count_identities(self, include_revoked: bool = False) -> int:
        """Retorna total de identidades registradas no CA."""
        with self._get_conn() as conn:
            if include_revoked:
                row = conn.execute("SELECT COUNT(*) as c FROM identities").fetchone()
            else:
                row = conn.execute("SELECT COUNT(*) as c FROM identities WHERE revoked = 0").fetchone()
        return row["c"] if row else 0

    def count_revoked(self) -> int:
        """Retorna total de identidades revogadas."""
        with self._get_conn() as conn:
            row = conn.execute("SELECT COUNT(*) as c FROM identities WHERE revoked = 1").fetchone()
        return row["c"] if row else 0
