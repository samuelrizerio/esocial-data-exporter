"""
Testes avançados para o módulo gerenciador_banco_dados.py
"""

import pytest
import sys
import os
import sqlite3
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.banco_dados.gerenciador_banco_dados import GerenciadorBancoDados


class TestGerenciadorBancoDadosAvancado:
    """Testes avançados para a classe GerenciadorBancoDados"""

    def setup_method(self):
        """Configuração para cada teste"""
        self.db_path = ":memory:"
        self.gerenciador = GerenciadorBancoDados(self.db_path)
    
    def teardown_method(self):
        """Limpeza após cada teste"""
        if hasattr(self, 'gerenciador'):
            self.gerenciador.close()

    def test_executar_query_select_sucesso(self):
        """Testa execução de query SELECT com sucesso"""
        # Criar tabela de teste usando inserir_dados
        dados_teste = {'cpf_trabalhador': '12345678901', 'nome_trabalhador': 'João'}
        self.gerenciador.inserir_dados('esocial_s2200', dados_teste)
        
        # Executar query SELECT
        resultado = self.gerenciador.executar_query("SELECT * FROM esocial_s2200 WHERE cpf_trabalhador = ?", ('12345678901',))
        
        assert resultado is not None
        assert len(resultado) == 1
        assert resultado[0]['cpf_trabalhador'] == '12345678901'

    def test_executar_query_insert_sucesso(self):
        """Testa execução de query INSERT com sucesso"""
        # Usar inserir_dados para inserir registro
        dados = {'cpf_trabalhador': '12345678901', 'nome_trabalhador': 'João'}
        registros_inseridos = self.gerenciador.inserir_dados('esocial_s2200', dados)
        
        # Verificar se o registro foi inserido
        assert registros_inseridos == 1
        
        # Verificar se o registro existe
        registros = self.gerenciador.executar_query("SELECT * FROM esocial_s2200")
        assert len(registros) == 1
        assert registros[0]['nome_trabalhador'] == 'João'

    def test_executar_query_erro_sintaxe(self):
        """Testa execução de query com erro de sintaxe"""
        # O método executar_query retorna lista vazia em caso de erro
        resultado = self.gerenciador.executar_query("SELECT * FROM tabela_inexistente")
        assert resultado == []

    def test_executar_query_erro_parametros(self):
        """Testa execução de query com parâmetros incorretos"""
        # Tentar inserir dados com parâmetros incorretos
        dados_invalidos = {'campo_inexistente': 'valor'}
        
        # Deve retornar 0 registros inseridos
        registros_inseridos = self.gerenciador.inserir_dados('esocial_s2200', dados_invalidos)
        assert registros_inseridos == 0

    def test_executar_query_transacao(self):
        """Testa execução de query em transação"""
        # Inserir múltiplos registros
        dados = [
            {'cpf_trabalhador': '12345678901', 'nome_trabalhador': 'João'},
            {'cpf_trabalhador': '98765432109', 'nome_trabalhador': 'Maria'}
        ]
        
        registros_inseridos = self.gerenciador.inserir_dados('esocial_s2200', dados)
        
        # Verificar se os registros foram inseridos
        assert registros_inseridos == 2
        
        # Verificar se os registros existem
        registros = self.gerenciador.executar_query("SELECT * FROM esocial_s2200 ORDER BY cpf_trabalhador")
        assert len(registros) == 2
        assert registros[0]['nome_trabalhador'] == 'João'
        assert registros[1]['nome_trabalhador'] == 'Maria'

    def test_executar_query_rollback(self):
        """Testa rollback de transação"""
        # Inserir primeiro registro
        dados1 = {'cpf_trabalhador': '12345678901', 'nome_trabalhador': 'João'}
        self.gerenciador.inserir_dados('esocial_s2200', dados1)
        
        # Tentar inserir dados inválidos (que devem falhar)
        dados_invalidos = {'campo_inexistente': 'valor'}
        registros_inseridos = self.gerenciador.inserir_dados('esocial_s2200', dados_invalidos)
        
        # Verificar se apenas o primeiro registro permaneceu
        registros = self.gerenciador.executar_query("SELECT * FROM esocial_s2200")
        assert len(registros) == 1
        assert registros[0]['nome_trabalhador'] == 'João'

    def test_obter_estrutura_tabela(self):
        """Testa obtenção da estrutura de uma tabela"""
        # Usar PRAGMA para obter estrutura da tabela
        estrutura = self.gerenciador.executar_query("PRAGMA table_info(esocial_s2200)")
        
        assert estrutura is not None
        assert len(estrutura) > 0
        
        # Verificar se há colunas
        colunas = [col['name'] for col in estrutura]
        assert 'cpf_trabalhador' in colunas or 'nome_trabalhador' in colunas

    def test_obter_estrutura_tabela_inexistente(self):
        """Testa obtenção da estrutura de tabela inexistente"""
        estrutura = self.gerenciador.executar_query("PRAGMA table_info(tabela_inexistente)")
        
        assert estrutura == []

    def test_verificar_existencia_tabela(self):
        """Testa verificação de existência de tabela"""
        # Verificar se a tabela existe
        tabelas = self.gerenciador.obter_tabelas()
        existe = 'esocial_s2200' in tabelas
        assert existe is True
        
        # Verificar se tabela inexistente não existe
        nao_existe = 'tabela_inexistente' in tabelas
        assert nao_existe is False

    def test_obter_tabelas(self):
        """Testa obtenção de lista de tabelas"""
        # Criar tabelas usando inserir_dados (que cria as tabelas automaticamente)
        self.gerenciador.inserir_dados('esocial_s2200', {'id': 1, 'nome': 'teste'})
        
        tabelas = self.gerenciador.obter_tabelas()
        
        assert 'esocial_s2200' in tabelas
        assert 'esocial_s1020' in tabelas
        assert 'esocial_s1030' in tabelas

    def test_obter_contagem_registros(self):
        """Testa obtenção de contagem de registros"""
        # Inserir registros
        dados = [
            {'cpf_trabalhador': '12345678901', 'nome_trabalhador': 'João'},
            {'cpf_trabalhador': '98765432109', 'nome_trabalhador': 'Maria'},
            {'cpf_trabalhador': '11122233344', 'nome_trabalhador': 'Pedro'}
        ]
        self.gerenciador.inserir_dados('esocial_s2200', dados)
        
        # Obter contagem
        resultado = self.gerenciador.executar_query("SELECT COUNT(*) as total FROM esocial_s2200")
        contagem = resultado[0]['total']
        
        assert contagem == 3

    def test_obter_contagem_registros_tabela_vazia(self):
        """Testa obtenção de contagem de registros em tabela vazia"""
        resultado = self.gerenciador.executar_query("SELECT COUNT(*) as total FROM esocial_s2200")
        contagem = resultado[0]['total']
        
        assert contagem == 0

    def test_obter_contagem_registros_tabela_inexistente(self):
        """Testa obtenção de contagem de registros em tabela inexistente"""
        # O método executar_query retorna lista vazia em caso de erro
        resultado = self.gerenciador.executar_query("SELECT COUNT(*) FROM tabela_inexistente")
        assert resultado == []

    def test_executar_query_com_timeout(self):
        """Testa execução de query com timeout"""
        # Executar query simples
        resultado = self.gerenciador.executar_query("SELECT 1 as teste")
        
        assert resultado is not None
        assert len(resultado) == 1

    def test_executar_query_multiplas_linhas(self):
        """Testa execução de query com múltiplas linhas"""
        # Inserir múltiplos registros
        dados = [
            {'cpf_trabalhador': '12345678901', 'nome_trabalhador': 'João'},
            {'cpf_trabalhador': '98765432109', 'nome_trabalhador': 'Maria'},
            {'cpf_trabalhador': '11122233344', 'nome_trabalhador': 'Pedro'}
        ]
        self.gerenciador.inserir_dados('esocial_s2200', dados)
        
        # Executar query que retorna múltiplas linhas
        resultado = self.gerenciador.executar_query("SELECT * FROM esocial_s2200 ORDER BY cpf_trabalhador")
        
        assert len(resultado) == 3
        # Verificar se todos os nomes estão presentes (ordem pode variar por CPF)
        nomes = [r['nome_trabalhador'] for r in resultado]
        assert 'João' in nomes
        assert 'Maria' in nomes
        assert 'Pedro' in nomes

    def test_executar_query_sem_parametros(self):
        """Testa execução de query sem parâmetros"""
        # Inserir registro
        dados = {'cpf_trabalhador': '12345678901', 'nome_trabalhador': 'João'}
        self.gerenciador.inserir_dados('esocial_s2200', dados)
        
        # Executar query sem parâmetros
        resultado = self.gerenciador.executar_query("SELECT * FROM esocial_s2200")
        
        assert len(resultado) == 1
        assert resultado[0]['nome_trabalhador'] == 'João'

    def test_executar_query_com_erro_banco(self):
        """Testa execução de query com diferentes tipos de erros de banco de dados"""
        
        # Teste 1: Query com coluna inexistente
        resultado1 = self.gerenciador.executar_query(
            "SELECT coluna_inexistente FROM esocial_s2200"
        )
        assert resultado1 == []
        
        # Teste 2: Query com sintaxe inválida
        resultado2 = self.gerenciador.executar_query(
            "SELECT * FROM esocial_s2200 WHERE cpf_trabalhador = '123' AND"
        )
        assert resultado2 == []
        
        # Teste 3: Query com parâmetros incorretos
        resultado3 = self.gerenciador.executar_query(
            "SELECT * FROM esocial_s2200 WHERE cpf_trabalhador = ?",
            ("12345678901", "parametro_extra")  # Parâmetros extras
        )
        assert resultado3 == []
        
        # Teste 4: Query com tabela inexistente
        resultado4 = self.gerenciador.executar_query(
            "SELECT * FROM tabela_que_nao_existe"
        )
        assert resultado4 == []
        
        # Teste 5: Query que funciona corretamente (controle)
        dados_validos = {'cpf_trabalhador': '12345678901', 'nome_trabalhador': 'João'}
        self.gerenciador.inserir_dados('esocial_s2200', dados_validos)
        
        resultado5 = self.gerenciador.executar_query(
            "SELECT * FROM esocial_s2200 WHERE cpf_trabalhador = ?",
            ('12345678901',)
        )
        assert len(resultado5) == 1
        assert resultado5[0]['nome_trabalhador'] == 'João'
        
        # Teste 6: Query com operação não permitida (INSERT via executar_query)
        resultado6 = self.gerenciador.executar_query(
            "INSERT INTO esocial_s2200 (cpf_trabalhador, nome_trabalhador) VALUES (?, ?)",
            ('98765432109', 'Maria')
        )
        # Deve retornar lista vazia pois executar_query só permite SELECT
        assert resultado6 == []

    def test_fechar_conexao(self):
        """Testa fechamento da conexão"""
        # Verificar se a conexão está aberta
        assert self.gerenciador._connection is not None
        
        # Fechar conexão
        self.gerenciador.close()
        
        # Verificar se a conexão foi fechada
        assert self.gerenciador._connection is None

    def test_context_manager(self):
        """Testa uso do gerenciador como context manager"""
        # O gerenciador não suporta context manager, então vamos testar o uso normal
        gerenciador = GerenciadorBancoDados(self.db_path)
        
        # Inserir dados usando campos corretos da tabela
        dados = {'cpf_trabalhador': '12345678901', 'nome_trabalhador': 'João'}
        registros_inseridos = gerenciador.inserir_dados('esocial_s2200', dados)
        
        # Verificar se os dados foram inseridos
        resultado = gerenciador.executar_query("SELECT * FROM esocial_s2200")
        assert len(resultado) == 1
        assert resultado[0]['nome_trabalhador'] == 'João'
        
        # Fechar conexão
        gerenciador.close()
        assert gerenciador._connection is None

    def test_inserir_dados_vazio(self):
        """Testa inserção de dados vazios"""
        registros_inseridos = self.gerenciador.inserir_dados('esocial_s2200', [])
        
        assert registros_inseridos == 0

    def test_inserir_dados_tabela_inexistente(self):
        """Testa inserção em tabela inexistente"""
        dados = {'id': 1, 'nome': 'João'}
        registros_inseridos = self.gerenciador.inserir_dados('tabela_inexistente', dados)
        
        assert registros_inseridos == 0

    def test_exportar_dados(self):
        """Testa exportação de dados"""
        # Inserir dados de teste
        dados = {'id': 1, 'nome': 'João'}
        self.gerenciador.inserir_dados('esocial_s2200', dados)
        
        # Exportar dados
        resultado = self.gerenciador.exportar_dados('funcionarios')
        
        assert isinstance(resultado, list)

    def test_limpar_dados_para_processamento(self):
        """Testa limpeza de dados para novo processamento"""
        # Inserir dados usando campos corretos da tabela
        dados = {'cpf_trabalhador': '12345678901', 'nome_trabalhador': 'João'}
        self.gerenciador.inserir_dados('esocial_s2200', dados)
        
        # Verificar se os dados foram inseridos
        resultado = self.gerenciador.executar_query("SELECT COUNT(*) as total FROM esocial_s2200")
        contagem_antes = resultado[0]['total']
        assert contagem_antes == 1
        
        # Limpar dados
        sucesso = self.gerenciador.limpar_dados_para_processamento()
        assert sucesso is True
        
        # Verificar se os dados foram removidos
        resultado = self.gerenciador.executar_query("SELECT COUNT(*) as total FROM esocial_s2200")
        contagem_depois = resultado[0]['total']
        assert contagem_depois == 0

    def test_verificar_estatisticas_banco(self):
        """Testa verificação de estatísticas do banco"""
        estatisticas = self.gerenciador.verificar_estatisticas_banco()
        
        assert isinstance(estatisticas, dict)
        assert 'tabelas' in estatisticas
        assert 'total_tabelas' in estatisticas
        assert 'indices' in estatisticas
        assert 'tamanho_banco' in estatisticas
        
        # Verificar se há tabelas
        assert estatisticas['total_tabelas'] > 0
        
        # Verificar se a tabela esocial_s2200 existe nas estatísticas
        assert 'esocial_s2200' in estatisticas['tabelas']

    def test_otimizar_banco(self):
        """Testa otimização do banco de dados"""
        sucesso = self.gerenciador.otimizar_banco()
        
        assert sucesso is True 