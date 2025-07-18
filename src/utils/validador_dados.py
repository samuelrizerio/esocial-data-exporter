"""
Módulo para validação de dados do eSocial
"""

import re
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Union, Tuple

logger = logging.getLogger(__name__)

# Padrões de validação comuns
PADRAO_CPF = r'^\d{11}$'
PADRAO_CNPJ = r'^\d{14}$'
PADRAO_DATA = r'^\d{4}-\d{2}-\d{2}$'
PADRAO_PIS = r'^\d{11}$'

class ValidadorDados:
    """Classe para validação de dados do eSocial antes de inserção ou processamento"""
    
    @staticmethod
    def validar_cpf(cpf: str) -> bool:
        """
        Valida se o CPF tem formato válido
        
        Args:
            cpf: String do CPF para validar
            
        Returns:
            True se o CPF for válido, False caso contrário
        """
        if not cpf:
            return False
            
        # Remover caracteres não numéricos
        cpf = re.sub(r'\D', '', cpf)
        
        # Verificar tamanho
        if len(cpf) != 11:
            return False
            
        # Verificar se todos os dígitos são iguais - caso inválido
        if len(set(cpf)) == 1:
            return False
            
        # Validar dígitos verificadores
        # Primeiro dígito
        soma = 0
        for i in range(9):
            soma += int(cpf[i]) * (10 - i)
        resto = (soma * 10) % 11
        if resto == 10:
            resto = 0
        if resto != int(cpf[9]):
            return False
            
        # Segundo dígito
        soma = 0
        for i in range(10):
            soma += int(cpf[i]) * (11 - i)
        resto = (soma * 10) % 11
        if resto == 10:
            resto = 0
        if resto != int(cpf[10]):
            return False
            
        return True
    
    @staticmethod
    def validar_cnpj(cnpj: str) -> bool:
        """
        Valida se o CNPJ tem formato válido
        
        Args:
            cnpj: String do CNPJ para validar
            
        Returns:
            True se o CNPJ for válido, False caso contrário
        """
        if not cnpj:
            return False
            
        # Remover caracteres não numéricos
        cnpj = re.sub(r'\D', '', cnpj)
        
        # Verificar tamanho
        if len(cnpj) != 14:
            return False
            
        # Verificar se todos os dígitos são iguais - caso inválido
        if len(set(cnpj)) == 1:
            return False
            
        # Validar dígitos verificadores
        # Primeiro dígito
        multiplicadores = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        soma = 0
        for i in range(12):
            soma += int(cnpj[i]) * multiplicadores[i]
        resto = soma % 11
        if resto < 2:
            digito1 = 0
        else:
            digito1 = 11 - resto
        if digito1 != int(cnpj[12]):
            return False
            
        # Segundo dígito
        multiplicadores = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        soma = 0
        for i in range(13):
            soma += int(cnpj[i]) * multiplicadores[i]
        resto = soma % 11
        if resto < 2:
            digito2 = 0
        else:
            digito2 = 11 - resto
        if digito2 != int(cnpj[13]):
            return False
            
        return True
    
    @staticmethod
    def validar_data(data_str: str) -> bool:
        """
        Valida se a string de data está em um formato válido
        
        Args:
            data_str: String da data para validar (formato YYYY-MM-DD)
            
        Returns:
            True se a data for válida, False caso contrário
        """
        if not data_str:
            return True  # Data vazia é considerada válida (pode ser um campo opcional)
            
        # Verificar formato
        if not re.match(PADRAO_DATA, data_str):
            return False
            
        # Verificar se é uma data válida
        try:
            data = datetime.strptime(data_str, "%Y-%m-%d")
            # Verificar se está em um intervalo razoável
            ano_atual = datetime.now().year
            if data.year < 1900 or data.year > ano_atual + 1:
                return False
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validar_pis(pis: str) -> bool:
        """
        Valida se o PIS/NIS tem formato válido
        
        Args:
            pis: String do PIS para validar
            
        Returns:
            True se o PIS for válido, False caso contrário
        """
        if not pis:
            return True  # PIS vazio é considerado válido (pode ser um campo opcional)
            
        # Remover caracteres não numéricos
        pis = re.sub(r'\D', '', pis)
        
        # Verificar tamanho
        if len(pis) != 11:
            return False
            
        # Verificar se todos os dígitos são iguais - caso inválido
        if len(set(pis)) == 1:
            return False
            
        # Validar dígito verificador
        multiplicadores = [3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        soma = 0
        for i in range(10):
            soma += int(pis[i]) * multiplicadores[i]
        resto = soma % 11
        if resto < 2:
            digito = 0
        else:
            digito = 11 - resto
        
        return digito == int(pis[10])
    
    @staticmethod
    def formatar_cpf(cpf: str) -> str:
        """
        Formata um CPF para o padrão esperado (apenas dígitos)
        
        Args:
            cpf: String do CPF para formatar
            
        Returns:
            CPF formatado
        """
        if not cpf:
            return ""
        return re.sub(r'\D', '', cpf)
    
    @staticmethod
    def formatar_cnpj(cnpj: str) -> str:
        """
        Formata um CNPJ para o padrão esperado (apenas dígitos)
        
        Args:
            cnpj: String do CNPJ para formatar
            
        Returns:
            CNPJ formatado
        """
        if not cnpj:
            return ""
        return re.sub(r'\D', '', cnpj)
    
    @classmethod
    def validar_registro_s2200(cls, dados: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Valida os dados de um registro S-2200 (Cadastramento Inicial do Vínculo)
        
        Args:
            dados: Dicionário com os dados a serem validados
            
        Returns:
            Tupla com (sucesso, lista de mensagens de erro)
        """
        erros = []
        
        # Validar CPF
        cpf = dados.get('cpf_trabalhador', '')
        if cpf and not cls.validar_cpf(cpf):
            erros.append(f"CPF inválido: {cpf}")
        
        # Validar PIS
        pis = dados.get('nis_trabalhador', '')
        if pis and not cls.validar_pis(pis):
            erros.append(f"PIS/NIS inválido: {pis}")
        
        # Validar Data de Nascimento
        data_nascimento = dados.get('data_nascimento', '')
        if data_nascimento and not cls.validar_data(data_nascimento):
            erros.append(f"Data de nascimento inválida: {data_nascimento}")
        
        # Validar Data de Admissão
        data_admissao = dados.get('data_admissao', '')
        if data_admissao and not cls.validar_data(data_admissao):
            erros.append(f"Data de admissão inválida: {data_admissao}")
        
        # Validar CNPJ
        cnpj = dados.get('cnpj_empregador', '')
        if cnpj and not cls.validar_cnpj(cnpj):
            erros.append(f"CNPJ do empregador inválido: {cnpj}")
        
        return (len(erros) == 0, erros)
    
    @classmethod
    def validar_registro_s1020(cls, dados: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Valida os dados de um registro S-1020 (Tabela de Lotações Tributárias)
        
        Args:
            dados: Dicionário com os dados a serem validados
            
        Returns:
            Tupla com (sucesso, lista de mensagens de erro)
        """
        erros = []
        
        # Validar código da lotação
        codigo = dados.get('codigo', '')
        if not codigo:
            erros.append("Código da lotação é obrigatório")
        
        # Validar datas
        inicio_validade = dados.get('inicio_validade', '')
        if inicio_validade and not cls.validar_data(inicio_validade):
            erros.append(f"Data de início de validade inválida: {inicio_validade}")
        
        fim_validade = dados.get('fim_validade', '')
        if fim_validade:
            if not cls.validar_data(fim_validade):
                erros.append(f"Data de fim de validade inválida: {fim_validade}")
            # Verificar se a data fim é posterior à data início
            elif inicio_validade and fim_validade < inicio_validade:
                erros.append(f"Data de fim de validade ({fim_validade}) é anterior à data de início ({inicio_validade})")
        
        # Validar CNPJ
        cnpj = dados.get('cnpj_empregador', '')
        if cnpj and not cls.validar_cnpj(cnpj):
            erros.append(f"CNPJ do empregador inválido: {cnpj}")
        
        return (len(erros) == 0, erros)
    
    @classmethod
    def validar_registro_s1030(cls, dados: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Valida os dados de um registro S-1030 (Tabela de Cargos)
        
        Args:
            dados: Dicionário com os dados a serem validados
            
        Returns:
            Tupla com (sucesso, lista de mensagens de erro)
        """
        erros = []
        
        # Validar código do cargo
        codigo = dados.get('codigo', '')
        if not codigo:
            erros.append("Código do cargo é obrigatório")
        
        # Validar CBO
        cbo = dados.get('cbo', '')
        if cbo and len(cbo) != 6:
            erros.append(f"Código CBO inválido: {cbo}. Deve ter 6 dígitos.")
        
        # Validar datas
        inicio_validade = dados.get('inicio_validade', '')
        if inicio_validade and not cls.validar_data(inicio_validade):
            erros.append(f"Data de início de validade inválida: {inicio_validade}")
        
        fim_validade = dados.get('fim_validade', '')
        if fim_validade:
            if not cls.validar_data(fim_validade):
                erros.append(f"Data de fim de validade inválida: {fim_validade}")
            # Verificar se a data fim é posterior à data início
            elif inicio_validade and fim_validade < inicio_validade:
                erros.append(f"Data de fim de validade ({fim_validade}) é anterior à data de início ({inicio_validade})")
        
        # Validar CNPJ
        cnpj = dados.get('cnpj_empregador', '')
        if cnpj and not cls.validar_cnpj(cnpj):
            erros.append(f"CNPJ do empregador inválido: {cnpj}")
        
        return (len(erros) == 0, erros)
    
    @classmethod
    def validar_registro_s2299(cls, dados: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Valida os dados de um registro S-2299 (Desligamento)
        
        Args:
            dados: Dicionário com os dados a serem validados
            
        Returns:
            Tupla com (sucesso, lista de mensagens de erro)
        """
        erros = []
        
        # Validar CPF
        cpf = dados.get('cpf_trabalhador', '')
        if cpf and not cls.validar_cpf(cpf):
            erros.append(f"CPF inválido: {cpf}")
        
        # Validar Data de Desligamento
        data_desligamento = dados.get('data_desligamento', '')
        if not data_desligamento:
            erros.append(f"Data de desligamento é obrigatória")
        elif not cls.validar_data(data_desligamento):
            erros.append(f"Data de desligamento inválida: {data_desligamento}")
        
        # Verificar se há algum motivo de desligamento
        motivo_desligamento = dados.get('motivo_desligamento', '')
        if not motivo_desligamento:
            erros.append("Motivo de desligamento é obrigatório")
        
        # Validar CNPJ
        cnpj = dados.get('cnpj_empregador', '')
        if cnpj and not cls.validar_cnpj(cnpj):
            erros.append(f"CNPJ do empregador inválido: {cnpj}")
        
        return (len(erros) == 0, erros)
    
    @classmethod
    def sanitizar_dados(cls, dados: Dict[str, Any], tipo_registro: str) -> Dict[str, Any]:
        """
        Sanitiza e formata os dados antes de inserir no banco de dados
        
        Args:
            dados: Dicionário com os dados a serem sanitizados
            tipo_registro: Tipo de registro (ex: S-2200)
            
        Returns:
            Dicionário com dados sanitizados
        """
        dados_sanitizados = {}
        
        # Copiar os dados originais
        for chave, valor in dados.items():
            dados_sanitizados[chave] = valor
        
        # Formatações comuns
        if 'cpf_trabalhador' in dados:
            dados_sanitizados['cpf_trabalhador'] = cls.formatar_cpf(dados['cpf_trabalhador'])
        
        if 'cnpj_empregador' in dados:
            dados_sanitizados['cnpj_empregador'] = cls.formatar_cnpj(dados['cnpj_empregador'])
        
        # Sanitização específica por tipo de registro
        if tipo_registro == 'S-2200':
            # Remover caracteres especiais do nome
            if 'nome_trabalhador' in dados:
                dados_sanitizados['nome_trabalhador'] = re.sub(r'[^\w\s]', '', dados['nome_trabalhador'])
        
        elif tipo_registro == 'S-1020':
            # Garantir que o código da lotação esteja no formato correto
            if 'codigo' in dados:
                # Remover espaços em branco e caracteres especiais do código
                dados_sanitizados['codigo'] = re.sub(r'[^\w]', '', dados['codigo'])
        
        elif tipo_registro == 'S-1030':
            # Garantir que o código CBO esteja no formato correto (6 dígitos)
            if 'cbo' in dados and dados['cbo']:
                # Remover caracteres não numéricos e garantir comprimento
                cbo = re.sub(r'\D', '', dados['cbo'])
                # Preencher com zeros à esquerda para garantir 6 dígitos
                dados_sanitizados['cbo'] = cbo.zfill(6)[:6]
        
        elif tipo_registro == 'S-2299':
            # Sanitizar CPF
            if 'cpf_trabalhador' in dados:
                dados_sanitizados['cpf_trabalhador'] = cls.formatar_cpf(dados['cpf_trabalhador'])
                
            # Sanitizar valores monetários
            for campo in ['valor_rescisao', 'valor_multa_fgts']:
                if campo in dados and dados[campo]:
                    try:
                        valor = float(str(dados[campo]).replace(',', '.'))
                        dados_sanitizados[campo] = valor
                    except (ValueError, TypeError):
                        dados_sanitizados[campo] = 0.0
        
        return dados_sanitizados
