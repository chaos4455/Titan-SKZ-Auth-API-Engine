# -*- coding: utf-8 -*-
"""
🔑 ZKP CLIENT — Utilitários para clientes ZKP
============================================
Geração de chaves, assinatura de nonces. Para uso em stress testers,
microserviços e clientes que consomem a API ZKP.

Autor: Elias Andrade — Arquiteto de Soluções — Replika AI — Maringá Paraná
Micro-revisão: 000000001
"""

from titan_intra_service_auth.infrastructure.zkp_client.keygen import generate_identity_keys, sign_nonce

__all__ = ["generate_identity_keys", "sign_nonce"]
