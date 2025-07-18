#!/usr/bin/env python3
"""
Script de teste para verificar a estrutura de diretórios e importações
"""

import sys
import os
from pathlib import Path

# Adicionar src ao PYTHONPATH
pasta_raiz = Path(__file__).parent.parent
caminho_src = pasta_raiz / "src"
sys.path.insert(0, str(caminho_src))

# Verificar diretórios no PYTHONPATH
print("PYTHONPATH:")
for p in sys.path:
    print(f"  - {p}")

# Verificar diretórios em src
print("\nDiretórios em src:")
for d in Path(caminho_src).iterdir():
    if d.is_dir():
        print(f"  - {d}")

# Verificar importações
print("\nTestando importações:")
try:
    from configuracao.configuracoes import Configuracoes
    print("  - Importação de configuracoes.py: OK")
except ImportError as e:
    print(f"  - Importação de configuracoes.py: FALHA - {str(e)}")

try:
    from banco_dados.gerenciador_banco_dados import GerenciadorBancoDados
    print("  - Importação de gerenciador_banco_dados.py: OK")
except ImportError as e:
    print(f"  - Importação de gerenciador_banco_dados.py: FALHA - {str(e)}")

try:
    from processadores.processador_xml import ProcessadorXML
    print("  - Importação de processador_xml.py: OK")
except ImportError as e:
    print(f"  - Importação de processador_xml.py: FALHA - {str(e)}")

try:
    from exportadores.exportador_generico import ExportadorGenerico
    print("  - Importação de exportador_generico.py: OK")
except ImportError as e:
    print(f"  - Importação de exportador_generico.py: FALHA - {str(e)}")

try:
    from exportadores.exportador_templates_empresa import ExportadorTemplatesEmpresa
    print("  - Importação de exportador_templates_empresa.py: OK")
except ImportError as e:
    print(f"  - Importação de exportador_templates_empresa.py: FALHA - {str(e)}")

try:
    from src.utils.mapeador_campos_empresa import MapeadorCamposEmpresa
    print("  - Importação de mapeador_campos_empresa.py: OK")
except ImportError as e:
    print(f"  - Importação de mapeador_campos_empresa.py: FALHA - {str(e)}")

print("\n Teste de imports concluído!")

def test_imports():
    """Teste para verificar se as importações funcionam"""
    try:
        from configuracao.configuracoes import Configuracoes
        from banco_dados.gerenciador_banco_dados import GerenciadorBancoDados
        from processadores.processador_xml import ProcessadorXML
        from exportadores.exportador_generico import ExportadorGenerico
        from exportadores.exportador_templates_empresa import ExportadorTemplatesEmpresa
        from src.utils.mapeador_campos_empresa import MapeadorCamposEmpresa
        assert True
    except ImportError as e:
        assert False, f"Falha na importação: {e}"

if __name__ == "__main__":
    test_imports()
