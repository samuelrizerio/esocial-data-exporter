"""
Testes básicos para validar o funcionamento da aplicação
"""

import os
import sys
import pytest
from pathlib import Path

# Adicionar o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from configuracao.configuracoes import Configuracoes
from banco_dados.gerenciador_banco_dados import GerenciadorBancoDados


class TestDatabase:
    """Testes para o módulo de banco de dados"""
    
    def setup_method(self):
        """Configuração para cada teste"""
        # Usar um banco de dados em memória para testes
        self.configuracoes = Configuracoes()
        self.configuracoes.CAMINHO_BANCO_DADOS = Path(":memory:")
        self.db = GerenciadorBancoDados(self.configuracoes.CAMINHO_BANCO_DADOS)
    
    def test_database_initialization(self):
        """Testa se o banco de dados e inicializado corretamente"""
        # Verificar se as tabelas foram criadas corretamente
        tables_query = self.db.executar_query("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [table['name'] for table in tables_query]
        
        expected_tables = [
            'esocial_s1020', 'esocial_s1030', 'esocial_s1200',
            'esocial_s2200', 'esocial_s2205', 'esocial_s2206', 'esocial_s2230',
            'esocial_dependentes'
        ]
        
        for table in expected_tables:
            assert table in tables, f"Tabela {table} nao foi criada"
    
    def test_insert_data(self):
        """Testa a inserção de dados no banco"""
        # Inserir um registro de teste
        dados = [{
            'cpf_trabalhador': '12345678901',
            'nome_trabalhador': 'Trabalhador Teste',
            'sexo': 'M',
            'data_nascimento': '1990-01-01'
        }]
        
        self.db.inserir_dados('esocial_s2200', dados)
        
        # Verificar se o registro foi inserido
        resultado = self.db.executar_query("SELECT * FROM esocial_s2200 WHERE cpf_trabalhador = '12345678901'")
        
        assert len(resultado) == 1
        assert resultado[0]['nome_trabalhador'] == 'Trabalhador Teste'
    
    def test_query_execution(self):
        """Testa a execução de consultas SQL"""
        # Inserir alguns registros de teste
        dados1 = {'codigo': 'C001', 'descricao': 'Cargo Teste 1', 'cbo': '123456'}
        dados2 = {'codigo': 'C002', 'descricao': 'Cargo Teste 2', 'cbo': '654321'}
        
        self.db.inserir_dados('esocial_s1030', dados1)
        self.db.inserir_dados('esocial_s1030', dados2)
        
        # Executar uma consulta SQL
        resultado = self.db.executar_query("SELECT * FROM esocial_s1030 ORDER BY codigo")
        
        assert len(resultado) == 2
        assert resultado[0]['codigo'] == 'C001'
        assert resultado[1]['codigo'] == 'C002'
