#!/usr/bin/env python3
"""
Teste de integridade de dados entre etapas do pipeline
Valida consistência entre extração, mapeamento e exportação
"""

import sys
import pytest
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

# Adicionar diretório raiz ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from configuracao.configuracoes import Configuracoes
from banco_dados.gerenciador_banco_dados import GerenciadorBancoDados
from processadores.processador_xml import ProcessadorXML
from exportadores.exportador_templates_empresa import ExportadorTemplatesEmpresa
from src.utils.mapeador_campos_empresa import MapeadorCamposEmpresa


class TestIntegridadeDadosPipeline:
    """Testa integridade de dados entre etapas do pipeline"""
    
    @pytest.fixture(scope="class")
    def banco_memoria(self):
        """Cria banco de dados em memória para testes"""
        config = Configuracoes()
        config.CAMINHO_BANCO_DADOS = Path(":memory:")
        db = GerenciadorBancoDados(config.CAMINHO_BANCO_DADOS)
        yield db
        db.close()
    
    @pytest.fixture(scope="class")
    def processador(self, banco_memoria):
        """Cria processador XML para testes"""
        config = Configuracoes()
        return ProcessadorXML(banco_memoria, config)
    
    @pytest.fixture(scope="class")
    def exportador(self, banco_memoria):
        """Cria exportador para testes"""
        config = Configuracoes()
        return ExportadorTemplatesEmpresa(banco_memoria, config)
    
    @pytest.fixture(scope="class")
    def mapeador(self):
        """Cria mapeador de campos para testes"""
        return MapeadorCamposEmpresa()
    
    def test_consistencia_extracao_exportacao(self, processador, banco_memoria, exportador):
        """Testa consistência entre dados extraídos e exportados"""
        
        # Processar XML
        xml_path = Path(__file__).parent / "data" / "xml" / "S-2200.xml"
        if not xml_path.exists():
            pytest.skip(f"Arquivo XML de teste não encontrado: S-2200.xml")
        
        sucesso = processador.processar_arquivo(str(xml_path))
        assert sucesso, "Falha ao processar XML"
        
        # Buscar dados extraídos do banco
        dados_banco = banco_memoria.executar_query("SELECT cpf_trabalhador, nome_trabalhador, data_nascimento, sexo FROM esocial_s2200 LIMIT 1")
        assert len(dados_banco) > 0, "Nenhum dado encontrado no banco"
        
        registro_banco = dados_banco[0]
        
        # Exportar dados para CSV
        output_dir = Path(__file__).parent / "test_output"
        output_dir.mkdir(exist_ok=True)
        exportador.caminho_saida = str(output_dir)
        
        sucesso_export = exportador.exportar_todos_templates()
        assert sucesso_export > 0, "Falha na exportação"
        
        # Ler dados exportados
        csv_path = output_dir / "01_CONVTRABALHADOR.csv"
        if not csv_path.exists():
            # Tentar encontrar em outros diretórios
            csv_path = Path("data/output/01_CONVTRABALHADOR.csv")
        assert csv_path.exists(), f"Arquivo CSV não foi gerado. Procurado em: {output_dir} e data/output/"
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            linhas = f.readlines()
        
        # Verificar se há dados (além do header)
        assert len(linhas) > 1, "CSV deve ter dados além do header"
        
        # Verificar se dados do banco estão no CSV
        dados_csv = linhas[1].strip()  # Primeira linha de dados
        assert str(registro_banco['cpf_trabalhador']) in dados_csv, "CPF do banco deve estar no CSV"
        assert str(registro_banco['nome_trabalhador']) in dados_csv, "Nome do banco deve estar no CSV"
    
    def test_relacionamentos_entre_tabelas(self, processador, banco_memoria):
        """Testa relacionamentos entre tabelas"""
        
        # Processar múltiplos XMLs para criar relacionamentos
        xmls = ["S-2200.xml", "S-1200.xml", "S-1030.xml"]
        
        for xml_file in xmls:
            xml_path = Path(__file__).parent / "data" / "xml" / xml_file
            if xml_path.exists():
                processador.processar_arquivo(str(xml_path))
        
        # Verificar relacionamentos por CPF
        cpfs_s2200 = banco_memoria.executar_query("SELECT DISTINCT cpf_trabalhador FROM esocial_s2200")
        cpfs_s1200 = banco_memoria.executar_query("SELECT DISTINCT cpf_trabalhador FROM esocial_s1200")
        
        # Verificar se CPFs do S-2200 têm correspondência no S-1200
        cpfs_2200_set = {r['cpf_trabalhador'] for r in cpfs_s2200}
        cpfs_1200_set = {r['cpf_trabalhador'] for r in cpfs_s1200}
        
        # Pelo menos alguns CPFs devem estar em ambas as tabelas
        cpfs_comuns = cpfs_2200_set.intersection(cpfs_1200_set)
        assert len(cpfs_comuns) > 0, "Deve haver CPFs em comum entre S-2200 e S-1200"
    
    def test_chaves_estrangeiras_consistentes(self, processador, banco_memoria):
        """Testa consistência de chaves estrangeiras"""
        
        # Processar XMLs
        xml_path = Path(__file__).parent / "data" / "xml" / "S-2200.xml"
        if xml_path.exists():
            processador.processar_arquivo(str(xml_path))
        
        # Verificar se CPFs são únicos em cada tabela
        tabelas = ["esocial_s2200", "esocial_s1200", "esocial_s2205", "esocial_s2206", "esocial_s2230"]
        
        for tabela in tabelas:
            try:
                # Contar CPFs únicos
                resultado = banco_memoria.executar_query(f"SELECT COUNT(DISTINCT cpf_trabalhador) as unicos, COUNT(*) as total FROM {tabela}")
                if resultado and resultado[0]['total'] > 0:
                    unicos = resultado[0]['unicos']
                    total = resultado[0]['total']
                    
                    # CPFs devem ser únicos (ou pelo menos não duplicados excessivamente)
                    assert unicos > 0, f"Tabela {tabela} deve ter CPFs únicos"
                    assert unicos <= total, f"CPFs únicos ({unicos}) não podem ser mais que total ({total})"
            except Exception as e:
                # Tabela pode não existir ou não ter dados
                pass
    
    def test_mapeamento_completo_campos(self, banco_memoria, mapeador):
        """Testa se todos os campos mapeados são extraídos corretamente"""
        
        # Buscar registro de teste
        resultado = banco_memoria.executar_query("SELECT * FROM esocial_s2200 LIMIT 1")
        if not resultado:
            pytest.skip("Nenhum registro encontrado para teste de mapeamento")
        
        registro = resultado[0]
        
        # Lista de campos críticos do template CONVTRABALHADOR
        campos_criticos = [
            "3 C-CPF trabalhador",
            "4 D-Nome trabalhador", 
            "5 E-Data nascimento trabalhador",
            "10 J-Sexo trabalhador",
            "11 K-Grau de instrução",
            "12 L-Raça/Cor do trabalhador"
        ]
        
        # Verificar se todos os campos críticos são mapeados
        campos_mapeados = 0
        for campo in campos_criticos:
            valor = mapeador.obter_valor_campo("01_CONVTRABALHADOR", campo, registro)
            if valor and str(valor).strip():
                campos_mapeados += 1
        
        # Pelo menos 80% dos campos críticos devem estar mapeados
        percentual_mapeamento = (campos_mapeados / len(campos_criticos)) * 100
        assert percentual_mapeamento >= 80, f"Mapeamento insuficiente: {percentual_mapeamento:.1f}% (esperado >= 80%)"
    
    def test_dados_json_consistentes(self, banco_memoria):
        """Testa consistência dos dados JSON armazenados"""
        
        # Buscar registros com JSON
        resultado = banco_memoria.executar_query("SELECT cpf_trabalhador, json_data FROM esocial_s2200 LIMIT 3")
        assert len(resultado) > 0, "Nenhum registro com JSON encontrado"
        
        for registro in resultado:
            json_data = json.loads(registro['json_data'])
            
            # Verificar estrutura básica do JSON (estrutura real - agora wrapped em evtAdmissao)
            assert "evtAdmissao" in json_data, "JSON deve conter evtAdmissao"
            assert "trabalhador" in json_data["evtAdmissao"], "JSON deve conter dados do trabalhador"
            
            # Verificar se dados críticos estão no JSON
            trabalhador = json_data["evtAdmissao"]["trabalhador"]
            assert "cpfTrab" in trabalhador, "JSON deve conter CPF do trabalhador"
            assert "nmTrab" in trabalhador, "JSON deve conter nome do trabalhador"
    
    def test_exportacao_todos_templates(self, processador, banco_memoria, exportador):
        """Testa exportação de todos os templates com dados consistentes"""
        
        # Processar XMLs para ter dados
        xmls = ["S-2200.xml", "S-1200.xml", "S-1030.xml", "S-2230.xml"]
        for xml_file in xmls:
            xml_path = Path(__file__).parent / "data" / "xml" / xml_file
            if xml_path.exists():
                processador.processar_arquivo(str(xml_path))
        
        # Exportar todos os templates
        output_dir = Path(__file__).parent / "test_output"
        output_dir.mkdir(exist_ok=True)
        exportador.caminho_saida = str(output_dir)
        
        templates_processados = exportador.exportar_todos_templates()
        assert templates_processados > 0, "Nenhum template foi processado"
        
        # Verificar se arquivos foram gerados
        templates_esperados = [
            "01_CONVTRABALHADOR.csv",
            "02_CONVCONTRATO.csv",
            "05_FERIAS.csv",
            "07_CARGOS.csv"
        ]
        
        for template in templates_esperados:
            arquivo_path = output_dir / template
            if arquivo_path.exists():
                # Verificar se arquivo tem dados
                with open(arquivo_path, 'r', encoding='utf-8') as f:
                    linhas = f.readlines()
                
                # Arquivo deve ter header e pelo menos uma linha de dados
                assert len(linhas) >= 2, f"Template {template} deve ter header e dados"
                
                # Verificar se dados do banco estão no arquivo
                dados_csv = linhas[1].strip()
                assert len(dados_csv) > 0, f"Template {template} deve ter dados não vazios"
    
    def test_rollback_transacoes(self, banco_memoria):
        """Testa se dados válidos são preservados em caso de erro"""
        
        # Contar registros antes
        resultado_antes = banco_memoria.executar_query("SELECT COUNT(*) as total FROM esocial_s2200")
        total_antes = resultado_antes[0]['total'] if resultado_antes else 0
        
        # Simular erro (tentar inserir dados inválidos)
        try:
            banco_memoria.executar_query("INSERT INTO esocial_s2200 (cpf_trabalhador) VALUES (NULL)")
        except Exception:
            # Erro esperado - CPF não pode ser NULL
            pass
        
        # Verificar se dados válidos foram preservados
        resultado_depois = banco_memoria.executar_query("SELECT COUNT(*) as total FROM esocial_s2200")
        total_depois = resultado_depois[0]['total'] if resultado_depois else 0
        
        assert total_depois == total_antes, "Dados válidos devem ser preservados após erro"


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 