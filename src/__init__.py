"""
Módulo inicial do pacote src
"""
__version__ = '0.1.0'

# Adicionar diretórios ao PYTHONPATH
import sys
import os
from pathlib import Path

# Obter diretório atual
diretorio_atual = Path(__file__).parent

# Adicionar apenas pastas ao PYTHONPATH
diretorios = [
    'configuracao',
    'banco_dados',
    'processadores',
    'exportadores',
    'utilitarios',
    'esquemas',
    'layouts'
]

for diretorio in diretorios:
    caminho = diretorio_atual / diretorio
    if caminho.exists() and caminho.is_dir() and str(caminho) not in sys.path:
        sys.path.insert(0, str(caminho))
