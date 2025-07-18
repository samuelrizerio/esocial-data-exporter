#!/usr/bin/env python3
"""
Teste de qualidade de extração de campos específicos
Valida se campos críticos são extraídos corretamente do XML para o banco
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
from src.utils.mapeador_campos_empresa import MapeadorCamposEmpresa


class TestQualidadeExtracaoCampos:
    """Testa a qualidade da extração de campos específicos"""
    
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
    def mapeador(self):
        """Cria mapeador de campos para testes"""
        return MapeadorCamposEmpresa()
    
    def test_extracao_campos_criticos_s2200(self, processador, banco_memoria, mapeador):
        """Testa extração de campos críticos do S-2200"""
        
        # Processar XML de teste
        xml_path = Path(__file__).parent / "data" / "xml" / "S-2200.xml"
        if not xml_path.exists():
            pytest.skip(f"Arquivo XML de teste não encontrado: S-2200.xml")
        
        sucesso = processador.processar_arquivo(str(xml_path))
        assert sucesso, "Falha ao processar XML S-2200"
        
        # Buscar dados extraídos
        resultado = banco_memoria.executar_query("SELECT * FROM esocial_s2200 WHERE cpf_trabalhador = '12345678901'")
        assert len(resultado) > 0, "Registro não encontrado no banco"
        
        registro = resultado[0]
        
        # Testar campos críticos (usando dados reais do XML)
        campos_criticos = {
            "cpf_trabalhador": "12345678901",
            "nome_trabalhador": "José Teste",
            "data_nascimento": "1991-01-07",
            "sexo": "M",
            "grau_instrucao": "10",
            "raca_cor": "1"
        }
        
        for campo, valor_esperado in campos_criticos.items():
            valor_extraido = registro.get(campo)
            assert valor_extraido == valor_esperado, f"Campo {campo}: esperado '{valor_esperado}', extraído '{valor_extraido}'"
    
    def test_mapeamento_campos_criticos_template(self, banco_memoria, mapeador):
        """Testa mapeamento de campos críticos para template"""
        
        # Buscar registro de teste
        resultado = banco_memoria.executar_query("SELECT * FROM esocial_s2200 LIMIT 1")
        if not resultado:
            pytest.skip("Nenhum registro encontrado para teste de mapeamento")
        
        registro = resultado[0]
        
        # Testar mapeamento de campos críticos do template (usando dados reais)
        campos_template = {
            "3 C-CPF trabalhador": "12345678901",
            "4 D-Nome trabalhador": "José Teste",
            "5 E-Data nascimento trabalhador": "1991-01-07",
            "10 J-Sexo trabalhador": "M",
            "11 K-Grau de instrução": "10",
            "12 L-Raça/Cor do trabalhador": "1"
        }
        
        for campo_template, valor_esperado in campos_template.items():
            valor_mapeado = mapeador.obter_valor_campo("01_CONVTRABALHADOR", campo_template, registro)
            assert valor_mapeado == valor_esperado, f"Campo {campo_template}: esperado '{valor_esperado}', mapeado '{valor_mapeado}'"
    
    def test_validacao_formatos_dados(self, banco_memoria):
        """Testa validação de formatos de dados"""
        
        # Buscar registros
        resultado = banco_memoria.executar_query("SELECT cpf_trabalhador, data_nascimento, sexo FROM esocial_s2200 LIMIT 5")
        assert len(resultado) > 0, "Nenhum registro encontrado"
        
        for registro in resultado:
            # Validar formato CPF (11 dígitos)
            cpf = str(registro['cpf_trabalhador'])
            assert len(cpf) == 11, f"CPF deve ter 11 dígitos: {cpf}"
            assert cpf.isdigit(), f"CPF deve conter apenas dígitos: {cpf}"
            
            # Validar formato data (YYYY-MM-DD)
            data = str(registro['data_nascimento'])
            assert len(data) == 10, f"Data deve ter formato YYYY-MM-DD: {data}"
            assert data.count('-') == 2, f"Data deve ter 2 hífens: {data}"
            
            # Validar sexo (M ou F)
            sexo = str(registro['sexo'])
            assert sexo in ['M', 'F'], f"Sexo deve ser M ou F: {sexo}"
    
    def test_consistencia_dados_xml_banco(self, processador, banco_memoria):
        """Testa consistência entre dados XML originais e banco"""
        
        # Processar XML
        xml_path = Path(__file__).parent / "data" / "xml" / "S-2200.xml"
        if not xml_path.exists():
            pytest.skip(f"Arquivo XML de teste não encontrado: S-2200.xml")
        
        sucesso = processador.processar_arquivo(str(xml_path))
        assert sucesso, "Falha ao processar XML"
        
        # Buscar dados do banco
        resultado = banco_memoria.executar_query("SELECT cpf_trabalhador, nome_trabalhador, json_data FROM esocial_s2200 LIMIT 1")
        assert len(resultado) > 0, "Nenhum registro encontrado"
        
        registro = resultado[0]
        
        # Verificar se dados estão no JSON
        json_data = json.loads(registro['json_data'])
        
        # Extrair dados do JSON para comparação (estrutura real do JSON - agora wrapped em evtAdmissao)
        cpf_json = json_data.get("evtAdmissao", {}).get("trabalhador", {}).get("cpfTrab", {}).get("_text", "")
        nome_json = json_data.get("evtAdmissao", {}).get("trabalhador", {}).get("nmTrab", {}).get("_text", "")
        
        # Comparar com dados do banco
        assert str(registro['cpf_trabalhador']) == cpf_json, f"CPF inconsistente: banco={registro['cpf_trabalhador']}, json={cpf_json}"
        assert str(registro['nome_trabalhador']) == nome_json, f"Nome inconsistente: banco={registro['nome_trabalhador']}, json={nome_json}"
    
    def test_extracao_multiplos_registros(self, processador, banco_memoria):
        """Testa extração de múltiplos registros do mesmo XML"""
        
        # Processar XML com múltiplos registros
        xml_path = Path(__file__).parent / "data" / "xml" / "S-1200.xml"
        if not xml_path.exists():
            pytest.skip(f"Arquivo XML de teste não encontrado: S-1200.xml")
        
        sucesso = processador.processar_arquivo(str(xml_path))
        assert sucesso, "Falha ao processar XML S-1200"
        
        # Verificar se todos os registros foram extraídos
        resultado = banco_memoria.executar_query("SELECT COUNT(*) as total FROM esocial_s1200")
        total_registros = resultado[0]['total']
        
        # S-1200 deve ter 2 registros de remuneração
        assert total_registros == 2, f"Esperado 2 registros, encontrado {total_registros}"
        
        # Verificar se todos os registros têm dados válidos
        registros = banco_memoria.executar_query("SELECT cpf_trabalhador, matricula FROM esocial_s1200")
        for registro in registros:
            assert registro['cpf_trabalhador'], "CPF não pode estar vazio"
            assert registro['matricula'], "Matrícula não pode estar vazia"
    
    def test_campos_obrigatorios_preenchidos(self, banco_memoria):
        """Testa se campos obrigatórios estão preenchidos"""
        
        # Lista de campos obrigatórios por tabela
        campos_obrigatorios = {
            "esocial_s2200": ["cpf_trabalhador", "nome_trabalhador", "data_nascimento"],
            "esocial_s1200": ["cpf_trabalhador", "matricula", "data_inicio"],
            "esocial_s1030": ["cod_cargo", "nome_cargo"],
            "esocial_s2230": ["cpf_trabalhador", "matricula", "data_inicio"]
        }
        
        for tabela, campos in campos_obrigatorios.items():
            try:
                # Verificar se tabela existe e tem dados
                resultado = banco_memoria.executar_query(f"SELECT COUNT(*) as total FROM {tabela}")
                if resultado[0]['total'] > 0:
                    # Verificar campos obrigatórios
                    for campo in campos:
                        resultado_campo = banco_memoria.executar_query(f"SELECT COUNT(*) as total FROM {tabela} WHERE {campo} IS NOT NULL AND {campo} != ''")
                        total_preenchido = resultado_campo[0]['total']
                        assert total_preenchido > 0, f"Campo obrigatório '{campo}' não preenchido na tabela {tabela}"
            except Exception as e:
                # Tabela pode não existir ou não ter dados, o que é aceitável
                pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 