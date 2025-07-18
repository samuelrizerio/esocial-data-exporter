"""
Teste para processamento de arquivos XML do eSocial e detecção de layouts
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import MagicMock, patch
import xml.etree.ElementTree as ET

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Importar o processador de XML
from processadores.processador_xml import ProcessadorXML, identificar_layout

# Only include supported layouts in the test
ESOCIAL_EVENT_PATTERNS = {
    'evtTabLotacao': 'S-1020',
    'evtTabCargo': 'S-1030',
    'evtRemun': 'S-1200',
    'evtAdmissao': 'S-2200',
    'evtAltCadastral': 'S-2205',
    'evtAltContratual': 'S-2206',
    'evtAfastTemp': 'S-2230'
}

class TestProcessadorXML:
    """Testes para o processador de XML"""

    def setup_method(self):
        """Configuração para cada teste"""
        self.mock_bd = MagicMock()
        self.mock_config = MagicMock()
        self.processador = ProcessadorXML(self.mock_bd, self.mock_config)
        
        # Diretório com arquivos XML de teste
        self.dir_teste = Path(__file__).parent / "data" / "xml"
        
    def test_detectar_layouts_todos_xmls(self):
        """Testa deteccao de layout para todos os XMLs de teste"""
        # Mapeamento de arquivos XML para seus layouts esperados
        xml_layouts = {
            "S-1020.xml": "S-1020",
            "S-1030.xml": "S-1030",
            "S-1200.xml": "S-1200",
            "S-2200.xml": "S-2200",
            "S-2205.xml": "S-2205",
            "S-2206.xml": "S-2206",
            "S-2230.xml": "S-2230",
        }
        
        for xml_file, expected_layout in xml_layouts.items():
            xml_path = self.dir_teste / xml_file
            
            # Verificar se o arquivo existe
            if not xml_path.exists():
                pytest.skip(f"Arquivo XML de teste nao encontrado: {xml_file}")
            
            # Carregar XML e verificar layout
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            # Usar a funcao de identificacao de layout
            layout = identificar_layout(root)
            
            print(f"Arquivo: {xml_file}, Layout detectado: {layout}, Esperado: {expected_layout}")
            assert layout == expected_layout, f"Layout incorreto para {xml_file}: esperado {expected_layout}, obtido {layout}"
    
    def test_deteccao_robusta_layout(self):
        """Testa deteccao robusta de layout com diferentes formatos de namespace"""
        for xml_file in self.dir_teste.glob("*.xml"):
            if not xml_file.exists():
                continue
            
            # Pular arquivos S-1000 que nao sao suportados
            if "S-1000" in xml_file.name or "S-1040" in xml_file.name or "S-1060" in xml_file.name or "S-1050" in xml_file.name or "S-1010" in xml_file.name or "S-1070" in xml_file.name or "S-2210" in xml_file.name or "S-2299" in xml_file.name or "S-1005" in xml_file.name:
                continue
    
            # Testar via método do processador
            layout = self.processador.detectar_layout_xml(str(xml_file))
    
            # Verificar se um layout foi identificado
            assert layout is not None, f"Falhou ao detectar layout para {xml_file.name}"
    
            # Verificar se o layout está entre os padrões conhecidos
            assert layout in ESOCIAL_EVENT_PATTERNS.values(), f"Layout desconhecido para {xml_file.name}: {layout}"
    
    @patch('src.processadores.processador_xml.identificar_layout')
    def test_processamento_completo(self, mock_identificar):
        """Testa processamento completo de arquivos XML"""
        # Configurar mock para retornar um layout conhecido e suportado
        mock_identificar.return_value = "S-2200"
        
        # Configurar processador para ter um handler para S-2200
        self.processador.processadores = {
            "S-2200": MagicMock(return_value=True)
        }
        
        # Caminho para um arquivo XML de teste
        xml_path = self.dir_teste / "S-2200.xml"
        if not xml_path.exists():
            pytest.skip("Arquivo XML de teste não encontrado")
        
        # Testar processamento
        resultado = self.processador._processar_arquivo(xml_path)
        
        # Verificar se o processamento foi bem-sucedido
        assert resultado is True
        
        # Verificar se o handler correto foi chamado
        assert self.processador.processadores["S-2200"].called

    def test_compatibilidade_versoes_esocial(self):
        """Testa compatibilidade com diferentes versões do eSocial"""
        # Versões que devem ser aceitas pelo processador
        versoes = [
            "http://www.esocial.gov.br/schema/evt/evtInfoEmpregador/v_S_01_00_00",
            "http://www.esocial.gov.br/schema/evt/evtTabLotacao/v_S_01_00_00",
            "http://www.esocial.gov.br/schema/evt/evtTabCargo/v_S_01_01_00",
            "http://www.esocial.gov.br/schema/evt/evtRemun/v_S_01_00_00",
            "http://www.esocial.gov.br/schema/evt/evtAdmissao/v_S_01_00_00",
            "http://www.esocial.gov.br/schema/evt/evtAltCadastral/v_S_01_00_00"
        ]
        
        for version in versoes:
            # Criar um XML simples com a versão a ser testada
            xml_string = f"""<?xml version="1.0" encoding="UTF-8"?>
            <eSocial xmlns="{version}">
                <evtInfoEmpregador Id="ID1234567890">
                    <ideEvento>
                        <tpAmb>1</tpAmb>
                    </ideEvento>
                </evtInfoEmpregador>
            </eSocial>
            """
            
            root = ET.fromstring(xml_string)
            
            # Verificar se o layout foi identificado corretamente
            layout = identificar_layout(root)
            
            # O layout deve ser reconhecido independente da versão
            assert layout is not None, f"Falhou na versão {version}"
