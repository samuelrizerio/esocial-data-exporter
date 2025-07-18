#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Suite de testes para processamento de todos os layouts suportados do eSocial

Este script verifica se os arquivos XML de exemplo estão sendo processados corretamente 
e se os dados estão sendo inseridos nas tabelas correspondentes.

Para usar, certifique-se de que existem arquivos XML de teste para cada layout em data/input/,
nomeados conforme o padrão S-XXXX.xml (ex: S-1000.xml, S-1020.xml, etc.)
"""

import os
import sys
import sqlite3
import logging
import json
from pathlib import Path
import argparse

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("testes_layouts")

# Adicionar o diretório raiz ao path para importar módulos do projeto
projeto_dir = os.path.dirname(os.path.abspath(__file__))
if projeto_dir not in sys.path:
    sys.path.insert(0, projeto_dir)

from banco_dados.gerenciador_banco_dados import GerenciadorBancoDados
from processadores.processador_xml import ProcessadorXML
from configuracao.configuracoes import Configuracoes

def testar_layout(layout, caminho_xml=None):
    """
    Testa um layout específico do eSocial
    
    Args:
        layout: Código do layout (ex: S-1000, S-2206)
        caminho_xml: Caminho para o arquivo XML de teste (opcional)
        
    Returns:
        True se o teste passar, False caso contrário
    """
    logger.info(f"Iniciando teste para o layout {layout}")
    
    # Determinar caminhos importantes
    if not caminho_xml:
        caminho_xml = os.path.join(projeto_dir, "data", "input", f"{layout}.xml")
    
    caminho_bd = os.path.join(projeto_dir, "data", f"teste_{layout.lower().replace('-', '')}.db")
    
    # Verificar se o arquivo XML de teste existe
    if not os.path.exists(caminho_xml):
        logger.error(f"Arquivo de teste não encontrado: {caminho_xml}")
        return False
    
    # Remover banco de dados de teste se existir
    if os.path.exists(caminho_bd):
        try:
            os.remove(caminho_bd)
            logger.info(f"Banco de dados de teste removido: {caminho_bd}")
        except Exception as e:
            logger.error(f"Erro ao remover banco de dados de teste: {e}")
            return False
    
    try:
        # Inicializar configurações
        configuracoes = Configuracoes()
        
        # Inicializar gerenciador de banco de dados
        gerenciador_bd = GerenciadorBancoDados(caminho_bd)
        
        # Inicializar processador XML
        processador = ProcessadorXML(gerenciador_bd, configuracoes)
        
        # Processar arquivo XML de teste
        logger.info(f"Processando arquivo de teste: {caminho_xml}")
        resultado = processador.processar_arquivo(caminho_xml)
        
        if not resultado:
            logger.error(f"Falha ao processar o arquivo XML de teste para {layout}")
            return False
        
        # Processar o mesmo arquivo novamente para testar UPSERT
        logger.info(f"Processando o mesmo arquivo novamente para testar UPSERT: {caminho_xml}")
        resultado2 = processador.processar_arquivo(caminho_xml)
        
        if not resultado2:
            logger.error(f"Falha ao processar o arquivo XML pela segunda vez para {layout}")
            return False
        
        # Verificar se os dados foram inseridos na tabela correspondente
        conn = sqlite3.connect(caminho_bd)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Nome da tabela esperado
        nome_tabela = f"esocial_{layout.lower().replace('-', '')}"
        
        # Verificar se a tabela existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (nome_tabela,))
        tabela_existe = cursor.fetchone()
        
        if not tabela_existe:
            logger.error(f"A tabela {nome_tabela} não foi criada")
            return False
        
        # Contar registros na tabela
        cursor.execute(f"SELECT COUNT(*) as total FROM {nome_tabela}")
        total = cursor.fetchone()['total']
        
        if total == 0:
            logger.error(f"Nenhum registro foi inserido na tabela {nome_tabela}")
            
            # Buscar logs de erros
            cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (nome_tabela,))
            schema = cursor.fetchone()['sql']
            logger.info(f"Schema da tabela {nome_tabela}:\n{schema}")
            
            return False
        
        # Verificar se há UNIQUE constraint para checar se UPSERT funcionou corretamente
        cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (nome_tabela,))
        schema = cursor.fetchone()['sql']
        tem_unique = "UNIQUE(" in schema.upper()
        
        if tem_unique and total > 1:
            logger.warning(f"Foram inseridos {total} registros na tabela {nome_tabela}, mas era esperado apenas 1 devido ao UPSERT")
        elif not tem_unique:
            logger.info(f"A tabela {nome_tabela} não tem restrição UNIQUE, então pode ter múltiplos registros")
        else:
            logger.info(f"UPSERT funcionando corretamente: total de registros após duas inserções = {total}")
        
        # Buscar registros inseridos
        cursor.execute(f"SELECT * FROM {nome_tabela}")
        registros = [dict(row) for row in cursor.fetchall()]
        
        for i, reg in enumerate(registros):
            logger.info(f"Registro {i+1}:")
            for k, v in reg.items():
                if k != 'json_data':  # Não exibir o JSON completo
                    logger.info(f"  {k}: {v}")
        
        logger.info(f"Total de {total} registro(s) inserido(s) com sucesso na tabela {nome_tabela}")
        conn.close()
        
        return True
        
    except Exception as e:
        logger.exception(f"Erro durante o teste de {layout}: {e}")
        return False

def main():
    """Função principal que executa os testes para os layouts especificados"""
    parser = argparse.ArgumentParser(description='Testes de layouts eSocial')
    
    parser.add_argument(
        '--layouts',
        type=str,
        help='Lista de layouts a serem testados, separados por vírgula (ex: S-1000,S-2206)',
        default=None
    )
    
    args = parser.parse_args()
    
    # Determinar layouts a serem testados
    if args.layouts:
        layouts = args.layouts.split(',')
    else:
        # Layouts padrão do sistema - apenas os 7 layouts suportados
        layouts = [
            'S-1020', 'S-1030', 'S-1200', 'S-2200', 'S-2205', 'S-2206', 'S-2230'
        ]
    
    logger.info(f"Iniciando testes para os layouts: {', '.join(layouts)}")
    
    resultados = {}
    for layout in layouts:
        resultado = testar_layout(layout)
        resultados[layout] = resultado
        logger.info(f"Resultado do teste {layout}: {'SUCESSO' if resultado else 'FALHA'}")
    
    # Exibir resumo
    logger.info("\n=== RESUMO DOS TESTES ===")
    sucessos = 0
    falhas = []
    
    for layout, resultado in resultados.items():
        status = "SUCESSO" if resultado else "FALHA"
        logger.info(f"{layout}: {status}")
        
        if resultado:
            sucessos += 1
        else:
            falhas.append(layout)
    
    total = len(resultados)
    logger.info(f"\nTotal de {sucessos}/{total} testes bem-sucedidos")
    
    if falhas:
        logger.error(f"Layouts com falha: {', '.join(falhas)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
