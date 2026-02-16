# -*- coding: utf-8 -*-
"""
🛡️ CA SERVICE — Lógica de Verificação de Assinaturas ZKP
========================================================
O CA verifica se um cliente possui a chave privada correspondente à identity_id,
sem a API precisar conhecer a identidade real. Prova de conhecimento zero:
cliente assina um nonce; CA verifica com a pubkey; API só recebe "autorizado" ou "não".

Autor: Elias Andrade — Arquiteto de Soluções — Replika AI — Maringá Paraná
Produto: Titan ZKP Auth — CA Service
Micro-revisão: 000000001
"""

import base64
from typing import Optional, Tuple

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from titan_intra_service_auth.infrastructure.ca.ca_repository import CARepository


class CAService:
    """
    Serviço do Certificate Authority.
    - register: adiciona nova identidade (pubkey)
    - verify_signature: verifica se a assinatura do nonce é válida para o identity_id
    """

    def __init__(self, repository: Optional[CARepository] = None) -> None:
        self._repo = repository or CARepository()

    def register_identity(self, pubkey_pem: str, scope: str = "access_root") -> Tuple[str, str]:
        """
        Registra identidade. Retorna (identity_id, fingerprint).
        Levanta ValueError se pubkey inválida ou duplicada.
        """
        # Valida que é PEM válido
        try:
            serialization.load_pem_public_key(pubkey_pem.encode())
        except Exception as e:
            raise ValueError(f"Pubkey inválida: {e}") from e
        return self._repo.register(pubkey_pem=pubkey_pem.strip(), scope=scope)

    def verify_signature(self, identity_id: str, nonce: str, signature_b64: str) -> bool:
        """
        Verifica se a assinatura do nonce foi feita pela chave privada correspondente
        ao identity_id. Retorna True se válida, False caso contrário.
        """
        pubkey_pem = self._repo.get_pubkey(identity_id)
        if not pubkey_pem:
            return False

        try:
            public_key = serialization.load_pem_public_key(pubkey_pem.encode())
        except Exception:
            return False

        try:
            signature_bytes = base64.urlsafe_b64decode(signature_b64 + "==")
        except Exception:
            return False

        # ECDSA P-256: assinatura em formato raw (r,s) ou DER
        # cryptography espera DER; vamos tentar ambos
        nonce_bytes = nonce.encode() if isinstance(nonce, str) else nonce

        try:
            public_key.verify(signature_bytes, nonce_bytes, ec.ECDSA(hashes.SHA256()))
            return True
        except InvalidSignature:
            return False
        except Exception:
            return False

    def is_authorized(self, identity_id: str) -> bool:
        """Delega ao repositório."""
        return self._repo.is_authorized(identity_id)
