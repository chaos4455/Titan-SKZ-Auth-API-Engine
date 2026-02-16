# -*- coding: utf-8 -*-
"""
Ponto de entrada para: python -m titan_intra_service_auth
(Execute na raiz do repo ou dentro de titan_intra_service_auth.)
Elias Andrade — Replika AI Solutions
"""

import os
import sys

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_SRC_DIR = os.path.join(_THIS_DIR, "src")
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from titan_intra_service_auth.main import main

if __name__ == "__main__":
    main()
