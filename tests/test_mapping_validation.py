#!/usr/bin/env python3
"""
Teste para validar o mapeamento de campos
"""

import sys
import os
import json
from pathlib import Path

# Adicionar diretório src ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from src.utils.mapeador_campos_empresa import MapeadorCamposEmpresa
from banco_dados.gerenciador_banco_dados import GerenciadorBancoDados
from configuracao.configuracoes import Configuracoes


def test_mapeamento_campos():
    """Testa o mapeamento de campos com dados reais do banco"""
    
    print(" Testando mapeamento de campos...")
    
    # Configurar componentes
    config = Configuracoes()
    db_path = project_root / "data/db/esocial.db"
    gerenciador_bd = GerenciadorBancoDados(str(db_path))
    mapeador = MapeadorCamposEmpresa()
    
    # Buscar um registro de teste
    query = "SELECT * FROM esocial_s2200 LIMIT 1"
    resultado = gerenciador_bd.executar_query(query)
    
    if not resultado:
        print(" Nenhum registro encontrado no banco")
        return
    
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
    
    for campo in campos_teste:
        valor = mapeador.obter_valor_campo(template, campo, registro_dict)
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
                
    except Exception as e:
        print(f" Erro ao processar JSON: {e}")


def test_mapeamento_json_structure():
    """Testa especificamente a estrutura JSON e extração de dados"""
    
    print("\n Testando estrutura JSON...")
    
    # Mock data para teste
    mock_json = {
        "evtAdmissao": {
            "trabalhador": {
                "nmTrab": {"_text": "João da Silva"},
                "cpfTrab": {"_text": "12345678901"},
                "sexo": {"_text": "M"},
                "nascimento": {
                    "dtNascto": {"_text": "1980-01-01"}
                }
            }
        }
    }
    
    mapeador = MapeadorCamposEmpresa()
    mock_registro = {"json_data": json.dumps(mock_json)}
    
    # Testar extração
    nome = mapeador._extrair_do_json(json.dumps(mock_json), ["evtAdmissao", "trabalhador", "nmTrab", "_text"])
    cpf = mapeador._extrair_do_json(json.dumps(mock_json), ["evtAdmissao", "trabalhador", "cpfTrab", "_text"])
    data_nasc = mapeador._extrair_do_json(json.dumps(mock_json), ["evtAdmissao", "trabalhador", "nascimento", "dtNascto", "_text"])
    
    print(f"  Nome extraído: '{nome}'")
    print(f"  CPF extraído: '{cpf}'")
    print(f"  Data nascimento: '{data_nasc}'")
    
    assert nome == "João da Silva", f"Nome incorreto: {nome}"
    assert cpf == "12345678901", f"CPF incorreto: {cpf}"
    assert data_nasc == "1980-01-01", f"Data incorreta: {data_nasc}"
    
    print("   Estrutura JSON funcionando corretamente")


if __name__ == "__main__":
    # Detectar se está sendo executado como script ou teste
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_mapeamento_json_structure()
    else:
        test_mapeamento_campos()
        test_mapeamento_json_structure()
