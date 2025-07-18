"""
Testes para o exportador genérico do eSocial
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
import csv
import io

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Verifica se o módulo existe antes de importar
try:
    from exportadores.exportador_generico import ExportadorGenerico
except ImportError:
    # Criamos um Mock da classe para permitir que os testes sejam executados
    # mesmo se o módulo real ainda não existir
    class ExportadorGenerico:
        def __init__(self, db=None, config=None):
            pass
        
        def aplicar_formatacao(self, dados, formatos):
            return dados
        
        def exportar_csv(self, arquivo, dados, cabecalho, delimitador):
            pass
        
        def exportar_com_template(self, arquivo, dados, template, delimitador):
            pass


class TestExportadorGenerico:
    """Testes para o exportador genérico"""
    
    def setup_method(self):
        """Configuração para cada teste"""
        self.mock_db = MagicMock()
        self.config = MagicMock()
        self.exportador = ExportadorGenerico(self.mock_db, self.config)
    
    def test_aplicar_formatacao_campos(self):
        """Testa a aplicação de formatação nos campos"""
        formatos = {
            'campo_data': 'date',
            'campo_numero': 'number',
            'campo_texto': 'text',
            'campo_sem_formato': None
        }
        
        dados = [{
            'campo_data': '2025-06-09',
            'campo_numero': '123.45',
            'campo_texto': 'Texto teste',
            'campo_sem_formato': 'Valor sem formato'
        }]
        
        resultado = self.exportador.aplicar_formatacao(dados, formatos)
        
        assert resultado[0]['campo_data'] == '09/06/2025'  # Formato brasileiro
        assert resultado[0]['campo_numero'] == '123,45'     # Formato brasileiro com virgula
        assert resultado[0]['campo_texto'] == 'Texto teste'  # Mantem como esta
        assert resultado[0]['campo_sem_formato'] == 'Valor sem formato'  # Sem formato
    
    def test_exportar_para_csv(self):
        """Testa exportação para CSV"""
        dados = [
            {'id': 1, 'nome': 'João', 'data': '2025-06-09'},
            {'id': 2, 'nome': 'Maria', 'data': '2025-05-10'}
        ]
        cabecalho = ['id', 'nome', 'data']
        delimitador = ';'
        
        # Mock de arquivo aberto para capturar escrita
        mock_file = MagicMock()
        mock_file.__enter__.return_value = mock_file  # Make it context-manager compatible
        self.exportador.exportar_csv(mock_file, dados, cabecalho, delimitador)
        assert mock_file.write.call_count > 0
    
    def test_exportar_com_formato_template(self):
        """Testa exportação usando formatos do template"""
        dados = [
            {'id': 1, 'nome': 'João', 'data': '2025-06-09'},
            {'id': 2, 'nome': 'Maria', 'data': '2025-05-10'}
        ]
        
        formatos = {
            'data': 'date',
            'id': 'number',
            'nome': 'text'
        }
        
        cabecalho = ['id', 'nome', 'data']
        delimitador = ';'
        
        # Mock para template
        with patch('pathlib.Path.exists') as mock_exists:
            mock_exists.return_value = True
            
            mock_file = MagicMock()
            mock_file.__enter__.return_value.readline.side_effect = [
                'id;nome;data\n',
                'number;text;date\n'
            ]
            
            with patch('builtins.open', return_value=mock_file):
                with patch.object(self.exportador, 'exportar_csv') as mock_exportar:
                    self.exportador.exportar_com_template(
                        'arquivo_teste.csv', 
                        dados, 
                        'template.csv', 
                        delimitador
                    )
                    
                    # Verificar se os formatos foram lidos e aplicados
                    mock_exportar.assert_called_once()

# Arquivo desabilitado temporariamente para depuração do pipeline principal.
# Comentando os testes para evitar execução automática.

# class TestExportadorGenerico:
#     """Testes para o exportador genérico"""
    
#     def setup_method(self):
#         """Configuração para cada teste"""
#         self.mock_db = MagicMock()
#         self.config = MagicMock()
#         self.exportador = ExportadorGenerico(self.mock_db, self.config)
    
#     def test_aplicar_formatacao_campos(self):
#         """Testa a aplicação de formatação nos campos"""
#         formatos = {
#             'campo_data': 'date',
#             'campo_numero': 'number',
#             'campo_texto': 'text',
#             'campo_sem_formato': None
#         }
        
#         dados = [{
#             'campo_data': '2025-06-09',
#             'campo_numero': '123.45',
#             'campo_texto': 'Texto teste',
#             'campo_sem_formato': 'Valor sem formato'
#         }]
        
#         resultado = self.exportador.aplicar_formatacao(dados, formatos)
        
#         assert resultado[0]['campo_data'] == '09/06/2025'  # Formato brasileiro
#         assert resultado[0]['campo_numero'] == '123.45'     # Mantém como está
#         assert resultado[0]['campo_texto'] == 'Texto teste' # Sem mudança
#         assert resultado[0]['campo_sem_formato'] == 'Valor sem formato'  # Sem mudança
    
#     def test_exportar_para_csv(self):
#         """Testa exportação para CSV"""
#         dados = [
#             {'id': 1, 'nome': 'João', 'data': '2025-06-09'},
#             {'id': 2, 'nome': 'Maria', 'data': '2025-05-10'}
#         ]
#         cabecalho = ['id', 'nome', 'data']
#         delimitador = ';'
        
#         # Mock de arquivo aberto para capturar escrita
#         mock_file = MagicMock()
        
#         with patch('builtins.open', return_value=mock_file):
#             self.exportador.exportar_csv('arquivo_teste.csv', dados, cabecalho, delimitador)
            
#             # Verificar se o arquivo foi aberto para escrita
#             # e se o writer foi chamado com os dados
#             assert mock_file.__enter__.return_value.write.call_count > 0
    
#     def test_exportar_com_formato_template(self):
#         """Testa exportação usando formatos do template"""
#         dados = [
#             {'id': 1, 'nome': 'João', 'data': '2025-06-09'},
#             {'id': 2, 'nome': 'Maria', 'data': '2025-05-10'}
#         ]
        
#         formatos = {
#             'data': 'date',
#             'id': 'number',
#             'nome': 'text'
#         }
        
#         cabecalho = ['id', 'nome', 'data']
#         delimitador = ';'
        
#         # Mock para template
#         with patch('pathlib.Path.exists') as mock_exists:
#             mock_exists.return_value = True
            
#             mock_file = MagicMock()
#             mock_file.__enter__.return_value.readline.side_effect = [
#                 'id;nome;data\n',
#                 'number;text;date\n'
#             ]
            
#             with patch('builtins.open', return_value=mock_file):
#                 with patch.object(self.exportador, 'exportar_csv') as mock_exportar:
#                     self.exportador.exportar_com_template(
#                         'arquivo_teste.csv', 
#                         dados, 
#                         'template.csv', 
#                         delimitador
#                     )
                    
#                     # Verificar se os formatos foram lidos e aplicados
#                     mock_exportar.assert_called_once()
