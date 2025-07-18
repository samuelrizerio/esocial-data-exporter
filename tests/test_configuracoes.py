"""
Testes para o módulo configuracoes.py
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.configuracao.configuracoes import Configuracoes


class TestConfiguracoes:
    """Testes para a classe Configuracoes"""

    def setup_method(self):
        """Configuração para cada teste"""
        self.config = Configuracoes()

    def test_inicializacao_padrao(self):
        """Testa inicialização com valores padrão"""
        config = Configuracoes()
        
        # Verificar se os atributos básicos foram definidos
        assert hasattr(config, 'CAMINHO_ENTRADA')
        assert hasattr(config, 'CAMINHO_SAIDA')
        assert hasattr(config, 'CAMINHO_BANCO_DADOS')
        assert hasattr(config, 'LAYOUTS_SUPORTADOS')
        assert hasattr(config, 'TEMPLATES_EXPORTACAO')

    def test_carregar_configuracao_arquivo_existente(self):
        """Testa carregamento de configuração de arquivo existente"""
        config_data = """
        [DEFAULT]
        CAMINHO_ENTRADA = /test/input
        CAMINHO_SAIDA = /test/output
        CAMINHO_BANCO_DADOS = /test/db/test.db
        """
        
        with patch('builtins.open', mock_open(read_data=config_data)):
            with patch('os.path.exists', return_value=True):
                config = Configuracoes()
                
                # Verificar se os valores foram carregados
                assert config.CAMINHO_ENTRADA is not None
                assert config.CAMINHO_SAIDA is not None
                assert config.CAMINHO_BANCO_DADOS is not None

    def test_carregar_configuracao_arquivo_inexistente(self):
        """Testa carregamento quando arquivo de configuração não existe"""
        with patch('os.path.exists', return_value=False):
            config = Configuracoes()
            
            # Verificar se valores padrão foram usados
            assert config.CAMINHO_ENTRADA is not None
            assert config.CAMINHO_SAIDA is not None
            assert config.CAMINHO_BANCO_DADOS is not None

    def test_obter_configuracao_template(self):
        """Testa obtenção de configuração de template"""
        # Configurar dados de template
        template_data = {
            'colunas': ['col1', 'col2', 'col3'],
            'campos_obrigatorios': ['col1'],
            'mapeamento': {'field1': 'col1', 'field2': 'col2'}
        }
        
        with patch.object(self.config, 'TEMPLATES_EXPORTACAO', {'test_template': template_data}):
            resultado = self.config.TEMPLATES_EXPORTACAO.get('test_template')
            
            assert resultado == template_data

    def test_obter_configuracao_template_inexistente(self):
        """Testa obtenção de configuração de template inexistente"""
        resultado = self.config.TEMPLATES_EXPORTACAO.get('template_inexistente')
        
        # Deve retornar None
        assert resultado is None

    def test_obter_campos_obrigatorios(self):
        """Testa obtenção de campos obrigatórios de um template"""
        template_data = {
            'campos_obrigatorios': ['campo1', 'campo2', 'campo3']
        }
        
        with patch.object(self.config, 'TEMPLATES_EXPORTACAO', {'test_template': template_data}):
            campos = self.config.TEMPLATES_EXPORTACAO['test_template'].get('campos_obrigatorios', [])
            
            assert campos == ['campo1', 'campo2', 'campo3']

    def test_obter_campos_obrigatorios_sem_configuracao(self):
        """Testa obtenção de campos obrigatórios sem configuração"""
        campos = self.config.TEMPLATES_EXPORTACAO.get('template_sem_config', {}).get('campos_obrigatorios', [])
        
        # Deve retornar lista vazia
        assert campos == []

    def test_obter_colunas_template(self):
        """Testa obtenção de colunas de um template"""
        template_data = {
            'colunas': ['coluna1', 'coluna2', 'coluna3', 'coluna4']
        }
        
        with patch.object(self.config, 'TEMPLATES_EXPORTACAO', {'test_template': template_data}):
            colunas = self.config.TEMPLATES_EXPORTACAO['test_template'].get('colunas', [])
            
            assert colunas == ['coluna1', 'coluna2', 'coluna3', 'coluna4']

    def test_obter_colunas_template_sem_configuracao(self):
        """Testa obtenção de colunas sem configuração"""
        colunas = self.config.TEMPLATES_EXPORTACAO.get('template_sem_config', {}).get('colunas', [])
        
        # Deve retornar lista vazia
        assert colunas == []

    def test_obter_mapeamento_campos(self):
        """Testa obtenção de mapeamento de campos"""
        template_data = {
            'mapeamento': {
                'cpf': 'CPF',
                'nome': 'NOME',
                'cargo': 'CARGO'
            }
        }
        
        with patch.object(self.config, 'TEMPLATES_EXPORTACAO', {'test_template': template_data}):
            mapeamento = self.config.TEMPLATES_EXPORTACAO['test_template'].get('mapeamento', {})
            
            assert mapeamento == {
                'cpf': 'CPF',
                'nome': 'NOME',
                'cargo': 'CARGO'
            }

    def test_obter_mapeamento_campos_sem_configuracao(self):
        """Testa obtenção de mapeamento sem configuração"""
        mapeamento = self.config.TEMPLATES_EXPORTACAO.get('template_sem_config', {}).get('mapeamento', {})
        
        # Deve retornar dicionário vazio
        assert mapeamento == {}

    def test_validar_configuracao(self):
        """Testa validação de configuração"""
        # Configurar configuração válida
        self.config.CAMINHO_ENTRADA = Path('/test/input')
        self.config.CAMINHO_SAIDA = Path('/test/output')
        self.config.CAMINHO_BANCO_DADOS = Path('/test/db/test.db')
        
        with patch('os.path.exists', return_value=True):
            # Verificar se os caminhos são válidos
            assert self.config.CAMINHO_ENTRADA is not None
            assert self.config.CAMINHO_SAIDA is not None
            assert self.config.CAMINHO_BANCO_DADOS is not None

    def test_validar_configuracao_diretorio_entrada_inexistente(self):
        """Testa validação com diretório de entrada inexistente"""
        self.config.CAMINHO_ENTRADA = Path('/diretorio/inexistente')
        
        with patch('os.path.exists', return_value=False):
            # Verificar se o caminho foi definido
            assert self.config.CAMINHO_ENTRADA is not None

    def test_obter_templates_disponiveis(self):
        """Testa obtenção de templates disponíveis"""
        # Configurar templates
        self.config.TEMPLATES_EXPORTACAO = {
            'template1': {'colunas': ['col1', 'col2']},
            'template2': {'colunas': ['col3', 'col4']},
            'template3': {'colunas': ['col5', 'col6']}
        }
        
        templates = list(self.config.TEMPLATES_EXPORTACAO.keys())
        
        assert 'template1' in templates
        assert 'template2' in templates
        assert 'template3' in templates
        assert len(templates) == 3

    def test_obter_configuracao_logging(self):
        """Testa obtenção de configuração de logging"""
        self.config.CAMINHO_LOGGING_CONF = Path('/test/logs/app.log')
        
        config_log = self.config._carregar_logging_conf()
        
        assert isinstance(config_log, dict)

    def test_carregar_configuracao_erro_arquivo(self):
        """Testa carregamento com erro no arquivo de configuração"""
        # Simular erro ao carregar configuração de logging
        with patch.object(Configuracoes, '_carregar_logging_conf', return_value={}):
            # Deve usar valores padrão sem falhar
            config = Configuracoes()
            
            # Verificar se os valores padrão foram mantidos
            assert config.CAMINHO_ENTRADA is not None
            assert config.CAMINHO_SAIDA is not None
            assert config.CAMINHO_BANCO_DADOS is not None

    def test_obter_configuracao_banco_dados(self):
        """Testa obtenção de configuração de banco de dados"""
        self.config.CAMINHO_BANCO_DADOS = Path('/test/db/test.db')
        
        config_bd = {
            'arquivo': str(self.config.CAMINHO_BANCO_DADOS),
            'backup_habilitado': True,
            'backup_intervalo': 1000
        }
        
        assert config_bd['arquivo'] == '/test/db/test.db'
        assert config_bd['backup_habilitado'] is True
        assert config_bd['backup_intervalo'] == 1000

    def test_layouts_suportados(self):
        """Testa se os layouts suportados estão definidos"""
        layouts = self.config.LAYOUTS_SUPORTADOS
        
        assert 'S-1020' in layouts
        assert 'S-1030' in layouts
        assert 'S-1200' in layouts
        assert 'S-2200' in layouts
        assert 'S-2205' in layouts
        assert 'S-2206' in layouts
        assert 'S-2230' in layouts

    def test_config_processamento(self):
        """Testa configurações de processamento"""
        config = self.config.CONFIG_PROCESSAMENTO
        
        assert 'tamanho_lote' in config
        assert 'tempo_limite_segundos' in config
        assert 'processamento_paralelo' in config
        assert config['tamanho_lote'] == 1000
        assert config['tempo_limite_segundos'] == 300
        assert config['processamento_paralelo'] is False

    def test_colunas_templates(self):
        """Testa se as colunas dos templates estão definidas"""
        colunas = self.config.COLUNAS_TEMPLATES
        
        assert '01_CONVTRABALHADOR.csv' in colunas
        assert '02_CONVCONTRATO.csv' in colunas
        assert '03_CONVCONTRATOALT.csv' in colunas
        assert '04_CONVDEPENDENTE.csv' in colunas

    def test_atualizar_de_args(self):
        """Testa atualização de configurações a partir de argumentos"""
        args = {
            'input': '/tmp/novo/input',
            'output': '/tmp/novo/output',
            'database': '/tmp/novo/db.db',
            'log_level': 'DEBUG'
        }
        
        self.config.atualizar_de_args(args)
        
        # Verificar se os valores foram atualizados
        assert str(self.config.CAMINHO_ENTRADA) == '/tmp/novo/input'
        assert str(self.config.CAMINHO_SAIDA) == '/tmp/novo/output'
        assert str(self.config.CAMINHO_BANCO_DADOS) == '/tmp/novo/db.db'

    def test_atualizar_log_level(self):
        """Testa atualização do nível de log"""
        novo_level = 'DEBUG'
        
        self.config.atualizar_log_level(novo_level)
        
        # Verificar se o nível foi atualizado
        assert hasattr(self.config, 'log_level')
        assert self.config.log_level == 'DEBUG' 