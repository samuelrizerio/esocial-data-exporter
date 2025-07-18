#!/usr/bin/env python3
"""
Teste para validar a exportação completa de dados
"""

import sys
import os
from pathlib import Path

# Adicionar diretório src ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from configuracao.configuracoes import Configuracoes
from banco_dados.gerenciador_banco_dados import GerenciadorBancoDados
from exportadores.exportador_templates_empresa import ExportadorTemplatesEmpresa
from exportadores.exportador_generico import ExportadorGenerico


def test_exportacao_templates():
    """Testa a exportação completa dos templates"""
    
    print(" Testando exportação de templates...")
    
    # Configurar componentes
    config = Configuracoes()
    db_path = project_root / "data/db/esocial.db"
    gerenciador_bd = GerenciadorBancoDados(str(db_path))
    
    # Configurar pasta de saída
    output_dir = project_root / "data/output/test_export"
    output_dir.mkdir(parents=True, exist_ok=True)
    
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
        _verificar_arquivos_gerados(output_dir)
        
        print(f"\n Teste de exportação concluído com sucesso!")
        return True
        
    except Exception as e:
        print(f" Erro durante a exportação: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_exportacao_individual():
    """Testa exportação de templates individuais"""
    
    print("\n Testando exportação individual...")
    
    config = Configuracoes()
    db_path = project_root / "data/db/esocial.db"
    gerenciador_bd = GerenciadorBancoDados(str(db_path))
    
    output_dir = project_root / "data/output/test_individual"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        exportador = ExportadorTemplatesEmpresa(gerenciador_bd, config)
        exportador.caminho_saida = str(output_dir)
        
        # Testar templates específicos
        templates_teste = [
            "01_CONVTRABALHADOR",
            "02_CONVDEPENDENTE", 
            "04_CONVCONTRATO"
        ]
        
        resultados = {}
        for template in templates_teste:
            print(f"   Testando template {template}...")
            try:
                resultado = exportador.exportar_template(template)
                resultados[template] = resultado
                print(f"     {template}: {resultado} registros")
            except Exception as e:
                print(f"     {template}: {e}")
                resultados[template] = 0
        
        print(f"\n Resumo da exportação individual:")
        for template, resultado in resultados.items():
            status = "" if resultado > 0 else ""
            print(f"  {status} {template}: {resultado} registros")
        
        return len([r for r in resultados.values() if r > 0]) > 0
        
    except Exception as e:
        print(f" Erro na exportação individual: {e}")
        return False


def _verificar_arquivos_gerados(output_dir: Path):
    """Verifica e lista arquivos gerados"""
    
    print(f"\n Arquivos gerados em {output_dir}:")
    
    if not output_dir.exists():
        print("   Diretório de saída não existe")
        return
    
    arquivos = list(output_dir.glob("*.csv"))
    
    if not arquivos:
        print("   Nenhum arquivo CSV encontrado")
        return
    
    for arquivo in sorted(arquivos):
        if arquivo.is_file():
            tamanho = arquivo.stat().st_size
            print(f"   {arquivo.name} ({tamanho} bytes)")
            
            # Mostrar amostra do conteúdo do primeiro template
            if arquivo.name == "01_CONVTRABALHADOR.csv":
                _mostrar_amostra_arquivo(arquivo)


def _mostrar_amostra_arquivo(arquivo: Path):
    """Mostra amostra do conteúdo de um arquivo"""
    
    try:
        print(f"       Amostra do conteúdo:")
        with open(arquivo, 'r', encoding='utf-8') as f:
            for i, linha in enumerate(f):
                if i < 3:  # Mostrar primeiras 3 linhas
                    linha_limitada = linha.strip()[:100]
                    if len(linha.strip()) > 100:
                        linha_limitada += "..."
                    print(f"      {i+1}: {linha_limitada}")
                else:
                    break
    except Exception as e:
        print(f"       Erro ao ler arquivo: {e}")


def test_verificacao_dados():
    """Verifica se há dados no banco para exportar"""
    
    print("\n Verificando dados no banco...")
    
    config = Configuracoes()
    db_path = project_root / "data/db/esocial.db"
    
    if not db_path.exists():
        print("   Banco de dados não encontrado")
        return False
    
    gerenciador_bd = GerenciadorBancoDados(str(db_path))
    
    # Verificar tabelas principais
    tabelas = [
        "esocial_s1020",
        "esocial_s1030", 
        "esocial_s1200",
        "esocial_s2200",
        "esocial_s2205",
        "esocial_s2206",
        "esocial_s2230"
    ]
    
    dados_encontrados = False
    
    for tabela in tabelas:
        try:
            query = f"SELECT COUNT(*) as total FROM {tabela}"
            resultado = gerenciador_bd.executar_query(query)
            
            if resultado and resultado[0]['total'] > 0:
                print(f"   {tabela}: {resultado[0]['total']} registros")
                dados_encontrados = True
            else:
                print(f"   {tabela}: 0 registros")
                
        except Exception as e:
            print(f"   {tabela}: Erro - {e}")
    
    if not dados_encontrados:
        print("\n Nenhum dado encontrado para exportação")
        print("   Execute primeiro o processamento de XMLs")
    
    return dados_encontrados


if __name__ == "__main__":
    print(" EXECUTANDO TESTES DE EXPORTAÇÃO")
    print("=" * 50)
    
    # Verificar se há dados para exportar
    tem_dados = test_verificacao_dados()
    
    if tem_dados:
        # Executar testes de exportação
        sucesso_templates = test_exportacao_templates()
        sucesso_individual = test_exportacao_individual()
        
        if sucesso_templates and sucesso_individual:
            print("\n Todos os testes de exportação passaram!")
        else:
            print("\n Alguns testes falharam")
    else:
        print("\n Testes de exportação pulados - sem dados no banco")
