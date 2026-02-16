# -*- coding: utf-8 -*-
"""
🔐 INFRAESTRUTURA CA — CERTIFICATE AUTHORITY (ZKP)
==================================================
Componente isolado que determina quem pode consumir a API e obter tokens.
Armazena apenas dados criptográficos (pubkeys) — ZKP: nunca identidades em claro.

Autor: Elias Andrade — Arquiteto de Soluções — Replika AI — Maringá Paraná
Produto: Titan ZKP Auth — CA Module
Micro-revisão: 000000001
"""

from titan_intra_service_auth.infrastructure.ca.ca_repository import CARepository
from titan_intra_service_auth.infrastructure.ca.ca_service import CAService

__all__ = ["CARepository", "CAService"]
