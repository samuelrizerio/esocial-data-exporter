#!/usr/bin/env python3
"""
Script principal de execução do projeto de migração do eSocial

Este script foi modernizado para usar apenas o pipeline principal.
"""

import sys
from pathlib import Path

# Configuração mínima inicial - apenas src
pasta_raiz = Path(__file__).parent
sys.path.insert(0, str(pasta_raiz / "src"))

# Importar função principal
from src.main import main

if __name__ == "__main__":
    sys.exit(main())
