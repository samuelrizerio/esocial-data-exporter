#!/usr/bin/env python3
"""
Teste de exportação e validação de todos os layouts/CSVs principais do pipeline eSocial
"""

import sys
import pytest
import csv
from pathlib import Path
from configuracao.configuracoes import Configuracoes
from banco_dados.gerenciador_banco_dados import GerenciadorBancoDados
from processadores.processador_xml import ProcessadorXML
from exportadores.exportador_templates_empresa import ExportadorTemplatesEmpresa

# Lista de layouts/CSVs principais e seus arquivos XML de teste
LAYOUTS_CSVS = [
    ("01_CONVTRABALHADOR.csv", "S-2200.xml"),
    ("02_CONVCONTRATO.csv", "S-2200.xml"),
    ("03_CONVCONTRATOALT.csv", "S-2206.xml"),
    ("04_CONVDEPENDENTE.csv", "S-2200_dependentes.xml"),
    ("05_FERIAS.csv", "S-2230.xml"),
    ("06_CONVFICHA.csv", "S-1200.xml"),
    ("07_CARGOS.csv", "S-1030.xml"),
    ("08_CONVAFASTAMENTO.csv", "S-2230.xml"),
    ("09_CONVATESTADO.csv", "S-2230.xml"),
]

@pytest.mark.parametrize("csv_name, xml_name", LAYOUTS_CSVS)
def test_exportacao_layout(tmp_path, csv_name, xml_name):
    config = Configuracoes()
    config.CAMINHO_SAIDA = tmp_path
    config.CAMINHO_ENTRADA = Path("tests/data/xml")
    config.CAMINHO_TEMPLATES = Path("src/layouts/ORIGINAL")
    
    bd = GerenciadorBancoDados(str(tmp_path / "test.db"))
    processador = ProcessadorXML(bd, config)
    exportador = ExportadorTemplatesEmpresa(bd, config)
    exportador.caminho_saida = tmp_path
    
    # Processar o XML de teste
    xml_path = config.CAMINHO_ENTRADA / xml_name
    processador.processar_arquivo(str(xml_path))
    
    # Exportar o template
    exportador.exportar_todos_templates()
    
    # Validar se o arquivo foi criado
    csv_path = tmp_path / csv_name
    assert csv_path.exists(), f"Arquivo CSV {csv_name} não foi gerado"
    
    # Validar headers reais e linhas dentro do with open
    with open(csv_path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=';')
        headers = reader.fieldnames
        headers_reais = config.COLUNAS_TEMPLATES.get(csv_name)
        assert headers_reais is not None, f"Headers do template {csv_name} não encontrados"
        for header in headers_reais:
            assert header in headers, f"Header '{header}' ausente no CSV {csv_name}"
        linhas = list(reader)
        if csv_name not in ["03_CONVCONTRATOALT.csv", "04_CONVDEPENDENTE.csv", "07_CARGOS.csv"]:
            assert len(linhas) > 0, f"CSV {csv_name} não possui dados" 