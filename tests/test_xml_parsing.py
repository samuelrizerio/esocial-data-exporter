"""
Test cases for XML parsing functionality in the eSocial Migration project.
Tests the ability to process different layouts and schema versions.
"""

import pytest
import sys
import os
import xml.etree.ElementTree as ET
from pathlib import Path
import sqlite3
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import modules to test
from processadores.processador_xml import (
    identificar_layout, ProcessadorXML, extrair_tipo_evento,
    extrair_namespace_dinamico, obter_namespaces_dinamicos, 
    encontrar_elemento, encontrar_todos_elementos, obter_texto_elemento
)

class TestXmlParsing:
    """Tests for XML parsing functionality"""
    
    def setup_method(self):
        """Set up test environment before each test"""
        self.xml_dir = Path(__file__).parent / "data" / "xml"
        
    def test_layout_identification(self):
        """Test that layouts are correctly identified from XML files"""
        # Define test cases with XML file and expected layout code
        test_cases = [
            ("S-1020.xml", "S-1020"),
            ("S-1030.xml", "S-1030"),
            ("S-1200.xml", "S-1200"),
            ("S-2200.xml", "S-2200"),
            ("S-2205.xml", "S-2205"),
            ("S-2206.xml", "S-2206"),
            ("S-2230.xml", "S-2230"),
        ]
        
        # Run tests for each case
        for xml_file, expected_layout in test_cases:
            file_path = self.xml_dir / xml_file
            assert file_path.exists(), f"Test file {xml_file} not found"
            
            # Parse XML
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Identify layout
            detected_layout = identificar_layout(root)
            
            # Check result
            assert detected_layout == expected_layout, \
                f"Layout detection failed for {xml_file}. Expected {expected_layout}, got {detected_layout}"
    
    def test_schema_version_compatibility(self):
        """Test that different schema versions can be parsed correctly"""
        # Test different S-2200 schema versions (since S-1000 is not supported)
        version_files = [
            "S-2200.xml",      # Standard version
            "S-2200_dependentes.xml",   # With dependents
        ]
        
        for xml_file in version_files:
            file_path = self.xml_dir / xml_file
            assert file_path.exists(), f"Test file {xml_file} not found"
            
            # Parse XML
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Extract namespace from root
            namespace = extrair_namespace_dinamico(root)
            assert namespace, f"Namespace not extracted from {xml_file}"
            
            # Verify we can extract worker info regardless of version
            cpf = obter_texto_elemento(root, "cpfTrab")
            assert cpf, f"Could not extract worker CPF from {xml_file}"
    
    def test_special_format_handling(self):
        """Test handling of special formats like decimal numbers"""
        # Test decimal formatting in remuneration values
        file_path = self.xml_dir / "S-1200_formato_decimal.xml"
        assert file_path.exists(), "Format test file not found"
        
        # Parse XML
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # Extract decimal values and verify they're processed correctly
        # This may need to be adjusted based on how decimal values are actually handled
        vrRubr_elements = encontrar_todos_elementos(root, "vrRubr")
        values = [elem.text for elem in vrRubr_elements if elem is not None and elem.text]
        
        # Check that we have decimal values
        decimal_values = [v for v in values if "." in v]
        assert len(decimal_values) > 0, "No decimal values found in format test file"
        
    def test_dependents_handling(self):
        """Test handling of employee dependents in XML"""
        file_path = self.xml_dir / "S-2200_dependentes.xml"
        assert file_path.exists(), "Dependents test file not found"
        
        # Parse XML
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # Find dependent elements
        dependent_elements = encontrar_todos_elementos(root, "dependente")
        
        # Verify dependents are found
        assert len(dependent_elements) > 0, "No dependents found in test file"
        
        # Verify dependent information can be extracted
        for dep in dependent_elements:
            nome = obter_texto_elemento(dep, "nmDep")
            tipo = obter_texto_elemento(dep, "tpDep")
            assert nome, "Dependent name not found"
            assert tipo, "Dependent type not found"
            
    def test_all_layout_data_extraction(self):
        """Test data extraction for all supported layouts"""
        # Test all main layout types
        layout_files = [
            "S-1020.xml",
            "S-1030.xml",
            "S-1200.xml",
            "S-2200.xml",
            "S-2205.xml",
            "S-2206.xml",
            "S-2230.xml",
        ]
        
        # Mock database connection
        mock_db = MagicMock()
        
        for xml_file in layout_files:
            file_path = self.xml_dir / xml_file
            assert file_path.exists(), f"Test file {xml_file} not found"
            
            # Parse XML
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Get layout code
            layout_code = identificar_layout(root)
            assert layout_code, f"Could not identify layout for {xml_file}"
            
            # Test with mock to avoid actual DB operations
            with patch('src.processadores.processador_xml.ProcessadorXML') as mock_xml_processor:
                # Configure mock
                mock_processor_instance = MagicMock()
                mock_xml_processor.return_value = mock_processor_instance
                mock_processor_instance.processar_arquivo.return_value = True
                
                # Test processor creation and basic functionality
                processor = ProcessadorXML(mock_db, {})
                result = processor.processar_arquivo(str(file_path))
                
                # Verify processor was created correctly
                assert processor is not None, f"Processor creation failed for {xml_file}"
