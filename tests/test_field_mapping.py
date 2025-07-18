#!/usr/bin/env python3
"""
Teste para validar o mapeamento de campos da Empresa
Migrado de test_mapping.py para a pasta tests
"""

import sys
import os
import json
from pathlib import Path

# Adicionar diretório raiz ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.mapeador_campos_empresa import MapeadorCamposEmpresa
from banco_dados.gerenciador_banco_dados import GerenciadorBancoDados
from configuracao.configuracoes import Configuracoes


def test_campo_mapeamento():
    """Testa o mapeamento de campos com dados reais do banco"""
    
    print(" Testando mapeamento de campos...")
    
    # Configurar componentes
    config = Configuracoes()
    db_path = project_root / "data" / "db" / "esocial.db"
    if not db_path.exists():
        print(f" Banco de dados não encontrado em {db_path}")
        # Procurar por outros arquivos de banco
        db_files = list((project_root / "data" / "db").glob("esocial*.db"))
        if db_files:
            db_path = db_files[-1]  # Usar o mais recente
            print(f" Usando banco alternativo: {db_path.name}")
        else:
            print(" Nenhum arquivo de banco encontrado")
            return False
    
    gerenciador_bd = GerenciadorBancoDados(str(db_path))
    mapeador = MapeadorCamposEmpresa()
    
    # Buscar um registro de teste
    query = "SELECT * FROM esocial_s2200 LIMIT 1"
    resultado = gerenciador_bd.executar_query(query)
    
    if not resultado:
        print(" Nenhum registro encontrado no banco")
        return False
    
    # Usar o primeiro registro
    registro_dict = resultado[0]
    
    print(f" Registro encontrado: ID {registro_dict.get('id')}")
    print(f" JSON data preview: {registro_dict.get('json_data', '')[:100]}...")
    
    # Testar campos específicos do template CONVTRABALHADOR
    template = "01_CONVTRABALHADOR"
    campos_teste = [
        "4 D-Nome trabalhador",
        "3 C-CPF trabalhador", 
        "5 E-Data nascimento trabalhador",
        "10 J-Sexo trabalhador"
    ]
    
    print(f"\n Testando campos do template {template}:")
    print("-" * 50)
    
    valores_encontrados = {}
    for campo in campos_teste:
        valor = mapeador.obter_valor_campo(template, campo, registro_dict)
        valores_encontrados[campo] = valor
        print(f"  {campo}: '{valor}'")
    
    # Testar extração JSON direta
    try:
        json_data = json.loads(registro_dict.get('json_data', '{}'))
        nome_direto = json_data.get("evtAdmissao", {}).get("trabalhador", {}).get("nmTrab", {}).get("_text")
        print(f"\n Extração JSON direta do nome: '{nome_direto}'")
        
        # Mostrar estrutura JSON
        print(f"\n Estrutura JSON do trabalhador:")
        trabalhador = json_data.get("evtAdmissao", {}).get("trabalhador", {})
        for key, value in trabalhador.items():
            if isinstance(value, dict) and "_text" in value:
                print(f"  {key}: '{value['_text']}'")
            else:
                print(f"  {key}: {value}")
        
        # Validar se pelo menos o nome foi extraído corretamente
        nome_mapeado = valores_encontrados.get("4 D-Nome trabalhador")
        if nome_mapeado and nome_mapeado == nome_direto:
            print(f"\n Mapeamento do nome validado: '{nome_mapeado}'")
            return True
        elif nome_mapeado:
            print(f"\n Divergência no mapeamento do nome: '{nome_mapeado}' vs '{nome_direto}'")
            return False
        else:
            print(f"\n Nome não foi mapeado corretamente")
            return False
                
    except Exception as e:
        print(f" Erro ao processar JSON: {e}")
        return False


def main():
    """Função principal para executar o teste"""
    print("=" * 60)
    print(" TESTE DE MAPEAMENTO DE CAMPOS")
    print("=" * 60)
    
    success = test_campo_mapeamento()
    
    if success:
        print("\n Teste de mapeamento concluído com SUCESSO!")
        return 0
    else:
        print("\n Teste de mapeamento FALHOU!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
