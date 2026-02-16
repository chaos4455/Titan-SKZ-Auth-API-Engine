# -*- coding: utf-8 -*-
"""
🏛️ TITAN CA — Launcher do Servidor CA (Modo Standalone)
=======================================================
Opcional: rode o CA como processo separado na porta 8001.
Por padrão, o CA está embarcado na API (porta 8000).

Uso:
  python run_ca.py

Variáveis:
  TITAN_CA_PORT=8001  (porta do CA)

Criado por: Elias Andrade — Replika AI Solutions
"""

import os
import sys

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_SRC_DIR = os.path.join(_THIS_DIR, "src")
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

import uvicorn
from titan_intra_service_auth.infrastructure.ca.ca_server import ca_app

if __name__ == "__main__":
    port = int(os.environ.get("TITAN_CA_PORT", "8001"))
    print(f"[CA] Titan Certificate Authority — porta {port}")
    uvicorn.run(ca_app, host="0.0.0.0", port=port)
