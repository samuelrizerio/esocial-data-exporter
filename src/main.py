#!/usr/bin/env python3
"""
Módulo principal da aplicação de migração do eSocial
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Ensure src/ is in sys.path for local imports
sys.path.insert(0, str(Path(__file__).parent))

# Add project root to sys.path for package imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Importar módulos
from configuracao.configuracoes import Configuracoes
from banco_dados.gerenciador_banco_dados import GerenciadorBancoDados
from processadores.processador_xml import ProcessadorXML
from exportadores.exportador_templates_empresa import ExportadorTemplatesEmpresa

def configurar_logging(nivel_log: str = "INFO"):
    """Configura o sistema de logging da aplicação e retorna o logger principal"""
    nivel_numerico = getattr(logging, nivel_log.upper(), logging.INFO)
    diretorio_logs = Path("logs")
    diretorio_logs.mkdir(exist_ok=True)
    logging.basicConfig(
        level=nivel_numerico,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(diretorio_logs / 'application.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger("src.main")


def analisar_argumentos() -> Dict[str, Any]:
    """Analisa argumentos da linha de comando"""
    parser = argparse.ArgumentParser(description='Migração de dados do eSocial')
    
    parser.add_argument(
        '--input', '-i',
        type=str,
        help='Caminho do diretório de entrada com arquivos XML (padrão: data/input)'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Caminho do diretório de saída para arquivos CSV (padrão: data/output)'
    )
    
    parser.add_argument(
        '--templates', '-t',
        type=str,
        help='Caminho do diretório com templates CSV (padrão: data/templates)'
    )
    
    parser.add_argument(
        '--database', '-d',
        type=str,
        help='Caminho do banco de dados SQLite (padrão: data/db/esocial.db)'
    )
    
    parser.add_argument(
        '--log-level', '-l',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='ERROR',
        help='Nível de log (padrão: INFO)'
    )
    
    return vars(parser.parse_args())


def main() -> int:
    """Função principal da aplicação"""
    # Analisar argumentos e configurar logging
    args = analisar_argumentos()
    logger = configurar_logging(args.get('log_level', 'INFO'))
    
    try:
        logger.info("Iniciando migração de dados do eSocial")
        
        # Inicializar configurações
        configuracoes = Configuracoes()
        configuracoes.atualizar_de_args(args)
        
        # Always delete the database file before starting
        db_path = args.get('database') or 'data/db/esocial.db'
        if os.path.exists(db_path):
            os.remove(db_path)
        
        # Criar gerenciador de banco de dados
        gerenciador_bd = GerenciadorBancoDados(configuracoes.CAMINHO_BANCO_DADOS)
        
        # Processar arquivos XML
        processador_xml = ProcessadorXML(gerenciador_bd, configuracoes)
        total_processado = processador_xml.processar_diretorio(configuracoes.CAMINHO_ENTRADA)
        logger.info(f"Total de arquivos processados: {total_processado}")
        
        # Exportar para CSV usando templates Empresa
        exportador_templates = ExportadorTemplatesEmpresa(gerenciador_bd, configuracoes)
        templates_processados = exportador_templates.exportar_todos_templates()
        logger.info(f"Total de templates Empresa exportados: {templates_processados}")
        
        logger.info("Migração concluída com sucesso")
        return 0
    
    except Exception as e:
        logger.error(f"Erro durante a execução: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
