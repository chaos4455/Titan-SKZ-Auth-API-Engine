# -*- coding: utf-8 -*-
"""
Titan Intra Service Auth Engine — Launcher.
Coloque este arquivo na mesma pasta do README.md; ao abrir/executar, sobe a API.

Uso:
  - Duplo clique no run.py (Windows)
  - Ou no terminal: python run.py

Criado por: Elias Andrade — Replika AI Solutions
"""

import os
import sys

# Garante que o pacote seja encontrado: adiciona ./src ao path (pasta onde está o run.py)
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_SRC_DIR = os.path.join(_THIS_DIR, "src")
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

# Sobe a API (composition root + uvicorn)
from titan_intra_service_auth.main import main

if __name__ == "__main__":
    main()
