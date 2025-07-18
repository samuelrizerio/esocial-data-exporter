"""
Testes para o módulo main.py
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.main import main, configurar_logging, analisar_argumentos


class TestMain:
    """Testes para as funções principais do main.py"""

    def setup_method(self):
        """Configuração para cada teste"""
        self.mock_config = MagicMock()
        self.mock_bd = MagicMock()
        self.mock_processador = MagicMock()
        self.mock_exportador = MagicMock()

    @patch('src.main.Configuracoes')
    @patch('src.main.GerenciadorBancoDados')
    @patch('src.main.ProcessadorXML')
    @patch('src.main.ExportadorTemplatesEmpresa')
    def test_main_sucesso(self, mock_exportador_class, mock_processador_class, mock_bd_class, mock_config_class):
        """Testa execução bem-sucedida da função main"""
        # Configurar mocks
        mock_config_class.return_value = self.mock_config
        mock_bd_class.return_value = self.mock_bd
        mock_processador_class.return_value = self.mock_processador
        mock_exportador_class.return_value = self.mock_exportador
        
        # Configurar retornos
        self.mock_processador.processar_diretorio.return_value = 5  # Número de arquivos processados
        self.mock_exportador.exportar_todos_templates.return_value = 10
        
        # Executar main
        with patch('sys.argv', ['main.py']):
            resultado = main()
        
        # Verificar se as funções foram chamadas
        mock_config_class.assert_called_once()
        mock_bd_class.assert_called_once()
        mock_processador_class.assert_called_once_with(self.mock_bd, self.mock_config)
        mock_exportador_class.assert_called_once_with(self.mock_bd, self.mock_config)
        
        # Verificar se o processamento foi executado
        self.mock_processador.processar_diretorio.assert_called_once()
        self.mock_exportador.exportar_todos_templates.assert_called_once()
        
        assert resultado == 0

    @patch('src.main.Configuracoes')
    @patch('src.main.GerenciadorBancoDados')
    @patch('src.main.ProcessadorXML')
    @patch('src.main.ExportadorTemplatesEmpresa')
    def test_main_erro_processamento(self, mock_exportador_class, mock_processador_class, mock_bd_class, mock_config_class):
        """Testa main com erro no processamento"""
        # Configurar mocks
        mock_config_class.return_value = self.mock_config
        mock_bd_class.return_value = self.mock_bd
        mock_processador_class.return_value = self.mock_processador
        mock_exportador_class.return_value = self.mock_exportador
        
        # Configurar erro no processamento (0 arquivos processados)
        self.mock_processador.processar_diretorio.return_value = 0
        self.mock_exportador.exportar_todos_templates.return_value = 5
        
        # Executar main
        with patch('sys.argv', ['main.py']):
            resultado = main()
        
        # Verificar se retornou sucesso (mesmo com 0 arquivos processados, não é erro)
        assert resultado == 0

    @patch('src.main.Configuracoes')
    @patch('src.main.GerenciadorBancoDados')
    @patch('src.main.ProcessadorXML')
    @patch('src.main.ExportadorTemplatesEmpresa')
    def test_main_erro_exportacao(self, mock_exportador_class, mock_processador_class, mock_bd_class, mock_config_class):
        """Testa main com erro na exportação"""
        # Configurar mocks
        mock_config_class.return_value = self.mock_config
        mock_bd_class.return_value = self.mock_bd
        mock_processador_class.return_value = self.mock_processador
        mock_exportador_class.return_value = self.mock_exportador
        
        # Configurar sucesso no processamento mas erro na exportação
        self.mock_processador.processar_diretorio.return_value = 5
        self.mock_exportador.exportar_todos_templates.return_value = 0
        
        # Executar main
        with patch('sys.argv', ['main.py']):
            resultado = main()
        
        # Verificar se retornou sucesso (mesmo com 0 templates exportados, não é erro)
        assert resultado == 0

    def test_configurar_logging(self):
        """Testa configuração de logging"""
        logger = configurar_logging("INFO")
        
        assert logger is not None
        assert logger.name == "src.main"

    def test_analisar_argumentos_padrao(self):
        """Testa análise de argumentos com valores padrão"""
        with patch('sys.argv', ['main.py']):
            args = analisar_argumentos()
            
            # Verificar se os argumentos foram analisados
            assert isinstance(args, dict)
            assert 'log_level' in args

    def test_analisar_argumentos_com_parametros(self):
        """Testa análise de argumentos com parâmetros"""
        with patch('sys.argv', ['main.py', '--input', '/test/input', '--output', '/test/output']):
            args = analisar_argumentos()
            
            assert args['input'] == '/test/input'
            assert args['output'] == '/test/output'

    def test_main_com_argumentos(self):
        """Testa main com argumentos de linha de comando"""
        with patch('sys.argv', ['main.py', '--help']):
            with patch('src.main.argparse.ArgumentParser.print_help') as mock_print_help:
                with pytest.raises(SystemExit):
                    main()
                
                # Verificar se a ajuda foi exibida
                mock_print_help.assert_called()

    @patch('src.main.Configuracoes')
    def test_main_erro_configuracao(self, mock_config_class):
        """Testa main com erro na configuração"""
        # Configurar erro na configuração
        mock_config_class.side_effect = Exception("Erro de configuração")
        
        # Executar main
        with patch('sys.argv', ['main.py']):
            resultado = main()
        
        # Verificar se retornou erro
        assert resultado == 1

    @patch('src.main.Configuracoes')
    @patch('src.main.GerenciadorBancoDados')
    def test_main_erro_banco_dados(self, mock_bd_class, mock_config_class):
        """Testa main com erro no banco de dados"""
        # Configurar mocks
        mock_config_class.return_value = self.mock_config
        mock_bd_class.side_effect = Exception("Erro de banco de dados")
        
        # Executar main
        with patch('sys.argv', ['main.py']):
            resultado = main()
        
        # Verificar se retornou erro
        assert resultado == 1

    def test_main_remocao_banco_existente(self):
        """Testa remoção de banco de dados existente"""
        with patch('sys.argv', ['main.py']):
            with patch('os.path.exists', return_value=True) as mock_exists:
                with patch('os.remove') as mock_remove:
                    with patch('src.main.Configuracoes'):
                        with patch('src.main.GerenciadorBancoDados'):
                            with patch('src.main.ProcessadorXML'):
                                with patch('src.main.ExportadorTemplatesEmpresa'):
                                    main()
                    
                    # Verificar se o arquivo foi removido
                    mock_remove.assert_called()

    def test_configurar_logging_nivel_invalido(self):
        """Testa configuração de logging com nível inválido"""
        # Deve usar INFO como padrão para nível inválido
        logger = configurar_logging("NIVEL_INVALIDO")
        
        assert logger is not None
        assert logger.name == "src.main"

    @patch('src.main.Configuracoes')
    @patch('src.main.GerenciadorBancoDados')
    @patch('src.main.ProcessadorXML')
    @patch('src.main.ExportadorTemplatesEmpresa')
    def test_main_processamento_sucesso_exportacao_sucesso(self, mock_exportador_class, mock_processador_class, mock_bd_class, mock_config_class):
        """Testa main com sucesso no processamento e exportação"""
        # Configurar mocks
        mock_config_class.return_value = self.mock_config
        mock_bd_class.return_value = self.mock_bd
        mock_processador_class.return_value = self.mock_processador
        mock_exportador_class.return_value = self.mock_exportador
        
        # Configurar sucesso em ambas as operações
        self.mock_processador.processar_diretorio.return_value = 10
        self.mock_exportador.exportar_todos_templates.return_value = 5
        
        # Executar main
        with patch('sys.argv', ['main.py']):
            resultado = main()
        
        # Verificar se retornou sucesso
        assert resultado == 0

    def test_analisar_argumentos_todos_parametros(self):
        """Testa análise de argumentos com todos os parâmetros"""
        with patch('sys.argv', [
            'main.py', 
            '--input', '/test/input',
            '--output', '/test/output',
            '--templates', '/test/templates',
            '--database', '/test/db.db',
            '--log-level', 'DEBUG'
        ]):
            args = analisar_argumentos()
            
            assert args['input'] == '/test/input'
            assert args['output'] == '/test/output'
            assert args['templates'] == '/test/templates'
            assert args['database'] == '/test/db.db'
            assert args['log_level'] == 'DEBUG' 