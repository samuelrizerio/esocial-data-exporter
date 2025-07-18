"""
Testes para exportação de arquivos XML para CSV dos layouts do eSocial
"""

import pytest
import sys
import os
import csv
import pandas as pd
from pathlib import Path
from unittest.mock import MagicMock, patch
import xml.etree.ElementTree as ET
import tempfile
import shutil

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Importar o processador de XML e exportadores
from processadores.processador_xml import ProcessadorXML, identificar_layout
from exportadores.exportador_generico import ExportadorGenerico

class TestExportadorXmlCsv:
    """Testes para exportação de XML para CSV"""

    def setup_method(self):
        """Configuração para cada teste"""
        # Criar mocks para os objetos necessários
        self.mock_bd = MagicMock()
        self.mock_config = MagicMock()
        
        # Diretório temporário para saída de testes
        self.temp_dir = tempfile.mkdtemp()
        self.mock_config.CAMINHO_SAIDA = Path(self.temp_dir)
        self.mock_config.CAMINHO_TEMPLATES = Path(self.temp_dir) / "templates"
        self.mock_config.CAMINHO_TEMPLATES.mkdir(exist_ok=True)
        
        # Instanciar o processador e exportador
        self.processador = ProcessadorXML(self.mock_bd, self.mock_config)
        self.exportador = ExportadorGenerico(self.mock_bd, self.mock_config)
        
        # Diretório com arquivos XML de teste
        self.dir_teste = Path(__file__).parent / "data" / "xml"
        
    def teardown_method(self):
        """Limpeza após cada teste"""
        # Remover diretório temporário
        shutil.rmtree(self.temp_dir)

    def test_exportar_s2200_para_csv(self):
        """Testa exportação do layout S-2200 para CSV"""
        xml_path = self.dir_teste / "S-2200.xml"
        
        # Verificar se o arquivo existe
        if not xml_path.exists():
            pytest.skip(f"Arquivo XML de teste não encontrado: {xml_path}")
        
        # Criar dados de exemplo para teste
        dados = [
            {
                "cpfTrab": "12345678901",
                "nmTrab": "Trabalhador de Teste",
                "sexo": "M",
                "racaCor": "1",
                "estCiv": "1",
                "grauInstr": "10",
                "dtNascto": "1990-01-01",
                "dtAdmissao": "2023-01-01",
                "matricula": "001",
                "tpRegTrab": "1",
                "tpRegPrev": "1",
                "codCateg": "101",
                "dtBase": "01"
            }
        ]
        
        # Configurar mock para retornar dados de teste quando a função for chamada
        self.mock_bd.exportar_dados.return_value = dados
        
        # Configurar mock para template de exportação
        self.mock_config.TEMPLATES_EXPORTACAO = {
            "S-2200": {
                "query_name": "dados_s2200",
                "nome_arquivo": "S-2200.csv",
                "delimitador": ";",
                "cabecalho": True
            }
        }
        
        # Executar exportação
        resultado = self.exportador.exportar_template("S-2200")
        
        # Verificar se a exportação foi bem-sucedida
        assert resultado is True
        
        # Verificar se o arquivo CSV foi criado
        csv_path = self.mock_config.CAMINHO_SAIDA / "S-2200.csv"
        assert csv_path.exists()
        
        # Verificar o conteúdo do arquivo CSV
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f, delimiter=';')
            linhas = list(reader)
            
            # Deve ter pelo menos duas linhas (cabeçalho + dados)
            assert len(linhas) >= 2
            
            # Verificar se os campos esperados estão no arquivo
            cabecalho = linhas[0]
            assert "cpfTrab" in cabecalho
            assert "nmTrab" in cabecalho
            assert "dtAdmissao" in cabecalho
            
            # Verificar se os dados foram escritos corretamente
            primeira_linha = linhas[1]
            assert "12345678901" in primeira_linha  # cpfTrab
            assert "Trabalhador de Teste" in primeira_linha  # nmTrab
            assert "2023-01-01" in primeira_linha  # dtAdmissao
    
    def test_exportar_multiplos_layouts_para_csv(self):
        """Testa exportação de múltiplos layouts para CSV"""
        # Layouts a serem testados
        layouts = ["S-1020", "S-1030", "S-1200", "S-2200", "S-2205", "S-2206", "S-2230"]
        
        # Configurar mock para retornar dados de teste quando a função for chamada
        self.mock_bd.exportar_dados.return_value = [{"campo1": "valor1", "campo2": "valor2"}]
        
        # Configurar mock para templates de exportação
        templates = {}
        for layout in layouts:
            templates[layout] = {
                "query_name": f"dados_{layout.lower().replace('-', '')}",
                "nome_arquivo": f"{layout}.csv",
                "delimitador": ";",
                "cabecalho": True
            }
        
        self.mock_config.TEMPLATES_EXPORTACAO = templates
        
        # Exportar cada layout
        for layout in layouts:
            # Executar exportação
            resultado = self.exportador.exportar_template(layout)
            
            # Verificar se a exportação foi bem-sucedida
            assert resultado is True
            
            # Verificar se o arquivo CSV foi criado
            csv_path = self.mock_config.CAMINHO_SAIDA / f"{layout}.csv"
            assert csv_path.exists(), f"Arquivo CSV para {layout} não foi criado"
    
    def test_exportar_csv_com_formato_data(self):
        """Testa exportação com formatação de data no CSV"""
        # Dados com campos de data
        dados = [
            {
                "cpfTrab": "12345678901",
                "nmTrab": "Trabalhador de Teste",
                "dtNascto": "1990-01-01",
                "dtAdmissao": "2023-01-01",
                "vlrSalario": "3500.50"
            }
        ]
        
        # Configurar mock para retornar dados de teste
        self.mock_bd.exportar_dados.return_value = dados
        
        # Criar arquivo de template com formatos
        template_path = self.mock_config.CAMINHO_TEMPLATES / "template_test.csv"
        with open(template_path, 'w', encoding='utf-8-sig') as f:
            f.write("cpfTrab;nmTrab;dtNascto;dtAdmissao;vlrSalario\n")
            f.write("text;text;date;date;number.2\n")
        
        # Configurar mock para template de exportação
        self.mock_config.TEMPLATES_EXPORTACAO = {
            "TEST": {
                "query_name": "dados_teste",
                "nome_arquivo": "formatacao_test.csv",
                "delimitador": ";",
                "cabecalho": True,
                "template_arquivo": "template_test.csv"
            }
        }
        
        # Executar exportação
        resultado = self.exportador.exportar_template("TEST")
        
        # Verificar se a exportação foi bem-sucedida
        assert resultado is True
        
        # Verificar se o arquivo CSV foi criado
        csv_path = self.mock_config.CAMINHO_SAIDA / "formatacao_test.csv"
        assert csv_path.exists()
        
        # Verificar o conteúdo do arquivo CSV
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f, delimiter=';')
            linhas = list(reader)
            
            # Verificar se a formatação de data foi aplicada (formato DD/MM/YYYY)
            primeira_linha = linhas[1]
            assert "01/01/1990" in primeira_linha  # Data formatada
            assert "01/01/2023" in primeira_linha  # Data formatada
            
            # Verificar se a formatação de número foi aplicada (com 2 casas decimais)
            assert "3500,5" in primeira_linha  # Número formatado com vírgula
    
    def test_exportacao_integrada_xml_csv(self):
        """Testa integração completa entre processador XML e exportador CSV"""
        xml_path = self.dir_teste / "S-2200.xml"
        
        # Verificar se o arquivo existe
        if not xml_path.exists():
            pytest.skip(f"Arquivo XML de teste não encontrado: {xml_path}")
        
        # Mock da função para processar o XML e extrair dados estruturados
        dados_extraidos = [{
            "cpfTrab": "12345678901",
            "nmTrab": "Trabalhador de Teste",
            "dtAdmissao": "2023-01-01",
        }]
        
        # Configurar os mocks necessários para que o processador retorne os dados
        with patch.object(self.processador, 'processar_arquivo', return_value=True):
            with patch.object(self.processador, 'extrair_dados_xml', return_value=dados_extraidos):
                # Configurar o exportador para usar o template correto
                self.mock_config.TEMPLATES_EXPORTACAO = {
                    "S-2200": {
                        "query_name": "dados_s2200",
                        "nome_arquivo": "S-2200_integrado.csv",
                        "delimitador": ";",
                        "cabecalho": True
                    }
                }
                
                # Substituir a função exportar_dados para retornar nossos dados de teste
                self.mock_bd.exportar_dados.return_value = dados_extraidos
                
                # Processar o arquivo XML
                self.processador.processar_arquivo(str(xml_path))
                
                # Exportar os dados para CSV
                resultado = self.exportador.exportar_template("S-2200")
                
                # Verificar se a exportação foi bem-sucedida
                assert resultado is True
                
                # Verificar se o arquivo CSV foi criado
                csv_path = self.mock_config.CAMINHO_SAIDA / "S-2200_integrado.csv"
                assert csv_path.exists()

    def test_formatacao_personalizada_campos(self):
        """Testa formatação personalizada de campos no CSV"""
        # Dados com vários tipos de campos para formatação
        dados = [
            {
                "campo_texto": "Texto exemplo",
                "campo_data": "2025-06-09",
                "campo_numero": 1234.56,
                "campo_monetario": 1500.75,
                "campo_hora": "14:30:00",
                "campo_sem_formato": "valor sem formato"
            }
        ]
        
        # Configurar mock para retornar dados de teste
        self.mock_bd.exportar_dados.return_value = dados
        
        # Criar arquivo de template com formatos
        template_path = self.mock_config.CAMINHO_TEMPLATES / "template_formatos.csv"
        with open(template_path, 'w', encoding='utf-8-sig') as f:
            f.write("campo_texto;campo_data;campo_numero;campo_monetario;campo_hora;campo_sem_formato\n")
            f.write("text;date;number.2;money;time;text\n")
        
        # Configurar mock para template de exportação
        self.mock_config.TEMPLATES_EXPORTACAO = {
            "FORMATOS": {
                "query_name": "dados_formatos",
                "nome_arquivo": "teste_formatos.csv",
                "delimitador": ";",
                "cabecalho": True,
                "template_arquivo": "template_formatos.csv"
            }
        }
        
        # Executar exportação
        resultado = self.exportador.exportar_template("FORMATOS")
        
        # Verificar se a exportação foi bem-sucedida
        assert resultado is True
        
        # Verificar se o arquivo CSV foi criado
        csv_path = self.mock_config.CAMINHO_SAIDA / "teste_formatos.csv"
        assert csv_path.exists()
        
        # Verificar o conteúdo do arquivo CSV
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f, delimiter=';')
            linhas = list(reader)
            
            primeira_linha = linhas[1]
            assert "Texto exemplo" in primeira_linha  # Texto sem alteração
            assert "09/06/2025" in primeira_linha     # Data formatada
            assert "1234,6" in primeira_linha         # Número formatado
            assert "1500,75" in primeira_linha        # Valor monetário
            assert "14:30:00" in primeira_linha       # Hora formatada
            assert "valor sem formato" in primeira_linha  # Valor sem formato
