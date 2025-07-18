#!/usr/bin/env python3
"""
Teste para validar a exportação completa dos templates
Migrado de test_export.py para a pasta tests
"""

import sys
import os
import traceback
from pathlib import Path

# Adicionar diretório raiz ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from configuracao.configuracoes import Configuracoes
from banco_dados.gerenciador_banco_dados import GerenciadorBancoDados
from exportadores.exportador_templates_empresa import ExportadorTemplatesEmpresa
from exportadores.exportador_generico import ExportadorGenerico


def test_template_export():
    """Testa a exportação completa dos templates"""
    
    print(" Testando exportação de templates...")
    
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
    
    # Configurar pasta de saída
    output_dir = project_root / "data" / "output" / "test_export"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    arquivos_gerados = []
    
    try:
        # Teste 1: Exportador Empresa
        print("\n Testando ExportadorTemplatesEmpresa...")
        exportador_empresa = ExportadorTemplatesEmpresa(gerenciador_bd, config)
        exportador_empresa.caminho_saida = str(output_dir)
        
        templates_processados = exportador_empresa.exportar_todos_templates()
        print(f" Templates Empresa processados: {templates_processados}")
        
        # Teste 2: Exportador Genérico  
        print("\n Testando ExportadorGenerico...")
        exportador_csv = ExportadorGenerico(gerenciador_bd, config)
        exportador_csv.caminho_saida = str(output_dir)
        
        dados_exportados = exportador_csv.exportar_todos()
        print(f" Dados genéricos exportados: {dados_exportados}")
        
        # Verificar arquivos gerados
        print(f"\n Arquivos gerados em {output_dir}:")
        if output_dir.exists():
            for arquivo_path in output_dir.iterdir():
                if arquivo_path.is_file():
                    tamanho = arquivo_path.stat().st_size
                    arquivos_gerados.append(arquivo_path.name)
                    print(f"   {arquivo_path.name} ({tamanho} bytes)")
                    
                    # Mostrar amostra do conteúdo do primeiro template
                    if arquivo_path.name == "01_CONVTRABALHADOR.csv":
                        print(f"       Amostra do conteúdo:")
                        with open(arquivo_path, 'r', encoding='utf-8') as f:
                            for i, linha in enumerate(f):
                                if i < 3:  # Mostrar primeiras 3 linhas
                                    print(f"      {i+1}: {linha.strip()[:100]}...")
                                else:
                                    break
        
        # Validar se pelo menos alguns arquivos foram gerados
        if len(arquivos_gerados) >= 2:
            print(f"\n Exportação validada: {len(arquivos_gerados)} arquivos gerados")
            return True
        else:
            print(f"\n Poucos arquivos gerados: {len(arquivos_gerados)}")
            return False
        
    except Exception as e:
        print(f" Erro durante a exportação: {e}")
        traceback.print_exc()
        return False


def test_file_content_validation():
    """Valida o conteúdo dos arquivos exportados"""
    
    print("\n Validando conteúdo dos arquivos exportados...")
    
    output_dir = project_root / "data" / "output" / "test_export"
    
    # Procurar pelo arquivo principal
    funcionarios_file = output_dir / "funcionarios.csv"
    if funcionarios_file.exists():
        with open(funcionarios_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if "João da Silva" in content:
                print(" Dados de 'João da Silva' encontrados no arquivo funcionarios.csv")
                return True
            else:
                print(" Dados de 'João da Silva' NÃO encontrados no arquivo funcionarios.csv")
                print(f"   Primeiros 200 caracteres: {content[:200]}...")
                return False
    
    # Procurar em outros arquivos CSV
    for csv_file in output_dir.glob("*.csv"):
        with open(csv_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if "João da Silva" in content:
                print(f" Dados de 'João da Silva' encontrados em {csv_file.name}")
                return True
    
    print(" Dados de 'João da Silva' não encontrados em nenhum arquivo")
    return False


def main():
    """Função principal para executar os testes"""
    print("=" * 60)
    print(" TESTE DE EXPORTAÇÃO COMPLETA")
    print("=" * 60)
    
    # Teste 1: Exportação de templates
    export_success = test_template_export()
    
    # Teste 2: Validação de conteúdo
    content_success = test_file_content_validation()
    
    overall_success = export_success and content_success
    
    if overall_success:
        print("\n Todos os testes de exportação foram CONCLUÍDOS COM SUCESSO!")
        return 0
    else:
        print("\n Alguns testes de exportação FALHARAM!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
