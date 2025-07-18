"""
Gerenciador de banco de dados para migracao eSocial
"""

import sqlite3
import logging
import json
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime

from src.esquemas.esquemas_tabelas import TABLE_SCHEMAS, INDEXES, EXPORT_QUERIES


class GerenciadorBancoDados:
    """Gerenciador de banco de dados SQLite para migração eSocial"""
    
    def __init__(self, caminho_bd: Union[str, Path]):
        """
        Inicializa o gerenciador de banco de dados
        
        Args:
            caminho_bd: Caminho para o arquivo de banco de dados SQLite
        """
        self.caminho_bd = Path(caminho_bd)
        self.logger = logging.getLogger(__name__)
        self._connection = None  # Conexao persistente para bancos em memoria
        
        # Garantir que o diretorio do banco de dados existe
        if str(self.caminho_bd) != ":memory:":
            self.caminho_bd.parent.mkdir(parents=True, exist_ok=True)
        
        # Verificar existencia do banco de dados (nao cria mais backup)
        if self.caminho_bd.exists() and str(self.caminho_bd) != ":memory:":
            self._criar_backup_bd()
        
        # Inicializar o banco de dados
        self._inicializar_banco_dados()
    
    def _criar_backup_bd(self) -> None:
        """Funcao mantida para compatibilidade, mas nao cria mais backups do banco de dados"""
        try:
            # Gera timestamp (mantido para possivel uso em outros lugares)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Log informativo de que backups estao desativados
            self.logger.info("Funcionalidade de backup de banco de dados desativada")
        except Exception as e:
            self.logger.error(f"Erro no processamento: {e}", exc_info=True)
    
    def _inicializar_banco_dados(self) -> None:
        """Inicializa o banco de dados criando as tabelas necessarias"""
        self.logger.debug(f"Inicializando banco de dados: {self.caminho_bd}")
        
        conn = self._obter_conexao()
        cursor = conn.cursor()
        
        try:
            # Criar tabelas
            for nome_tabela, schema in TABLE_SCHEMAS.items():
                self.logger.debug(f"Criando tabela: {nome_tabela}")
                cursor.execute(schema)
            
            # Criar indices
            for nome_indice, indice_sql in INDEXES.items():
                self.logger.debug(f"Criando indice: {nome_indice}")
                cursor.execute(indice_sql)
            
            conn.commit()
            
            self.logger.debug("Banco de dados inicializado com sucesso")
            
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Erro ao inicializar banco de dados: {e}", exc_info=True)
            raise
        finally:
            # So fechar se nao for banco em memoria
            if str(self.caminho_bd) != ":memory:":
                conn.close()
    
    def _obter_conexao(self) -> sqlite3.Connection:
        """Obtem uma conexao com o banco de dados"""
        # Para bancos em memoria, usar conexao persistente
        if str(self.caminho_bd) == ":memory:":
            if self._connection is None:
                self._connection = sqlite3.connect(self.caminho_bd, detect_types=sqlite3.PARSE_DECLTYPES)
                self._connection.row_factory = sqlite3.Row  # Retornar linhas como dicionarios
            return self._connection
        else:
            # Para bancos em arquivo, criar nova conexao sempre
            conn = sqlite3.connect(self.caminho_bd, detect_types=sqlite3.PARSE_DECLTYPES)
            conn.row_factory = sqlite3.Row  # Retornar linhas como dicionarios
            return conn
    
    def limpar_dados_para_processamento(self) -> bool:
        """
        Limpa os dados das tabelas eSocial antes de um novo processamento
        para evitar acúmulo de registros duplicados
        
        Returns:
            bool: True se a operacao foi bem-sucedida, False caso contrario
        """
        self.logger.info("Iniciando limpeza de dados para novo processamento...")
        
        # Lista de tabelas a serem limpas (todas as tabelas eSocial)
        tabelas_esocial = [
            "esocial_s1020", "esocial_s1030", "esocial_s1200",
            "esocial_s2200", "esocial_s2205", "esocial_s2206",
            "esocial_s2230"
        ]
        
        conn = self._obter_conexao()
        cursor = conn.cursor()
        
        try:
            # Comecar uma transacao para garantir atomicidade
            conn.execute("BEGIN TRANSACTION")
            
            # Verificar quais tabelas existem no banco de dados
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tabelas_existentes = [row[0] for row in cursor.fetchall()]
            
            # Para cada tabela eSocial que existe, limpar os dados
            tabelas_limpas = 0
            for tabela in tabelas_esocial:
                if tabela in tabelas_existentes:
                    # Obter contagem de registros antes da limpeza para log
                    cursor.execute(f"SELECT COUNT(*) as total FROM {tabela}")
                    registros_antes = cursor.fetchone()['total']
                    
                    # Limpar a tabela
                    cursor.execute(f"DELETE FROM {tabela}")
                    
                    self.logger.info(f"Tabela {tabela}: {registros_antes} registros removidos")
                    tabelas_limpas += 1
            
            conn.commit()
            self.logger.info(f"Limpeza concluida com sucesso: {tabelas_limpas} tabelas limpas")
            return True
            
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Erro ao limpar dados para novo processamento: {e}", exc_info=True)
            return False
        finally:
            # So fechar se nao for banco em memoria
            if str(self.caminho_bd) != ":memory:":
                conn.close()
    
    def inserir_dados(self, nome_tabela: str, dados: Union[Dict[str, Any], List[Dict[str, Any]]]) -> int:
        """
        Insere dados em uma tabela
        
        Args:
            nome_tabela: Nome da tabela a ser inserida
            dados: Dicionário ou lista de dicionários com os dados a serem inseridos
            
        Returns:
            Número de registros inseridos
        """
        if not dados:
            self.logger.debug(f"Nenhum dado fornecido para inserção na tabela {nome_tabela}")
            return 0
        
        # Validar se a tabela existe
        tabelas_existentes = self.obter_tabelas()
        if nome_tabela not in tabelas_existentes:
            self.logger.error(f"Erro ao inserir dados: Tabela '{nome_tabela}' não existe")
            return 0
        
        # Converter dados para lista se for um único dicionário
        if isinstance(dados, dict):
            dados = [dados]
        
        conn = self._obter_conexao()
        cursor = conn.cursor()
        registros_inseridos = 0
        
        try:
            # Comecar uma transacao explicita para melhor performance com muitos registros
            conn.execute("BEGIN TRANSACTION")
            
            # Verificar se todos os dados tem as mesmas colunas
            colunas = list(dados[0].keys())
            marcadores = ["?" for _ in colunas]
            
            # Obter informacoes sobre as colunas da tabela para validacao
            cursor.execute(f"PRAGMA table_info({nome_tabela})")
            colunas_tabela = {row['name']: row for row in cursor.fetchall()}
            
            # Validar colunas
            for coluna in colunas:
                if coluna not in colunas_tabela:
                    conn.rollback()
                    self.logger.error(f"Erro ao inserir dados: Coluna '{coluna}' nao existe na tabela '{nome_tabela}'")
                    return 0
            
            # Construir query SQL - verificar se a tabela tem UNIQUE constraint para usar UPSERT
            cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{nome_tabela}'")
            table_sql = cursor.fetchone()['sql']
            
            # Verificar se a tabela tem UNIQUE constraint para determinar se podemos usar UPSERT
            if table_sql and "UNIQUE(" in table_sql.upper():
                # Usar UPSERT se houver UNIQUE constraint
                sql = f"INSERT INTO {nome_tabela} ({', '.join(colunas)}) VALUES ({', '.join(marcadores)}) " + \
                      "ON CONFLICT DO UPDATE SET " + \
                      ", ".join([f"{col} = excluded.{col}" for col in colunas if col != 'id'])
                self.logger.debug(f"Usando UPSERT para tabela {nome_tabela} com UNIQUE constraint")
            else:
                # Caso contrario, usar INSERT simples
                sql = f"INSERT INTO {nome_tabela} ({', '.join(colunas)}) VALUES ({', '.join(marcadores)})"
                self.logger.debug(f"Usando INSERT simples para tabela {nome_tabela} sem UNIQUE constraint")
            
            # Construir lista de valores para inserção - com lote de 1000 para melhor performance
            lote_size = 1000
            valores = []
            erros = 0
            
            for idx, registro in enumerate(dados):
                valores_linha = []
                for coluna in colunas:
                    valor = registro.get(coluna)
                    
                    # Converter valores complexos para JSON
                    if isinstance(valor, (dict, list)):
                        valor = json.dumps(valor)
                    
                    # Validar formato de dados
                    if coluna in colunas_tabela:
                        coluna_info = colunas_tabela[coluna]
                        # Validar tipos numéricos
                        if 'INTEGER' in coluna_info['type'] and valor and not isinstance(valor, (int, type(None))):
                            try:
                                valor = int(valor)
                            except (ValueError, TypeError):
                                self.logger.warning(f"Conversao automática para inteiro: '{valor}' para coluna '{coluna}'")
                                valor = 0
                        
                        # Validar tipos reais
                        if 'REAL' in coluna_info['type'] and valor and not isinstance(valor, (float, type(None))):
                            try:
                                valor = float(valor)
                            except (ValueError, TypeError):
                                self.logger.warning(f"Conversao automática para float: '{valor}' para coluna '{coluna}'")
                                valor = 0.0
                    
                    valores_linha.append(valor)
                
                valores.append(tuple(valores_linha))
                
                # Processar em lotes para evitar problemas de memória com grandes volumes de dados
                if len(valores) >= lote_size or idx == len(dados) - 1:
                    try:
                        cursor.executemany(sql, valores)
                        registros_inseridos += len(valores)
                        valores = []
                    except Exception as e:
                        erros += 1
                        self.logger.error(f"Erro ao inserir lote de dados na tabela {nome_tabela}: {e}", exc_info=True)
            
            # Commit das alterações
            conn.commit()
            
            if registros_inseridos > 0:
                self.logger.debug(f"Inseridos {registros_inseridos} registros na tabela {nome_tabela}")
            
            return registros_inseridos
            
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Erro ao inserir dados na tabela {nome_tabela}: {e}", exc_info=True)
            return 0
        finally:
            # So fechar se nao for banco em memoria
            if str(self.caminho_bd) != ":memory:":
                conn.close()
    
    def executar_query(self, sql: str, parametros: tuple = ()) -> List[Dict[str, Any]]:
        """
        Executa uma consulta SQL e retorna o resultado
        
        Args:
            sql: Query SQL a ser executada
            parametros: Parâmetros para a query (opcional)
            
        Returns:
            Lista de dicionários com os resultados
        """
        import time
        start_time = time.time()
        
        # Validar SQL antes da execução
        sql_lower = sql.lower().strip()
        if not sql_lower.startswith(("select", "pragma", "explain")):
            self.logger.error(f"Tentativa de executar uma query não-SELECT: {sql[:100]}...")
            return []
        
        conn = self._obter_conexao()
        cursor = conn.cursor()
        
        try:
            # Adicionando explicacao da query para diagnostico de performance
            if not sql_lower.startswith("explain"):
                explain_sql = f"EXPLAIN QUERY PLAN {sql}"
                cursor.execute(explain_sql, parametros)
                explain_result = cursor.fetchall()
                
                # Log do plano de execucao se a query for complexa ou contiver juncoes
                if any("SCAN" in str(row) for row in explain_result) or "JOIN" in sql_lower:
                    self.logger.debug(f"Plano de execucao para query: {sql[:100]}...")
                    for row in explain_result:
                        self.logger.debug(f"    {dict(row)}")
            
            # Executar a query real
            cursor.execute(sql, parametros)
            
            # Para testes, limitar o número de registros retornados
            if "count" in sql_lower and "group by" not in sql_lower:
                # Para consultas de contagem simples
                result = [dict(row) for row in cursor.fetchall()]
            else:
                # Limitar a 1000 registros para testes
                result = []
                max_rows = 1000
                rows_fetched = 0
                
                while True:
                    batch = cursor.fetchmany(100)
                    if not batch:
                        break
                    
                    result.extend([dict(row) for row in batch])
                    rows_fetched += len(batch)
                    
                    if rows_fetched >= max_rows:
                        break
            
            # Registrar performance apenas para queries lentas
            execution_time = time.time() - start_time
            if execution_time > 5.0:  # Log apenas queries muito lentas
                self.logger.warning(f"Query muito lenta ({execution_time:.2f}s): {sql[:100]}...")
            
            return result
        except Exception as e:
            self.logger.error(f"Erro ao executar query SQL: {e}", exc_info=True)
            self.logger.error(f"Query com erro: {sql[:200]}...")
            if parametros:
                self.logger.error(f"Parâmetros: {parametros}")
            return []
        finally:
            # So fechar se nao for banco em memoria
            if str(self.caminho_bd) != ":memory:":
                conn.close()
    
    def exportar_dados(self, nome_exportacao: str, parametros: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Exporta dados usando uma query pré-definida
        
        Args:
            nome_exportacao: Nome da exportação definida em EXPORT_QUERIES
            parametros: Parâmetros para a query (opcional)
            
        Returns:
            Lista de dicionários com os resultados
        """
        if nome_exportacao not in EXPORT_QUERIES:
            self.logger.error(f"Query de exportação não encontrada: {nome_exportacao}")
            return []
            
        sql = EXPORT_QUERIES[nome_exportacao]
        parametros_tuple = ()
        
        # Preparar parametros se fornecidos
        if parametros:
            # Extrair parametros nomeados da SQL
            param_names = []
            for param in parametros.keys():
                if f":{param}" in sql:
                    sql = sql.replace(f":{param}", "?")
                    param_names.append(param)
                    
                # Criar tupla de parametros na ordem correta
                parametros_tuple = tuple(parametros.get(p) for p in param_names)
            
        return self.executar_query(sql, parametros_tuple)
    
    def obter_tabelas(self) -> List[str]:
        """
        Retorna a lista de tabelas existentes no banco
        
        Returns:
            Lista com nomes das tabelas
        """
        sql = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        result = self.executar_query(sql)
        return [row['name'] for row in result]
    
    def otimizar_banco(self) -> bool:
        """
        Otimiza o banco de dados SQLite para melhor performance
        
        Returns:
            True se a otimização foi bem-sucedida, False caso contrário
        """
        if str(self.caminho_bd) == ":memory:":
            self.logger.info("Otimizacao ignorada para banco em memoria")
            return True
            
        conn = self._obter_conexao()
        
        try:
            self.logger.info("Iniciando otimizacao do banco de dados...")
            
            # Analise de estatisticas
            conn.execute("ANALYZE")
            
            # Vacuum para remover espaco nao utilizado
            conn.execute("VACUUM")
            
            # Limpar cache de preparacao de statements
            conn.execute("PRAGMA optimize")
            
            # Reindexar para otimizar indices
            conn.execute("REINDEX")
            
            # Verificar integridade do banco
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check")
            integrity_result = cursor.fetchone()
            
            if integrity_result and integrity_result[0] == 'ok':
                self.logger.info("Verificacao de integridade do banco concluida: OK")
            else:
                self.logger.warning(f"Verificacao de integridade do banco: {integrity_result}")
            
            self.logger.info("Otimizacao do banco de dados concluida com sucesso")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao otimizar banco de dados: {e}", exc_info=True)
            return False
        finally:
            if str(self.caminho_bd) != ":memory:":
                conn.close()
    
    def verificar_estatisticas_banco(self) -> Dict[str, Any]:
        """
        Coleta estatísticas sobre o banco de dados
        
        Returns:
            Dicionário com estatísticas do banco
        """
        estatisticas = {
            'total_tabelas': 0,
            'tabelas': {},
            'tamanho_banco': 0,
            'indices': 0
        }
        
        conn = self._obter_conexao()
        
        try:
            # Obter lista de tabelas
            tabelas = self.obter_tabelas()
            estatisticas['total_tabelas'] = len(tabelas)
            
            # Obter estatísticas por tabela
            for tabela in tabelas:
                # Contar registros
                cursor = conn.cursor()
                cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
                count = cursor.fetchone()[0]
                
                # Obter informações de índices
                cursor.execute(f"PRAGMA index_list({tabela})")
                indices = cursor.fetchall()
                
                estatisticas['tabelas'][tabela] = {
                    'registros': count,
                    'indices': len(indices),
                    'nome_indices': [idx['name'] for idx in indices]
                }
                
                estatisticas['indices'] += len(indices)
            
            # Obter tamanho do banco se não for em memória
            if str(self.caminho_bd) != ":memory:" and self.caminho_bd.exists():
                estatisticas['tamanho_banco'] = self.caminho_bd.stat().st_size
            
            return estatisticas
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar estatísticas do banco: {e}", exc_info=True)
            return estatisticas
        finally:
            if str(self.caminho_bd) != ":memory:":
                conn.close()
    
    def close(self) -> None:
        """Fecha a conexao persistente se existir"""
        if self._connection:
            self._connection.close()
            self._connection = None
            
    def __del__(self):
        """Cleanup ao destruir o objeto"""
        self.close()
