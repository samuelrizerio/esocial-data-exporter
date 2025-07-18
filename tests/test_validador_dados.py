"""
Testes para o módulo de validação de dados
"""

import unittest
import sys
import os
from datetime import datetime

# Adiciona o diretório raiz ao path para importações
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.utils.validador_dados import ValidadorDados


class TestValidadorDados(unittest.TestCase):
    """Testes para a classe ValidadorDados"""

    def test_validar_cpf(self):
        """Testa validação de CPF"""
        # CPFs válidos
        self.assertTrue(ValidadorDados.validar_cpf("123.456.789-09"))
        self.assertTrue(ValidadorDados.validar_cpf("12345678909"))
        
        # CPFs inválidos
        self.assertFalse(ValidadorDados.validar_cpf("123.456.789-10"))
        self.assertFalse(ValidadorDados.validar_cpf("12345678910"))
        self.assertFalse(ValidadorDados.validar_cpf(""))

    def test_validar_cnpj(self):
        """Testa validação de CNPJ"""
        # CNPJs válidos
        self.assertTrue(ValidadorDados.validar_cnpj("12.345.678/0001-95"))
        self.assertTrue(ValidadorDados.validar_cnpj("12345678000195"))
        
        # CNPJs inválidos
        self.assertFalse(ValidadorDados.validar_cnpj("12.345.678/0001-96"))
        self.assertFalse(ValidadorDados.validar_cnpj("12345678000196"))
        self.assertFalse(ValidadorDados.validar_cnpj(""))

    def test_validar_data(self):
        """Testa validação de data"""
        # Data válida
        self.assertTrue(ValidadorDados.validar_data("2023-01-01"))
        
        # Data inválida
        self.assertFalse(ValidadorDados.validar_data("2023/01/01"))
        self.assertFalse(ValidadorDados.validar_data("01/01/2023"))
        self.assertFalse(ValidadorDados.validar_data("2023-13-01"))
        self.assertFalse(ValidadorDados.validar_data("2023-01-32"))
        
        # Data vazia
        self.assertTrue(ValidadorDados.validar_data(""))
        
        # Data muito antiga ou futura
        self.assertFalse(ValidadorDados.validar_data("1800-01-01"))
        # Validar data futura (1 ano à frente)
        ano_futuro = datetime.now().year + 2
        self.assertFalse(ValidadorDados.validar_data(f"{ano_futuro}-01-01"))

    def test_validar_pis(self):
        """Testa validação de PIS/NIS"""
        # PIS válido
        self.assertTrue(ValidadorDados.validar_pis("12345678919"))
        
        # PIS inválido
        self.assertFalse(ValidadorDados.validar_pis("12345678910"))
        self.assertFalse(ValidadorDados.validar_pis("11111111111"))
        
        # PIS vazio
        self.assertTrue(ValidadorDados.validar_pis(""))

    def test_sanitizar_dados_s2200(self):
        """Testa sanitização de dados S-2200"""
        dados = {
            'cpf_trabalhador': '123.456.789-09',
            'nome_trabalhador': 'João da Silva!@#',
            'cnpj_empregador': '12.345.678/0001-95',
        }
        
        dados_sanitizados = ValidadorDados.sanitizar_dados(dados, 'S-2200')
        
        self.assertEqual(dados_sanitizados['cpf_trabalhador'], '12345678909')
        self.assertEqual(dados_sanitizados['cnpj_empregador'], '12345678000195')
        self.assertEqual(dados_sanitizados['nome_trabalhador'], 'João da Silva')

    def test_sanitizar_dados_s1030(self):
        """Testa sanitização de dados S-1030"""
        dados = {
            'codigo': 'CARGO-123',
            'cbo': '123',
            'cnpj_empregador': '12.345.678/0001-95',
        }
        
        dados_sanitizados = ValidadorDados.sanitizar_dados(dados, 'S-1030')
        
        self.assertEqual(dados_sanitizados['cnpj_empregador'], '12345678000195')
        self.assertEqual(dados_sanitizados['cbo'], '000123')
        
    # def test_sanitizar_dados_s2299(self):
    #     """Testa sanitização de dados S-2299"""
    #     dados = {
    #         'valor_rescisao': '1234.56',
    #         'data_desligamento': '2025-06-09'
    #     }
    #     dados_sanitizados = ValidadorDados.sanitizar_dados_s2299(dados)
    #     self.assertEqual(dados_sanitizados['valor_rescisao'], 1234.56)
    #     self.assertEqual(dados_sanitizados['data_desligamento'], '2025-06-09')

    def test_validar_registro_s2200(self):
        """Testa validação de registro S-2200"""
        # Dados válidos
        dados_validos = {
            'cpf_trabalhador': '12345678909',
            'data_nascimento': '2000-01-01',
            'data_admissao': '2022-01-01',
            'cnpj_empregador': '12345678000195',
        }
        
        valido, erros = ValidadorDados.validar_registro_s2200(dados_validos)
        self.assertTrue(valido)
        self.assertEqual(len(erros), 0)
        
        # Dados inválidos
        dados_invalidos = {
            'cpf_trabalhador': '12345678900',  # CPF inválido
            'data_nascimento': '2000/01/01',   # Formato de data inválido
            'data_admissao': '2022-15-01',     # Data inválida
            'cnpj_empregador': '12345678000199', # CNPJ inválido
        }
        
        valido, erros = ValidadorDados.validar_registro_s2200(dados_invalidos)
        self.assertFalse(valido)
        self.assertEqual(len(erros), 4) # 4 erros

    # def test_validar_registro_s2299(self):
    #     """Testa validação de registro S-2299"""
    #     dados = {
    #         'cpf_trabalhador': '12345678909',
    #         'data_desligamento': '2025-06-09',
    #         'valor_rescisao': 1234.56
    #     }
    #     self.assertTrue(ValidadorDados.validar_registro_s2299(dados))
    #     
    #     # Dados inválidos
    #     dados_invalidos = {
    #         'cpf_trabalhador': '12345678910',  # CPF inválido
    #         'data_desligamento': '2025-06-09',
    #         'valor_rescisao': 1234.56
    #     }
    #     self.assertFalse(ValidadorDados.validar_registro_s2299(dados_invalidos))


if __name__ == "__main__":
    unittest.main()
