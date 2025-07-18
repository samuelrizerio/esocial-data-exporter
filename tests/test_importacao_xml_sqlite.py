"""
Teste de integração: Importação de XMLs do eSocial para SQLite
"""

import sys
import pytest
from pathlib import Path
from banco_dados.gerenciador_banco_dados import GerenciadorBancoDados
from processadores.processador_xml import ProcessadorXML
from configuracao.configuracoes import Configuracoes

@pytest.fixture(scope="module")
def banco_memoria():
    config = Configuracoes()
    config.CAMINHO_BANCO_DADOS = Path(":memory:")
    db = GerenciadorBancoDados(config.CAMINHO_BANCO_DADOS)
    yield db
    db.close()

@pytest.fixture(scope="module")
def processador(banco_memoria):
    config = Configuracoes()
    return ProcessadorXML(banco_memoria, config)

@pytest.mark.parametrize("xml_file, tabela, campo, valor_esperado, esperado_count, deve_falhar", [
    ("S-1020.xml", "esocial_s1020", None, None, 1, False),
    ("S-1030.xml", "esocial_s1030", None, None, 1, False),
    ("S-1200.xml", "esocial_s1200", None, None, 2, False),  # 2 registros de remuneracao
    ("S-2200.xml", "esocial_s2200", "cpf_trabalhador", "12345678901", 1, False),
    ("S-2205.xml", "esocial_s2205", None, None, 1, False),
    ("S-2206.xml", "esocial_s2206", None, None, 1, False),
    ("S-2230.xml", "esocial_s2230", None, None, 1, False),
    ("S-2200_dependentes.xml", "esocial_dependentes", None, None, 1, False),
])
def test_importa_xml_para_sqlite(processador, banco_memoria, xml_file, tabela, campo, valor_esperado, esperado_count, deve_falhar):
    """Testa importação de XML real para SQLite, múltiplos registros, erros e versões"""
    xml_path = Path(__file__).parent / "data" / "xml" / xml_file
    if not xml_path.exists():
        pytest.skip(f"Arquivo XML de teste não encontrado: {xml_file}")
    try:
        ok = processador.processar_arquivo(str(xml_path))
    except Exception as e:
        if deve_falhar:
            pytest.skip(f"Falha esperada ao processar {xml_file}: {e}")
        else:
            raise
    if deve_falhar:
        if not ok:
            pytest.skip(f"Falha esperada ao processar {xml_file}")
    else:
        assert ok, f"Falha ao processar {xml_file} (não era esperado)"
    # Consulta simples para validar inserção
    if campo and valor_esperado:
        resultado = banco_memoria.executar_query(f"SELECT * FROM {tabela} WHERE {campo} = ?", (valor_esperado,))
        assert len(resultado) >= 1, f"Registro não encontrado em {tabela} para {campo}={valor_esperado}"
    else:
        resultado = banco_memoria.executar_query(f"SELECT * FROM {tabela}")
        assert len(resultado) == esperado_count, f"Registros esperados: {esperado_count}, encontrados: {len(resultado)} em {tabela} após importação do XML"

# Teste para layouts futuros/opcionais (exemplo S-1010, S-1050, S-1070)
import pytest
@pytest.mark.parametrize("xml_file, tabela", [
    ("S-1010.xml", "esocial_s1010"),
    ("S-1050.xml", "esocial_s1050"),
    ("S-1070.xml", "esocial_s1070"),
])
@pytest.mark.skip(reason="Layout ainda não suportado, teste de placeholder para futura implementação.")
def test_layouts_futuros(xml_file, tabela):
    pass
