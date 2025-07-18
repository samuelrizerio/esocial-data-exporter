"""
Definições e configurações globais da aplicação
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
import configparser
import logging

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

class Configuracoes:
    """Classe de configurações da aplicação"""
    
    def __init__(self):
        # Definir o diretório raiz do projeto
        self.RAIZ_PROJETO = Path(__file__).parent.parent.parent.absolute()
        
        # Diretórios padrão
        self.DIR_DADOS = self.RAIZ_PROJETO / 'data'
        self.CAMINHO_ENTRADA = self.DIR_DADOS / 'input'
        self.CAMINHO_SAIDA = self.DIR_DADOS / 'output'
        self.CAMINHO_TEMPLATES = self.DIR_DADOS / 'templates'
        self.CAMINHO_BANCO_DADOS = self.DIR_DADOS / 'db' / 'esocial.db'
        self.CAMINHO_LOGGING_CONF = self.RAIZ_PROJETO / 'src' / 'configuracao' / 'logging.conf'
        
        # Verificar se os diretórios existem e criá-los se necessário
        self.CAMINHO_ENTRADA.mkdir(parents=True, exist_ok=True)
        self.CAMINHO_SAIDA.mkdir(parents=True, exist_ok=True)
        self.CAMINHO_TEMPLATES.mkdir(parents=True, exist_ok=True)
        self.CAMINHO_BANCO_DADOS.parent.mkdir(parents=True, exist_ok=True)
        
        # Layouts do eSocial suportados
        self.LAYOUTS_SUPORTADOS = [
            'S-1020',  # Tabela de Lotações Tributárias
            'S-1030',  # Tabela de Cargos/Funções
            'S-1200',  # Remuneração do Trabalhador
            'S-2200',  # Cadastramento Inicial do Vínculo
            'S-2205',  # Alteração de Dados Cadastrais
            'S-2206',  # Alteração de Contrato de Trabalho
            'S-2230',  # Afastamento Temporário
        ]
        
        # Configurações de processamento
        self.CONFIG_PROCESSAMENTO = {
            'tamanho_lote': 1000,  # Tamanho do lote para inserção em massa
            'tempo_limite_segundos': 300,  # Tempo limite para operações de BD
            'processamento_paralelo': False,  # Processamento paralelo
        }
        
        # Templates de exportação
        self.TEMPLATES_EXPORTACAO = {
            'funcionarios': {
                'nome_arquivo': 'funcionarios.csv',
                'cabecalho': True,
                'delimitador': ';',
                'query_name': 'funcionarios',
                'template_arquivo': '01_CONVTRABALHADOR.csv'
            },
            'cargos': {
                'nome_arquivo': 'cargos.csv',
                'cabecalho': True,
                'delimitador': ';',
                'query_name': 'cargos',
                'template_arquivo': '07_CARGOS.csv'
            },
            'lotacoes': {
                'nome_arquivo': 'lotacoes.csv',
                'cabecalho': True,
                'delimitador': ';',
                'query_name': 'lotacoes'
            },
            'remuneracoes': {
                'nome_arquivo': 'remuneracoes.csv',
                'cabecalho': True,
                'delimitador': ';',
                'query_name': 'remuneracoes',
                'template_arquivo': '06_CONVFICHA.csv'
            },
            'afastamentos': {
                'nome_arquivo': 'afastamentos.csv',
                'cabecalho': True,
                'delimitador': ';',
                'query_name': 'afastamentos',
                'template_arquivo': '08_CONVAFASTAMENTO.csv'
            }
        }
        
        # Definições de colunas para templates
        # Permite que os templates sejam gerados mesmo sem os arquivos físicos
        self.COLUNAS_TEMPLATES = {
            '01_CONVTRABALHADOR.csv': [
                '1 A-ID do empregador', '2 B-Código referência', '3 C-CPF trabalhador', '4 D-Nome trabalhador', 
                '5 E-Data nascimento trabalhador', '6 F-Apelido trabalhador', '7 G-Nome social trabalhador', 
                '8 H-Nome mae trabalhador', '9 I-Nome pai trabalhador', '10 J-Sexo trabalhador', 
                '11 K-Grau de instrução', '12 L-Raça/Cor do trabalhador', 
                '13 M-Estado civil do trabalhador', '14 N-Indicativo de deficiência', 
                '15 O-Indicativo de deficiência física', '16 P-Indicativo de deficiência visual', 
                '17 Q-Indicativo de deficiência auditiva', '18 R-Indicativo de deficiência mental', 
                '19 S-Indicativo de deficiência intelectual', '20 T-Trabalhador reabilitado ou adaptado',
                '21 U-Trabalhador faz parte de cota de deficiente', '22 V-Tipo sanguíneo',
                '23 W-Nome da cidade de  nascimento', '24 X-UF da cidade de nascimento', 
                '25 Y-Código do país de nascimento', '26 Z-Nome do país de nascimento', 
                '27 AA-Código de país de nacionalidade', '28 AB-Nome do país denacionalidade', 
                '29 AC-Código RAIS do país', '30 AD-É aposentado', '31 AE-Data de aposentaria', '32 AF-Reside no país', 
                '33 AG-Código do tipo de logradouro', '34 AH-Endereço do trabalhador',
                '35 AI-Número de endereço do trabalhador', '36 AJ-Complemento do endereço de trabalhador', 
                '37 AK-CEP do trabalhador', '38 AL-Bairro do trabalhador', 
                '39 AM-Código da cidade de residência do trabalhador', '40 NA-Nome da cidade de residência do trabalhador',
                '41 AO-UF de residência', '42 AP-Referência do endereço do trabalhador', '43 AQ-Telefone',
                '44 AR-Telefone 2', '45 AS-Email', '46 AT-Email alternativo', '47 AU-Contato de emergência',
                '48 AV-Telefone do contato de emergência', '49 AW-Parentesco do contato para emergência',
                '50 AX-Peso', '51 AY-Altura', '52 AZ-Calça', '53 BA-Camisa', '54 BB-Calçado', 
                '55 BC-Número do CNS', '56 BD-Número do RG', '57 BE-Órgão emissor do RG',
                '58 BF-Data de emissão do RG', '59 BG-UF de emissão do RG', '60 BH-Número do RNE',
                '61 BI-Órgão emissor do RNE', '62 BJ-UF de emissão do RNE', '63 BK-Data de emissão do RNE',
                '64 BL-Data da chegada no país', '65 BM-Classificação estrangeiro', 
                '66 BN-Estrangeiro casado com brasileiro', '67 BO-Estrangeiro com filhos brasileiros', 
                '68 BP-Número do passaporte', '69 BQ-País de origem do passaporte', 
                '70 BR-Data de emissão do passaporte', '71 BS-Data de validade do passaporte',
                '72 BT-Número do RIC', '73 BU-Órgão emissor do RIC', '74 BV-UF de emissão do RIC', 
                '75 BW-Data de emissão do RIC', '76 BXPIS', '77 BY-Data de emissão do PIS', 
                '78 BZ-Número da CTPS', '79 CA-Série da CTPS', '80 CB-UF da CTPS', '81 CC-Data de emissão da CTPS',
                '82 CD-Número do título de eleitor', '83 CE-Zona do título de eleitor', 
                '84 CF-Seção do título de eleitor', '85 CG-Código da cidade do título de eleitor',
                '86 CH-Nome da cidade do título de eleitor', '87 CI-UF do título de eleitor',
                '88 CJ-Data de emissão do título de eleitor', '89 CK-Número da CNH', '90 CL-Categoria da CNH',
                '91 CM-UF da CNH', '92 CN-Data de emissão da CNH', '93 CO-Data de emissão da primeira CNH',
                '94 CP-Data de validade da CNH', '95 CQ-Número do certificado de alistamento militar',
                '96 CR-Data de expedição da CAM', '97 CS-Região militar', '98 CT-Tipo de certificado militar',
                '99 CU-Número do certificado militar', '100 CV-Número de série do certificado militar',
                '101 CW-Data de expedição do certificado militar', '102 CX-Categoria do certificado militar',
                '103 CY-Observações sobre a situação militar', '104 CZ-Profissão', 
                '105 DA-Número de registro no conselho de classe', '106 DB-Órgão emissor do registro de classe',
                '107 DC-UF do conselho de classe', '108 DD-Data de emissão do registro no conselho', 
                '109 DE-Data de vencimento do registro no conselho', '110 DF-Observações gerais', 
                '111 DG-País de residência no exterior', '112 DH-Bairro de residência no exterior',
                '113 DI-Endereço de residência no exterior', '114 DJ-Número de residência no exterior', 
                '115 DK-Complemento no endereço de residência no exterior', '116 DL-Cidade de residência no exterior',
                '117 DM-UF de residência no exterior', '118 DN-CEP de residência no exterior', 
                '119 DO-Cadastrado em', '120 DP-Categoria', '121 DQ-Data de desligamento',
                '122 DR-Tipo pessoa origem', '123 DS-Tipo pessoa destino', '124 DT-Início de validade',
                '125 DU-Forma de pagamento', '126 DV-Código do banco para pagamento pessoa',
                '127 DW-Agência sem dígito', '128 DX-Dígito da agência', '129 DY-Conta bancária sem dígito',
                '130 DZ-Dígito da conta', '131 EA-Tipo de conta', '132 EB-Tipo de operação'
            ],
            '02_CONVCONTRATO.csv': [
                '1 A-ID do empregador', '2 B-Código do estabelecimento', '3 C-Código do trabalhador', '4 D-Nome do trabalhador',
                '5 E-Código de lotação tributária', '6 F-Número de registro', '7 G-Código do contrato', '8 H-Matrícula no eSocial',
                '9 I-Número de registro no ponto eletrônico', '10 J-Código da categoria do trabalhador', '11 K-Número de processo menor',
                '12 L-Tipo de regime trabalhista', '13 M-Tipo de regime previdenciário', '14 N-Código de vínculo empregatício',
                '15 O-Data de admissão', '16 P-Número de dias de contrato de experiência', '17 Q-Número de dias de prorrogação do contrato de experiênc',
                '18 R-Optante para FGTS', '19 S-Data de opção do FGTS', '20 T-Código de motivo de admissão', '21 U-Tipo de admissão', 
                '22 V-Tipo de admissão para o CAGED', '23 W-Indicativo de admissão', '24 X-Natureza da atividade', 
                '25 Y-Enviado ao CAGED diário', '26 Z-Está recebendo seguro desemprego', '27 AA-UF do emprego anterior CAGED',
                '28 AB-Tipo de contrato de trabalho', '29 AC-Cláusula assecuratória rescisão antecipada prazo deter',
                '30 AD-Data de vencimento contrato de experiência', '31 AE-Data de vencimento do contrato de prorrogação',
                '32 AF-Data de vencimento prazo determinado', '33 AG-Fato que determina o fim do prazo determinado',
                '34 AH-Código de estrutura organizacional', '35 AI-Nome da classe organizacional', '36 AJ-Código do cargo',
                '37 AK-Código da função', '38 AL-Tipo de salário', '39 AM-Nível salarial', '40 AN-Valor do salário',
                '41 AO-Código de carreira pública', '42 AP-Data de ingresso na carreira', '43 AQ-CNPJ do sindicato da categoria',
                '44 AR-CNPJ do sindicato filiado', '45 AS-Desconta mensalidade sindical', '46 AT-Desconta contribuição sindical',
                '47 AU-Pagou contribuição sindical no ano de admissão', '48 AV-Código da jornada de trabalho',
                '49 AW-Tipo de contrato em tempo parcial', '50 AX-Exporta ponto eletrônico', '51 AY-Data de entrada por transferência',
                '52 AZ-Tipo de entrada', '53 BA-Código anterior do colaborador', '54 BB-Data de desligamento',
                '55 BC-Código de desligamento', '56 BD-Recebe adiantamento quinzenal', '57 BE-Percentual de adiantamento quinzenal',
                '58 BF-Recebe adiantamento no mês', '59 BG-Calcula INSS', '60 BH-Número de processo INSS',
                '61 BI-Calcula IRRF', '62 BJ-Número de processo IRRF', '63 BK-Natureza do estágio',
                '64 BL-Nível de estágio', '65 BM-Área de atuação do estágio', '66 BN-Número da apólice de seguro',
                '67 BO-Data prevista do término de estágio', '68 BP-CPF do superior de estágio', '69 BQ-Nome do supervisor do estágio',
                '70 BR-Indicativo de provimento estatuário', '71 BS-Tipo de provimento estatuário', '72 BT-Data de nomeação do estatuário',
                '73 BU-Data de posse do estatuário', '74 BV-Data de exercício do estatuário', '75 BW-Tipo de plano de segregação',
                '76 BX-CPF do colaborador substituto', '77 BY-Mês base de reajuste', '78 BZ-Tipo de regime da jornada',
                '79 CA-Cadastrado em', '80 CB-Hipótese legal para contratação do temporário', '81 CC-Justificativa para a contratação do temporário',
                '82 CD-Tipo de inclusão do contrato temporário', '83 CE-Data de aviso prévio', '84 CF-Destino'
            ],
            '03_CONVCONTRATOALT.csv': [
                '1 A-ID do empregador', '2 B-Nome do trabalhador', '3 C -Código do contrato', '4 D-Tipo de transferência',
                '5 E-Data da alteração', '6 F-Alteração registrada em', '7 G-ID do novo empregador', '8 H-Código do novo estabelecimento',
                '9 I-Código do novo departamento', '10 J-Código do novo cargo', '11 K-Valor do novo salário', '12 L-Tipo do novo salário',
                '13 M-Código do motivo de reajuste', '14 N-Código da nova jornada de trabalho', '15 O-Código do novo sindicato'
            ],
            '04_CONVDEPENDENTE.csv': [
                '1 A-ID do empregador', '2 B  - Código do trabalhador', '3 C  - Código do tipo de dependente',
                '4 D  - Código do dependente', '5 E  - Nome do dependente', '6 F  - Início da vigência',
                '7 G  - Término da vigência', '8 H  - Sexo do dependente', '9 I  - Data de nascimento do dependente',
                '10 J  - Nome da mãe', '11 K  - CPF do dependente', '12 L  - Paga salário família',
                '13 M  - Data de baixa do salário  família', '14 N  - Dependente para IRRF',
                '15 O  - Data de baixa de dependente para IRRF', '16 P  - Filho deficiente recebe salário família',
                '17 Q  - Código da cidade de nascimento', '18 R  - Número da certidão de nascimento do dependente',
                '19 S  - Nome do cartório de registro', '20 T  - Número de registro', '21 U  - Número no livro de registro',
                '22 V  - Número na folha de registro', '23 W  - Data de registro em cartório',
                '24 X  - Data de entrega do documento', '25 Y  - Endereço do dependente',
                '26 Z  - Número de endereço', '27 AA  - Bairro', '28 AB  - Código da cidade',
                '29 AC  - CEP do dependente', '30 AD  - Telefone 1 do dependente', '31 AE  - Telefone 2 do dependente',
                '32 AF  - Observações', '33 AG  - Data de registro', '34 AH  - Número do cartão nacional de saúde',
                '35 AI  - Número da declaração de nascimento vivo', '36 AJ  - Número do RG do dependente',
                '37 AK  - Origem', '38 AL  - Destino'
            ],
            '05_FERIAS.csv': [
                '1 A-ID do empregador', '2 B - Nome do trabalhador', '3 C - Código do contrato',
                '4 D - Início do período aquisitivo', '5 E - Término do período aquisitivo',
                '6 F - Quantidade de dias de direito', '7 G - Quantidade de dias de direito proporcional',
                '8 H - Quantidade de dias de faltas no período', '9 I - Quantidade de dias afastado no período',
                '10 J - Quantidade de dias perdidos no período', '11 K - Quantidade de dias gozados no período',
                '12 L - Quantidade total de dias de ABONO', '13 M - Férias já concluída', '14 N - Tipo de pessoa',
                '15 O - Destino', '16 P - Tipo de férias', '17 Q - Data do aviso de férias',
                '18 R - Início de gozo', '19 S - Término de gozo', '20 T - Quantidade de dias de gozo de férias',
                '21 U - Quantidade de dias deabono', '22 V - Data do pagamento das férias',
                '23 Férias pagas em dobro', '24 13° salário adiantado nas férias'
            ],
            '06_CONVFICHA.csv': [
                '1 A-ID do empregador', '2 B-Código do estabelecimento', '3 C - Código do tipo de cálculo',
                '4 D  - Data do pagamento', '5 E  - Data inicial do cálculo', '6 F  - Data final do cálculo',
                '7 G  - Data de cálculo da folha', '8 H  - Data recolhimento da GRRF',
                '9 I  - Observações sobre o cálculo', '10 J-Código do contrato', '11 K  - Código do cargo',
                '12 L  - Código da função', '13 M  - Código do departamento', '14 N  - Código da jornada de trabalho',
                '15 O  - Código do sindicato', '16 P  - Valor do salário', '17 Q  - Tipo de salário',
                '18 R  - Qtde de horas contratuais mensais', '19 S  - Qtde dependentes para IR',
                '20 T  - Qtde dependentes para SF', '21 U  - Código de exposição à agentes nocivos',
                '22 V  - Grau de insalubridade', '23 W  - Tem periculosidade',
                '24 X  - Ensejo de aposentadoria especial', '25 Y  - Sigla da rubrica',
                '26 Z  - Sigla da rubrica para o recibo', '27 AA  - Descrição da rubrica para o recibo',
                '28 AB  - Razão ou qtde', '29 AC  - Valor da rubrica', '30 AD  - Classe da rubrica',
                '31 AE  - Período de referência'
            ],
            '07_CARGOS.csv': [
                '1 A-ID do empregador', '2 B-Código do cargo', '3 C-Nome do cargo', '4 D-ID do tipo de código',
                '5 E-ID do nível organizacional', '6 F-Código do CBO', '7 G-Início da validade', '8 H-Término da validade',
                '9 I-Descrição sumária', '10 J-Permite acúmulo de cargo', '11 L-Permite contagem especial do acúmulo de cargo',
                '12 M-Cargo de dedicação exclusiva', '13 N-Número da Lei que criou e/ou extinguiu e/ou restruturou o',
                '14 O-Data da Lei que criou e/ou extinguiu e/ou restruturou o ca', '15 P-Situação gerada pela Lei',
                '16 Q-O cargo tem função'
            ],
            '08_CONVAFASTAMENTO.csv': [
                '1 A-ID do empregador', '2-Nome do trabalhador', '3-Código do contrato', '4-Código do motivo de afastamento',
                '5-Data inicial de afastamento', '6-Data final de afastamento', '7-Observações do afastamento',
                '8-Descrição do motivo de afastamento'
            ],
            '09_CONVATESTADO.csv': [
                '1 - ID do empregador', '2 - Data da consulta', '3 - Hora da consulta', '4 - Data inicial',
                '5 - Hora inicial', '6 - Data final', '7 - Hora final', '8 - Qtde de dias do atestado',
                '9 - Código de identificação do contrato', '10 - Código CID', '11 - MedicoTpCons',
                '12 - Número de inscrição do médico', '13 - UF do CRM do médico'
            ]
        }
        
        # Sobrescrever configurações com variáveis de ambiente
        self._carregar_de_env()
        self.logging_config = self._carregar_logging_conf()
        self.log_level = self.logging_config.get('logging', {}).get('level', 'ERROR')
        self._configurar_logging(self.log_level)
    
    def _carregar_de_env(self) -> None:
        """Carrega configurações das variáveis de ambiente"""
        # Diretórios
        input_path = os.getenv('ESOCIAL_INPUT_PATH')
        if input_path:
            self.CAMINHO_ENTRADA = Path(input_path)
            
        output_path = os.getenv('ESOCIAL_OUTPUT_PATH')
        if output_path:
            self.CAMINHO_SAIDA = Path(output_path)
            
        templates_path = os.getenv('ESOCIAL_TEMPLATES_PATH')
        if templates_path:
            self.CAMINHO_TEMPLATES = Path(templates_path)
            
        database_path = os.getenv('ESOCIAL_DATABASE_PATH')
        if database_path:
            self.CAMINHO_BANCO_DADOS = Path(database_path)
        
        # Configurações de processamento
        batch_size = os.getenv('ESOCIAL_BATCH_SIZE')
        if batch_size:
            try:
                self.CONFIG_PROCESSAMENTO['tamanho_lote'] = int(batch_size)
            except ValueError:
                pass
            
        timeout = os.getenv('ESOCIAL_TIMEOUT_SECONDS')
        if timeout:
            try:
                self.CONFIG_PROCESSAMENTO['tempo_limite_segundos'] = int(timeout)
            except ValueError:
                pass
            
        parallel = os.getenv('ESOCIAL_PARALLEL_PROCESSING')
        if parallel:
            self.CONFIG_PROCESSAMENTO['processamento_paralelo'] = parallel.lower() == 'true'
    
    def _carregar_logging_conf(self) -> dict:
        """Carrega configurações do arquivo logging.conf."""
        config = configparser.ConfigParser()
        if self.CAMINHO_LOGGING_CONF.exists():
            config.read(self.CAMINHO_LOGGING_CONF)
            return {section: dict(config.items(section)) for section in config.sections()}
        return {}

    def _configurar_logging(self, level: str):
        """Configura o logging global conforme o nível informado."""
        # Adicionar nível ALL se não existir
        if not hasattr(logging, 'ALL'):
            setattr(logging, 'ALL', 0)
            logging.addLevelName(getattr(logging, 'ALL', 0), 'ALL')
        level_upper = level.upper()
        if level_upper == 'ALL':
            numeric_level = getattr(logging, 'ALL', 0)
        else:
            numeric_level = getattr(logging, level_upper, logging.ERROR)
        logging.basicConfig(level=numeric_level)

    def atualizar_log_level(self, novo_level: str):
        """Atualiza o nível de log em tempo de execução e salva no logging.conf."""
        self.log_level = novo_level.upper()
        self._configurar_logging(self.log_level)
        # Atualiza o arquivo logging.conf
        config = configparser.ConfigParser()
        if self.CAMINHO_LOGGING_CONF.exists():
            config.read(self.CAMINHO_LOGGING_CONF)
        if 'logging' not in config:
            config['logging'] = {}
        config['logging']['level'] = self.log_level
        with open(self.CAMINHO_LOGGING_CONF, 'w') as configfile:
            config.write(configfile)
    
    def atualizar_de_args(self, args: Dict[str, Any]) -> None:
        """
        Atualiza configurações a partir dos argumentos da linha de comando
        
        Args:
            args: Dicionário de argumentos
        """
        if args.get('input'):
            self.CAMINHO_ENTRADA = Path(args['input'])
            self.CAMINHO_ENTRADA.mkdir(parents=True, exist_ok=True)
            
        if args.get('output'):
            self.CAMINHO_SAIDA = Path(args['output'])
            self.CAMINHO_SAIDA.mkdir(parents=True, exist_ok=True)
            
        if args.get('templates'):
            self.CAMINHO_TEMPLATES = Path(args['templates'])
            self.CAMINHO_TEMPLATES.mkdir(parents=True, exist_ok=True)
            
        if args.get('database'):
            self.CAMINHO_BANCO_DADOS = Path(args['database'])
            self.CAMINHO_BANCO_DADOS.parent.mkdir(parents=True, exist_ok=True)
