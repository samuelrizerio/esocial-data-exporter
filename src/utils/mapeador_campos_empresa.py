"""
Mapeamento de campos entre templates da Empresa e tabelas eSocial
"""

from typing import Dict, Any, List, Optional
import json


class MapeadorCamposEmpresa:
    """
    Mapeador de campos entre dados eSocial e templates da Empresa
    """
    
    def __init__(self):
        """Inicializa o mapeador com as definições de campo"""
        self.mapeamentos = self._definir_mapeamentos()
    
    def _definir_mapeamentos(self) -> Dict[str, Dict]:
        """
        Define os mapeamentos entre campos eSocial e templates Empresa
        
        Returns:
            Dicionário com mapeamentos por template
        """
        return {
            "01_CONVTRABALHADOR": {
                "fonte_principal": "esocial_s2200",
                "fontes_adicionais": ["esocial_s2205", "esocial_s2206"],
                "campos": {
                    # --- CAMPOS PRINCIPAIS MAPEADOS DIRETAMENTE DO BANCO ---
                    "1 A-ID do empregador": {"origem": "cnpj_empregador", "tipo": "string"},
                    "2 B-Código referência": {"origem": "cnpj_empregador", "tipo": "string"},
                    "3 C-CPF trabalhador": {"origem": "cpf_trabalhador", "tipo": "string"},
                    "4 D-Nome trabalhador": {"origem": "nome_trabalhador", "tipo": "string"},
                    "5 E-Data nascimento trabalhador": {"origem": "data_nascimento", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "6 F-Apelido trabalhador": {"origem": "nome_social", "tipo": "string"},
                    "7 G-Nome social trabalhador": {"origem": "nome_social", "tipo": "string"},
                    "8 H-Nome mae trabalhador": {"origem": "nm_mae", "tipo": "string"},
                    "9 I-Nome pai trabalhador": {"origem": "nm_pai", "tipo": "string"},
                    "10 J-Sexo trabalhador": {"origem": "sexo", "tipo": "string"},
                    "11 K-Grau de instrução": {"origem": "grau_instrucao", "tipo": "string"},
                    "12 L-Raça/Cor do trabalhador": {"origem": "raca_cor", "tipo": "string"},
                    "13 M-Estado civil do trabalhador": {"origem": "estado_civil", "tipo": "string"},
                    "14 N-Indicativo de deficiência": {"origem": "def_fisica", "tipo": "string"},
                    "15 O-Indicativo de deficiência física": {"origem": "def_fisica", "tipo": "string"},
                    "16 P-Indicativo de deficiência visual": {"origem": "def_visual", "tipo": "string"},
                    "17 Q-Indicativo de deficiência auditiva": {"origem": "def_auditiva", "tipo": "string"},
                    "18 R-Indicativo de deficiência mental": {"origem": "def_mental", "tipo": "string"},
                    "19 S-Indicativo de deficiência intelectual": {"origem": "def_intelectual", "tipo": "string"},
                    "20 T-Trabalhador reabilitado ou adaptado": {"origem": "reab_readap", "tipo": "string"},
                    "21 U-Trabalhador faz parte de cota de deficiente": {"origem": "info_cota", "tipo": "string"},
                    "22 V-Tipo sanguíneo": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "tipoSangue", "_text"], "tipo": "string"},
                    "23 W-Nome da cidade de  nascimento": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "nascimento", "nmCid", "_text"], "tipo": "string"},
                    "24 X-UF da cidade de nascimento": {"origem": "uf_nasc", "tipo": "string"},
                    "25 Y-Código do país de nascimento": {"origem": "pais_nasc", "tipo": "string"},
                    "26 Z-Nome do país de nascimento": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "nascimento", "paisNascto", "_text"], "tipo": "string"},
                    "27 AA-Código de país de nacionalidade": {"origem": "pais_nac", "tipo": "string"},
                    "28 AB-Nome do país denacionalidade": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "nascimento", "paisNac", "_text"], "tipo": "string"},
                    "29 AC-Código RAIS do país": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "nascimento", "codRais", "_text"], "tipo": "string"},
                    "30 AD-É aposentado": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "aposentado", "_text"], "tipo": "string"},
                    "31 AE-Data de aposentaria": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "dtAposent", "_text"], "tipo": "data", "formato": "YYYY-MM-DD"},
                    "32 AF-Reside no país": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "residePais", "_text"], "tipo": "string"},
                    "33 AG-Código do tipo de logradouro": {"origem": "tp_lograd", "tipo": "string"},
                    "34 AH-Endereço do trabalhador": {"origem": "dsc_lograd", "tipo": "string"},
                    "35 AI-Número de endereço do trabalhador": {"origem": "nr_lograd", "tipo": "string"},
                    "36 AJ-Complemento do endereço de trabalhador": {"origem": "complemento", "tipo": "string"},
                    "37 AK-CEP do trabalhador": {"origem": "cep", "tipo": "string"},
                    "38 AL-Bairro do trabalhador": {"origem": "bairro", "tipo": "string"},
                    "39 AM-Código da cidade de residência do trabalhador": {"origem": "cod_munic", "tipo": "string"},
                    "40 NA-Nome da cidade de residência do trabalhador": {"origem": "nm_cidade", "tipo": "string"},
                    "41 AO-UF de residência": {"origem": "uf_resid", "tipo": "string"},
                    "42 AP-Referência do endereço do trabalhador": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "endereco", "brasil", "referencia", "_text"], "tipo": "string"},
                    "43 AQ-Telefone": {"origem": "fone_princ", "tipo": "string"},
                    "44 AR-Telefone 2": {"origem": "fone_alt", "tipo": "string"},
                    "45 AS-Email": {"origem": "email_princ", "tipo": "string"},
                    "46 AT-Email alternativo": {"origem": "email_alt", "tipo": "string"},
                    "47 AU-Contato de emergência": {"origem": "contato_emerg", "tipo": "string"},
                    "48 AV-Telefone do contato de emergência": {"origem": "fone_emerg", "tipo": "string"},
                    "49 AW-Parentesco do contato para emergência": {"origem": "parentesco_emerg", "tipo": "string"},
                    "50 AX-Peso": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "peso", "_text"], "tipo": "string"},
                    "51 AY-Altura": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "altura", "_text"], "tipo": "string"},
                    "52 AZ-Calça": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "tamanhoCalca", "_text"], "tipo": "string"},
                    "53 BA-Camisa": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "tamanhoCamisa", "_text"], "tipo": "string"},
                    "54 BB-Calçado": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "tamanhoCalcado", "_text"], "tipo": "string"},
                    "55 BC-Número do CNS": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "documentos", "cns", "nrCns", "_text"], "tipo": "string"},
                    "56 BD-Número do RG": {"origem": "nr_rg", "tipo": "string"},
                    "57 BE-Órgão emissor do RG": {"origem": "orgao_emissor_rg", "tipo": "string"},
                    "58 BF-Data de emissão do RG": {"origem": "dt_exped_rg", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "59 BG-UF de emissão do RG": {"origem": "uf_rg", "tipo": "string"},
                    "60 BH-Número do RNE": {"origem": "nr_rne", "tipo": "string"},
                    "61 BI-Órgão emissor do RNE": {"origem": "orgao_emissor_rne", "tipo": "string"},
                    "62 BJ-UF de emissão do RNE": {"origem": "uf_rne", "tipo": "string"},
                    "63 BK-Data de emissão do RNE": {"origem": "dt_exped_rne", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "64 BL-Data da chegada no país": {"origem": "dt_chegada", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "65 BM-Classificação estrangeiro": {"origem": "class_trab_estrang", "tipo": "string"},
                    "66 BN-Estrangeiro casado com brasileiro": {"origem": "casado_br", "tipo": "string"},
                    "67 BO-Estrangeiro com filhos brasileiros": {"origem": "filhos_br", "tipo": "string"},
                    "68 BP-Número do passaporte": {"origem": "nr_passaporte", "tipo": "string"},
                    "69 BQ-País de origem do passaporte": {"origem": "pais_origem_passaporte", "tipo": "string"},
                    "70 BR-Data de emissão do passaporte": {"origem": "dt_exped_passaporte", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "71 BS-Data de validade do passaporte": {"origem": "dt_valid_passaporte", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "72 BT-Número do RIC": {"origem": "nr_ric", "tipo": "string"},
                    "73 BU-Órgão emissor do RIC": {"origem": "orgao_emissor_ric", "tipo": "string"},
                    "74 BV-UF de emissão do RIC": {"origem": "uf_ric", "tipo": "string"},
                    "75 BW-Data de emissão do RIC": {"origem": "dt_exped_ric", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "76 BXPIS": {"origem": "nis_trabalhador", "tipo": "string"},
                    "77 BY-Data de emissão do PIS": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "documentos", "pis", "dtExped", "_text"], "tipo": "data", "formato": "YYYY-MM-DD"},
                    "78 BZ-Número da CTPS": {"origem": "nr_ctps", "tipo": "string"},
                    "79 CA-Série da CTPS": {"origem": "serie_ctps", "tipo": "string"},
                    "80 CB-UF da CTPS": {"origem": "uf_ctps", "tipo": "string"},
                    "81 CC-Data de emissão da CTPS": {"origem": "dt_exped_ctps", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "82 CD-Número do título de eleitor": {"origem": "nr_titulo", "tipo": "string"},
                    "83 CE-Zona do título de eleitor": {"origem": "zona_titulo", "tipo": "string"},
                    "84 CF-Seção do título de eleitor": {"origem": "secao_titulo", "tipo": "string"},
                    "85 CG-Código da cidade do título de eleitor": {"origem": "cod_munic_titulo", "tipo": "string"},
                    "86 CH-Nome da cidade do título de eleitor": {"origem": "nm_cidade_titulo", "tipo": "string"},
                    "87 CI-UF do título de eleitor": {"origem": "uf_titulo", "tipo": "string"},
                    "88 CJ-Data de emissão do título de eleitor": {"origem": "dt_exped_titulo", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "89 CK-Número da CNH": {"origem": "nr_reg_cnh", "tipo": "string"},
                    "90 CL-Categoria da CNH": {"origem": "categoria_cnh", "tipo": "string"},
                    "91 CM-UF da CNH": {"origem": "uf_cnh", "tipo": "string"},
                    "92 CN-Data de emissão da CNH": {"origem": "dt_exped_cnh", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "93 CO-Data de emissão da primeira CNH": {"origem": "dt_pri_hab", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "94 CP-Data de validade da CNH": {"origem": "dt_valid_cnh", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "95 CQ-Número do certificado de alistamento militar": {"origem": "nr_certidao", "tipo": "string"},
                    "96 CR-Data de expedição da CAM": {"origem": "dt_exped_certidao", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "97 CS-Região militar": {"origem": "regiao_militar", "tipo": "string"},
                    "98 CT-Tipo de certificado militar": {"origem": "tipo_certidao", "tipo": "string"},
                    "99 CU-Número do certificado militar": {"origem": "nr_certidao2", "tipo": "string"},
                    "100 CV-Número de série do certificado militar": {"origem": "nr_serie", "tipo": "string"},
                    "101 CW-Data de expedição do certificado militar": {"origem": "dt_exped_certidao2", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "102 CX-Categoria do certificado militar": {"origem": "categoria_certidao", "tipo": "string"},
                    "103 CY-Observações sobre a situação militar": {"origem": "observacao_def", "tipo": "string"},
                    "104 CZ-Profissão": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "profissao", "_text"], "tipo": "string"},
                    "105 DA-Número de registro no conselho de classe": {"origem": "nr_registro_conselho", "tipo": "string"},
                    "106 DB-Órgão emissor do registro de classe": {"origem": "orgao_emissor_conselho", "tipo": "string"},
                    "107 DC-UF do conselho de classe": {"origem": "uf_conselho", "tipo": "string"},
                    "108 DD-Data de emissão do registro no conselho": {"origem": "dt_exped_conselho", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "109 DE-Data de vencimento do registro no conselho": {"origem": "dt_validade_conselho", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "110 DF-Observações gerais": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "observacoes", "_text"], "tipo": "string"},
                    "111 DG-País de residência no exterior": {"origem": "pais_resid", "tipo": "string"},
                    "112 DH-Bairro de residência no exterior": {"origem": "bairro_ext", "tipo": "string"},
                    "113 DI-Endereço de residência no exterior": {"origem": "dsc_lograd_ext", "tipo": "string"},
                    "114 DJ-Número de residência no exterior": {"origem": "nr_lograd_ext", "tipo": "string"},
                    "115 DK-Complemento no endereço de residência no exterior": {"origem": "complemento_ext", "tipo": "string"},
                    "116 DL-Cidade de residência no exterior": {"origem": "nm_cidade_ext", "tipo": "string"},
                    "117 DM-UF de residência no exterior": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "endereco", "exterior", "uf", "_text"], "tipo": "string"},
                    "118 DN-CEP de residência no exterior": {"origem": "cod_postal_ext", "tipo": "string"},
                    "119 DO-Cadastrado em": {"origem": "data_importacao", "tipo": "datetime", "formato": "YYYY-MM-DDTHH:mm:ss"},
                    "120 DP-Categoria": {"origem": "cod_categoria", "tipo": "string"},
                    "121 DQ-Data de desligamento": {"origem": "dt_deslig", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "122 DR-Tipo pessoa origem": {"origem": "json_data", "caminho_json": ["evtAdmissao", "vinculo", "sucessaoVinc", "origem", "_text"], "tipo": "string"},
                    "123 DS-Tipo pessoa destino": {"origem": "json_data", "caminho_json": ["evtAdmissao", "vinculo", "sucessaoVinc", "destino", "_text"], "tipo": "string"},
                    "124 DT-Início de validade": {"origem": "dt_adm", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "125 DU-Forma de pagamento": {"origem": "json_data", "caminho_json": ["evtAdmissao", "vinculo", "infoContrato", "localTrab", "infoLocalTrab", "endereco", "brasil", "formaPagamento", "_text"], "tipo": "string"},
                    "126 DV-Código do banco para pagamento pessoa": {"origem": "json_data", "caminho_json": ["evtAdmissao", "vinculo", "infoContrato", "localTrab", "infoLocalTrab", "endereco", "brasil", "banco", "codBanco", "_text"], "tipo": "string"},
                    "127 DW-Agência sem dígito": {"origem": "json_data", "caminho_json": ["evtAdmissao", "vinculo", "infoContrato", "localTrab", "infoLocalTrab", "endereco", "brasil", "banco", "nrAgencia", "_text"], "tipo": "string"},
                    "128 DX-Dígito da agência": {"origem": "json_data", "caminho_json": ["evtAdmissao", "vinculo", "infoContrato", "localTrab", "infoLocalTrab", "endereco", "brasil", "banco", "dvAgencia", "_text"], "tipo": "string"},
                    "129 DY-Conta bancária sem dígito": {"origem": "json_data", "caminho_json": ["evtAdmissao", "vinculo", "infoContrato", "localTrab", "infoLocalTrab", "endereco", "brasil", "banco", "nrConta", "_text"], "tipo": "string"},
                    "130 DZ-Dígito da conta": {"origem": "json_data", "caminho_json": ["evtAdmissao", "vinculo", "infoContrato", "localTrab", "infoLocalTrab", "endereco", "brasil", "banco", "dvConta", "_text"], "tipo": "string"},
                    "131 EA-Tipo de conta": {"origem": "json_data", "caminho_json": ["evtAdmissao", "vinculo", "infoContrato", "localTrab", "infoLocalTrab", "endereco", "brasil", "banco", "tpConta", "_text"], "tipo": "string"},
                    "132 EB-Tipo de operação": {"origem": "json_data", "caminho_json": ["evtAdmissao", "vinculo", "infoContrato", "localTrab", "infoLocalTrab", "endereco", "brasil", "banco", "tpOperacao", "_text"], "tipo": "string"},
                    "2 B-Código referência": {
                        "origem": "cnpj_empregador",
                        "caminho_json_alternativos": [
                            ["evtAdmissao", "ideEmpregador", "nrInsc", "_text"],
                            ["evtAltCadastral", "ideEmpregador", "nrInsc", "_text"]
                        ],
                        "tipo": "string", "obrigatorio": True, "valor_padrao": ""
                    },
                    "3 C-CPF trabalhador": {
                        "origem": "json_data",
                        "caminho_json": ["evtAdmissao", "trabalhador", "cpfTrab", "_text"],
                        "caminho_json_alternativos": [
                            ["trabalhador", "cpfTrab", "_text"],
                            ["trabalhador", "cpf", "_text"],
                            ["evtAltCadastral", "ideTrabalhador", "cpfTrab", "_text"],
                            ["ideTrabalhador", "cpfTrab", "_text"],
                            ["ideTrabalhador", "cpf", "_text"],
                            ["cpfTrab", "_text"],
                            ["cpf", "_text"]
                        ],
                        "tipo": "string", "obrigatorio": True, "valor_padrao": ""
                    },
                    "4 D-Nome trabalhador": {
                        "origem": "json_data",
                        "caminho_json": ["evtAdmissao", "trabalhador", "nmTrab", "_text"],
                        "caminho_json_alternativos": [
                            ["trabalhador", "nmTrab", "_text"],
                            ["trabalhador", "nome", "_text"],
                            ["evtAltCadastral", "alteracao", "dadosTrabalhador", "nmTrab", "_text"],
                            ["alteracao", "dadosTrabalhador", "nmTrab", "_text"],
                            ["evtAltContratual", "ideTrabalhador", "nmTrab", "_text"],
                            ["ideTrabalhador", "nmTrab", "_text"],
                            ["nome", "_text"]
                        ],
                        "tipo": "string", "obrigatorio": True, "valor_padrao": ""
                    },
                    "5 E-Data nascimento trabalhador": {
                        "origem": "json_data",
                        "caminho_json": ["evtAdmissao", "trabalhador", "nascimento", "dtNascto", "_text"],
                        "caminho_json_alternativos": [
                            ["trabalhador", "nascimento", "dtNascto", "_text"],
                            ["trabalhador", "dtNascto", "_text"],
                            ["nascimento", "dtNascto", "_text"],
                            ["dtNascto", "_text"],
                            ["trabalhador", "dataNascimento", "_text"],
                            ["dataNascimento", "_text"]
                        ],
                        "tipo": "data", "formato": "YYYY-MM-DD", "valor_padrao": ""
                    },
                    "6 F-Apelido trabalhador": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "nmSoc", "_text"], "tipo": "string"},
                    "7 G-Nome social trabalhador": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "nmSoc", "_text"], "tipo": "string"},
                    "8 H-Nome mae trabalhador": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "nascimento", "nmMae", "_text"], "tipo": "string"},
                    "9 I-Nome pai trabalhador": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "nascimento", "nmPai", "_text"], "tipo": "string"},
                    "10 J-Sexo trabalhador": {"origem": "sexo", "tipo": "string", "valores_validos": ["M", "F"]},
                    "11 K-Grau de instrução": {"origem": "grau_instrucao", "tipo": "string"},
                    "12 L-Raça/Cor do trabalhador": {"origem": "raca_cor", "tipo": "string"},
                    "Solteiro3 M-Estado civil do trabalhador": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "estCiv", "_text"], "tipo": "string"},
                    "76 BXPIS": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "nisTrab", "_text"], "tipo": "string"},
                    "119 DO-Cadastrado em": {"origem": "data_importacao", "tipo": "datetime", "formato": "YYYY-MM-DDTHH:mm:ss"},
                    "120 DP-Categoria": {"origem": "json_data", "caminho_json": ["evtAdmissao", "vinculo", "infoContrato", "codCateg", "_text"], "tipo": "string"},
                    "124 DT-Início de validade": {"origem": "json_data", "caminho_json": ["evtAdmissao", "vinculo", "infoRegimeTrab", "infoCeletista", "dtAdm", "_text"], "tipo": "data", "formato": "YYYY-MM-DD"},
                    "33 AG-Código do tipo de logradouro": {
                        "origem": "json_data",
                        "caminho_json": ["evtAdmissao", "trabalhador", "endereco", "brasil", "tpLograd", "_text"],
                        "caminho_json_alternativos": [
                            ["trabalhador", "endereco", "brasil", "tpLograd", "_text"],
                            ["endereco", "brasil", "tpLograd", "_text"],
                            ["trabalhador", "endereco", "tpLograd", "_text"],
                            ["endereco", "tpLograd", "_text"],
                            ["tpLograd", "_text"]
                        ],
                        "tipo": "string", "valor_padrao": ""
                    },
                    "34 AH-Endereço do trabalhador": {
                        "origem": "json_data",
                        "caminho_json": ["evtAdmissao", "trabalhador", "endereco", "brasil", "dscLograd", "_text"],
                        "caminho_json_alternativos": [
                            ["trabalhador", "endereco", "brasil", "dscLograd", "_text"],
                            ["endereco", "brasil", "dscLograd", "_text"],
                            ["trabalhador", "endereco", "dscLograd", "_text"],
                            ["endereco", "dscLograd", "_text"],
                            ["dscLograd", "_text"],
                            ["trabalhador", "endereco", "logradouro", "_text"],
                            ["endereco", "logradouro", "_text"],
                            ["logradouro", "_text"]
                        ],
                        "tipo": "string", "valor_padrao": ""
                    },
                    "35 AI-Número de endereço do trabalhador": {
                        "origem": "json_data",
                        "caminho_json": ["evtAdmissao", "trabalhador", "endereco", "brasil", "nrLograd", "_text"],
                        "caminho_json_alternativos": [
                            ["trabalhador", "endereco", "brasil", "nrLograd", "_text"],
                            ["endereco", "brasil", "nrLograd", "_text"],
                            ["trabalhador", "endereco", "nrLograd", "_text"],
                            ["endereco", "nrLograd", "_text"],
                            ["nrLograd", "_text"],
                            ["trabalhador", "endereco", "numero", "_text"],
                            ["endereco", "numero", "_text"],
                            ["numero", "_text"]
                        ],
                        "tipo": "string", "valor_padrao": ""
                    },
                    "36 AJ-Complemento do endereço de trabalhador": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "endereco", "brasil", "complemento", "_text"], "tipo": "string"},
                    "37 AK-CEP do trabalhador": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "endereco", "brasil", "cep", "_text"], "tipo": "string"},
                    "38 AL-Bairro do trabalhador": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "endereco", "brasil", "bairro", "_text"], "tipo": "string"},
                    "39 AM-Código da cidade de residência do trabalhador": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "endereco", "brasil", "codMunic", "_text"], "tipo": "string"},
                    "41 AO-UF de residência": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "endereco", "brasil", "uf", "_text"], "tipo": "string"},
                    "43 AQ-Telefone": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "contato", "fonePrinc", "_text"], "tipo": "string"},
                    "45 AS-Email": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "contato", "emailPrinc", "_text"], "tipo": "string"},
                    "78 BZ-Número da CTPS": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "documentos", "ctps", "nrCtps", "_text"], "tipo": "string"},
                    "79 CA-Série da CTPS": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "documentos", "ctps", "serieCtps", "_text"], "tipo": "string"},
                    "80 CB-UF da CTPS": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "documentos", "ctps", "ufCtps", "_text"], "tipo": "string"},
                    "56 BD-Número do RG": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "documentos", "rg", "nrRg", "_text"], "tipo": "string"},
                    "57 BE-Órgão emissor do RG": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "documentos", "rg", "orgaoEmissor", "_text"], "tipo": "string"},
                    "58 BF-Data de emissão do RG": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "documentos", "rg", "dtExped", "_text"], "tipo": "data", "formato": "YYYY-MM-DD"},
                    "24 X-UF da cidade de nascimento": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "nascimento", "uf", "_text"], "tipo": "string"},
                    "25 Y-Código do país de nascimento": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "nascimento", "paisNascto", "_text"], "tipo": "string"},
                    "27 AA-Código de país de nacionalidade": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "nascimento", "paisNac", "_text"], "tipo": "string"},
                    "111 DG-País de residência no exterior": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "endereco", "exterior", "paisResid", "_text"], "tipo": "string"},
                    "112 DH-Bairro de residência no exterior": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "endereco", "exterior", "bairro", "_text"], "tipo": "string"},
                    "113 DI-Endereço de residência no exterior": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "endereco", "exterior", "dscLograd", "_text"], "tipo": "string"},
                    "114 DJ-Número de residência no exterior": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "endereco", "exterior", "nrLograd", "_text"], "tipo": "string"},
                    "115 DK-Complemento no endereço de residência no exterior": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "endereco", "exterior", "complemento", "_text"], "tipo": "string"},
                    "116 DL-Cidade de residência no exterior": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "endereco", "exterior", "nmCid", "_text"], "tipo": "string"},
                    "118 DN-CEP de residência no exterior": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "endereco", "exterior", "codPostal", "_text"], "tipo": "string"},
                    "14 N-Indicativo de deficiência": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "infoDeficiencia", "defFisica", "_text"], "tipo": "string"},
                    "15 O-Indicativo de deficiência física": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "infoDeficiencia", "defFisica", "_text"], "tipo": "string"},
                    "16 P-Indicativo de deficiência visual": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "infoDeficiencia", "defVisual", "_text"], "tipo": "string"},
                    "17 Q-Indicativo de deficiência auditiva": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "infoDeficiencia", "defAuditiva", "_text"], "tipo": "string"},
                    "18 R-Indicativo de deficiência mental": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "infoDeficiencia", "defMental", "_text"], "tipo": "string"},
                    "19 S-Indicativo de deficiência intelectual": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "infoDeficiencia", "defIntelectual", "_text"], "tipo": "string"},
                    "20 T-Trabalhador reabilitado ou adaptado": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "infoDeficiencia", "reabReadap", "_text"], "tipo": "string"},
                    "21 U-Trabalhador faz parte de cota de deficiente": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "infoDeficiencia", "infoCota", "_text"], "tipo": "string"},
                    "103 CY-Observações sobre a situação militar": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "infoDeficiencia", "observacao", "_text"], "tipo": "string"},
                    "89 CK-Número da CNH": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "documentos", "cnh", "nrRegCnh", "_text"], "tipo": "string"},
                    "90 CL-Categoria da CNH": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "documentos", "cnh", "categoriaCnh", "_text"], "tipo": "string"},
                    "91 CM-UF da CNH": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "documentos", "cnh", "ufCnh", "_text"], "tipo": "string"},
                    "92 CN-Data de emissão da CNH": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "documentos", "cnh", "dtExped", "_text"], "tipo": "string"},
                    "93 CO-Data de emissão da primeira CNH": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "documentos", "cnh", "dtPriHab", "_text"], "tipo": "string"},
                    "94 CP-Data de validade da CNH": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "documentos", "cnh", "dtValid", "_text"], "tipo": "string"},
                    "60 BH-Número do RNE": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "documentos", "rne", "nrRne", "_text"], "tipo": "string"},
                    "61 BI-Órgão emissor do RNE": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "documentos", "rne", "orgaoEmissor", "_text"], "tipo": "string"},
                    "63 BK-Data de emissão do RNE": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "documentos", "rne", "dtExped", "_text"], "tipo": "data", "formato": "YYYY-MM-DD"},
                    "64 BL-Data da chegada no país": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "trabEstrangeiro", "dtChegada", "_text"], "tipo": "data", "formato": "YYYY-MM-DD"},
                    "65 BM-Classificação estrangeiro": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "trabEstrangeiro", "classTrabEstrang", "_text"], "tipo": "string"},
                    "66 BN-Estrangeiro casado com brasileiro": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "trabEstrangeiro", "casadoBr", "_text"], "tipo": "string"},
                    "67 BO-Estrangeiro com filhos brasileiros": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "trabEstrangeiro", "filhosBr", "_text"], "tipo": "string"},
                    # --- INÍCIO CAMPOS EXPANDIDOS S-2200 ---
                    "cpf_trabalhador": {"origem": "cpf_trabalhador", "tipo": "string"},
                    "nis_trabalhador": {"origem": "nis_trabalhador", "tipo": "string"},
                    "nome_trabalhador": {"origem": "nome_trabalhador", "tipo": "string"},
                    "sexo": {"origem": "sexo", "tipo": "string"},
                    "raca_cor": {"origem": "raca_cor", "tipo": "string"},
                    "estado_civil": {"origem": "estado_civil", "tipo": "string"},
                    "grau_instrucao": {"origem": "grau_instrucao", "tipo": "string"},
                    "data_nascimento": {"origem": "data_nascimento", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "nm_mae": {"origem": "nm_mae", "tipo": "string"},
                    "nm_pai": {"origem": "nm_pai", "tipo": "string"},
                    "uf_nasc": {"origem": "uf_nasc", "tipo": "string"},
                    "pais_nasc": {"origem": "pais_nasc", "tipo": "string"},
                    "pais_nac": {"origem": "pais_nac", "tipo": "string"},
                    "tp_lograd": {"origem": "tp_lograd", "tipo": "string"},
                    "dsc_lograd": {"origem": "dsc_lograd", "tipo": "string"},
                    "nr_lograd": {"origem": "nr_lograd", "tipo": "string"},
                    "complemento": {"origem": "complemento", "tipo": "string"},
                    "cep": {"origem": "cep", "tipo": "string"},
                    "bairro": {"origem": "bairro", "tipo": "string"},
                    "cod_munic": {"origem": "cod_munic", "tipo": "string"},
                    "nm_cidade": {"origem": "nm_cidade", "tipo": "string"},
                    "uf_resid": {"origem": "uf_resid", "tipo": "string"},
                    "pais_resid": {"origem": "pais_resid", "tipo": "string"},
                    "bairro_ext": {"origem": "bairro_ext", "tipo": "string"},
                    "dsc_lograd_ext": {"origem": "dsc_lograd_ext", "tipo": "string"},
                    "nr_lograd_ext": {"origem": "nr_lograd_ext", "tipo": "string"},
                    "complemento_ext": {"origem": "complemento_ext", "tipo": "string"},
                    "nm_cidade_ext": {"origem": "nm_cidade_ext", "tipo": "string"},
                    "cod_postal_ext": {"origem": "cod_postal_ext", "tipo": "string"},
                    "fone_princ": {"origem": "fone_princ", "tipo": "string"},
                    "fone_alt": {"origem": "fone_alt", "tipo": "string"},
                    "email_princ": {"origem": "email_princ", "tipo": "string"},
                    "email_alt": {"origem": "email_alt", "tipo": "string"},
                    "contato_emerg": {"origem": "contato_emerg", "tipo": "string"},
                    "fone_emerg": {"origem": "fone_emerg", "tipo": "string"},
                    "parentesco_emerg": {"origem": "parentesco_emerg", "tipo": "string"},
                    "ctps_numero": {"origem": "ctps_numero", "tipo": "string"},
                    "ctps_serie": {"origem": "ctps_serie", "tipo": "string"},
                    "ctps_uf": {"origem": "ctps_uf", "tipo": "string"},
                    "rg_numero": {"origem": "rg_numero", "tipo": "string"},
                    "rg_orgao": {"origem": "rg_orgao", "tipo": "string"},
                    "rg_data": {"origem": "rg_data", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "rg_uf": {"origem": "rg_uf", "tipo": "string"},
                    "rne_numero": {"origem": "rne_numero", "tipo": "string"},
                    "rne_orgao": {"origem": "rne_orgao", "tipo": "string"},
                    "rne_uf": {"origem": "rne_uf", "tipo": "string"},
                    "cnh_numero": {"origem": "cnh_numero", "tipo": "string"},
                    "cnh_categoria": {"origem": "cnh_categoria", "tipo": "string"},
                    "cnh_uf": {"origem": "cnh_uf", "tipo": "string"},
                    "cnh_data": {"origem": "cnh_data", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "cnh_pri_hab": {"origem": "cnh_pri_hab", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "cnh_validade": {"origem": "cnh_validade", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "def_fisica": {"origem": "def_fisica", "tipo": "string"},
                    "def_visual": {"origem": "def_visual", "tipo": "string"},
                    "def_auditiva": {"origem": "def_auditiva", "tipo": "string"},
                    "def_mental": {"origem": "def_mental", "tipo": "string"},
                    "def_intelectual": {"origem": "def_intelectual", "tipo": "string"},
                    "reab_readap": {"origem": "reab_readap", "tipo": "string"},
                    "info_cota": {"origem": "info_cota", "tipo": "string"},
                    "observacao_def": {"origem": "observacao_def", "tipo": "string"},
                    "dt_chegada": {"origem": "dt_chegada", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "class_estrangeiro": {"origem": "class_estrangeiro", "tipo": "string"},
                    "casado_br": {"origem": "casado_br", "tipo": "string"},
                    "filhos_br": {"origem": "filhos_br", "tipo": "string"},
                    "matricula": {"origem": "matricula", "tipo": "string"},
                    "data_admissao": {"origem": "data_admissao", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "tipo_admissao": {"origem": "tipo_admissao", "tipo": "string"},
                    "tipo_regime_jornada": {"origem": "tipo_regime_jornada", "tipo": "string"},
                    "natureza_atividade": {"origem": "natureza_atividade", "tipo": "string"},
                    "cnpj_empregador": {"origem": "cnpj_empregador", "tipo": "string"},
                    "cod_categoria": {"origem": "cod_categoria", "tipo": "string"},
                    "cod_cargo": {"origem": "cod_cargo", "tipo": "string"},
                    "cod_funcao": {"origem": "cod_funcao", "tipo": "string"},
                    "cod_lotacao": {"origem": "cod_lotacao", "tipo": "string"},
                    "salario_contratual": {"origem": "salario_contratual", "tipo": "decimal"},
                    "und_sal_fixo": {"origem": "und_sal_fixo", "tipo": "string"},
                    "tipo_contrato": {"origem": "tipo_contrato", "tipo": "string"},
                    "duracao_contrato": {"origem": "duracao_contrato", "tipo": "string"},
                    "passaporte_numero": {"origem": "passaporte_numero", "tipo": "string"},
                    "passaporte_pais_origem": {"origem": "passaporte_pais_origem", "tipo": "string"},
                    "passaporte_data_emissao": {"origem": "passaporte_data_emissao", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "passaporte_validade": {"origem": "passaporte_validade", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "ric_numero": {"origem": "ric_numero", "tipo": "string"},
                    "ric_orgao": {"origem": "ric_orgao", "tipo": "string"},
                    "ric_uf": {"origem": "ric_uf", "tipo": "string"},
                    "ric_data_emissao": {"origem": "ric_data_emissao", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "pis_numero": {"origem": "pis_numero", "tipo": "string"},
                    "pis_data_emissao": {"origem": "pis_data_emissao", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "titulo_eleitor_numero": {"origem": "titulo_eleitor_numero", "tipo": "string"},
                    "titulo_eleitor_zona": {"origem": "titulo_eleitor_zona", "tipo": "string"},
                    "titulo_eleitor_secao": {"origem": "titulo_eleitor_secao", "tipo": "string"},
                    "titulo_eleitor_cod_munic": {"origem": "titulo_eleitor_cod_munic", "tipo": "string"},
                    "titulo_eleitor_nm_cidade": {"origem": "titulo_eleitor_nm_cidade", "tipo": "string"},
                    "titulo_eleitor_uf": {"origem": "titulo_eleitor_uf", "tipo": "string"},
                    "titulo_eleitor_data_emissao": {"origem": "titulo_eleitor_data_emissao", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "cert_militar_numero": {"origem": "cert_militar_numero", "tipo": "string"},
                    "cert_militar_data_exped": {"origem": "cert_militar_data_exped", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "cert_militar_regiao": {"origem": "cert_militar_regiao", "tipo": "string"},
                    "cert_militar_tipo": {"origem": "cert_militar_tipo", "tipo": "string"},
                    "cert_militar_numero2": {"origem": "cert_militar_numero2", "tipo": "string"},
                    "cert_militar_serie": {"origem": "cert_militar_serie", "tipo": "string"},
                    "cert_militar_data_exped2": {"origem": "cert_militar_data_exped2", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "cert_militar_categoria": {"origem": "cert_militar_categoria", "tipo": "string"},
                    "cert_militar_observacoes": {"origem": "cert_militar_observacoes", "tipo": "string"},
                    "profissao": {"origem": "profissao", "tipo": "string"},
                    "conselho_numero": {"origem": "conselho_numero", "tipo": "string"},
                    "conselho_orgao": {"origem": "conselho_orgao", "tipo": "string"},
                    "conselho_uf": {"origem": "conselho_uf", "tipo": "string"},
                    "conselho_data_emissao": {"origem": "conselho_data_emissao", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "conselho_data_validade": {"origem": "conselho_data_validade", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "conselho_observacoes": {"origem": "conselho_observacoes", "tipo": "string"},
                    "banco_forma_pagamento": {"origem": "banco_forma_pagamento", "tipo": "string"},
                    "banco_codigo": {"origem": "banco_codigo", "tipo": "string"},
                    "banco_agencia": {"origem": "banco_agencia", "tipo": "string"},
                    "banco_agencia_dv": {"origem": "banco_agencia_dv", "tipo": "string"},
                    "banco_conta": {"origem": "banco_conta", "tipo": "string"},
                    "banco_conta_dv": {"origem": "banco_conta_dv", "tipo": "string"},
                    "banco_tipo_conta": {"origem": "banco_tipo_conta", "tipo": "string"},
                    "banco_tipo_operacao": {"origem": "banco_tipo_operacao", "tipo": "string"},
                    "peso": {"origem": "peso", "tipo": "string"},
                    "altura": {"origem": "altura", "tipo": "string"},
                    "tamanho_calca": {"origem": "tamanho_calca", "tipo": "string"},
                    "tamanho_camisa": {"origem": "tamanho_camisa", "tipo": "string"},
                    "tamanho_calcado": {"origem": "tamanho_calcado", "tipo": "string"},
                    "cns_numero": {"origem": "cns_numero", "tipo": "string"},
                    "observacoes_gerais": {"origem": "observacoes_gerais", "tipo": "string"},
                    # --- FIM CAMPOS EXPANDIDOS S-2200 ---
                }
            },
            
            "02_CONVCONTRATO": {
                "fonte_principal": "esocial_s2200",
                "fontes_adicionais": ["esocial_s2205", "esocial_s2206"],
                "campos": {
                    # --- CAMPOS PRINCIPAIS MAPEADOS DIRETAMENTE DO BANCO ---
                    "1 A-ID do empregador": {"origem": "cnpj_empregador", "tipo": "string"},
                    "2 B-Código referência": {"origem": "cnpj_empregador", "tipo": "string"},
                    "3 C-CPF trabalhador": {"origem": "cpf_trabalhador", "tipo": "string"},
                    "4 D-Nome trabalhador": {"origem": "nome_trabalhador", "tipo": "string"},
                    "5 E-Data nascimento trabalhador": {"origem": "data_nascimento", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "6 F-Apelido trabalhador": {"origem": "nome_social", "tipo": "string"},
                    "7 G-Nome social trabalhador": {"origem": "nome_social", "tipo": "string"},
                    "8 H-Nome mae trabalhador": {"origem": "nm_mae", "tipo": "string"},
                    "9 I-Nome pai trabalhador": {"origem": "nm_pai", "tipo": "string"},
                    "10 J-Sexo trabalhador": {"origem": "sexo", "tipo": "string"},
                    "11 K-Grau de instrução": {"origem": "grau_instrucao", "tipo": "string"},
                    "12 L-Raça/Cor do trabalhador": {"origem": "raca_cor", "tipo": "string"},
                    "13 M-Estado civil do trabalhador": {"origem": "estado_civil", "tipo": "string"},
                    "14 N-Indicativo de deficiência": {"origem": "def_fisica", "tipo": "string"},
                    "15 O-Indicativo de deficiência física": {"origem": "def_fisica", "tipo": "string"},
                    "16 P-Indicativo de deficiência visual": {"origem": "def_visual", "tipo": "string"},
                    "17 Q-Indicativo de deficiência auditiva": {"origem": "def_auditiva", "tipo": "string"},
                    "18 R-Indicativo de deficiência mental": {"origem": "def_mental", "tipo": "string"},
                    "19 S-Indicativo de deficiência intelectual": {"origem": "def_intelectual", "tipo": "string"},
                    "20 T-Trabalhador reabilitado ou adaptado": {"origem": "reab_readap", "tipo": "string"},
                    "21 U-Trabalhador faz parte de cota de deficiente": {"origem": "info_cota", "tipo": "string"},
                    "22 V-Tipo sanguíneo": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "tipoSangue", "_text"], "tipo": "string"},
                    "23 W-Nome da cidade de  nascimento": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "nascimento", "nmCid", "_text"], "tipo": "string"},
                    "24 X-UF da cidade de nascimento": {"origem": "uf_nasc", "tipo": "string"},
                    "25 Y-Código do país de nascimento": {"origem": "pais_nasc", "tipo": "string"},
                    "26 Z-Nome do país de nascimento": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "nascimento", "paisNascto", "_text"], "tipo": "string"},
                    "27 AA-Código de país de nacionalidade": {"origem": "pais_nac", "tipo": "string"},
                    "28 AB-Nome do país denacionalidade": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "nascimento", "paisNac", "_text"], "tipo": "string"},
                    "29 AC-Código RAIS do país": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "nascimento", "codRais", "_text"], "tipo": "string"},
                    "30 AD-É aposentado": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "aposentado", "_text"], "tipo": "string"},
                    "31 AE-Data de aposentaria": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "dtAposent", "_text"], "tipo": "data", "formato": "YYYY-MM-DD"},
                    "32 AF-Reside no país": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "residePais", "_text"], "tipo": "string"},
                    "33 AG-Código do tipo de logradouro": {"origem": "tp_lograd", "tipo": "string"},
                    "34 AH-Endereço do trabalhador": {"origem": "dsc_lograd", "tipo": "string"},
                    "35 AI-Número de endereço do trabalhador": {"origem": "nr_lograd", "tipo": "string"},
                    "36 AJ-Complemento do endereço de trabalhador": {"origem": "complemento", "tipo": "string"},
                    "37 AK-CEP do trabalhador": {"origem": "cep", "tipo": "string"},
                    "38 AL-Bairro do trabalhador": {"origem": "bairro", "tipo": "string"},
                    "39 AM-Código da cidade de residência do trabalhador": {"origem": "cod_munic", "tipo": "string"},
                    "40 NA-Nome da cidade de residência do trabalhador": {"origem": "nm_cidade", "tipo": "string"},
                    "41 AO-UF de residência": {"origem": "uf_resid", "tipo": "string"},
                    "42 AP-Referência do endereço do trabalhador": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "endereco", "brasil", "referencia", "_text"], "tipo": "string"},
                    "43 AQ-Telefone": {"origem": "fone_princ", "tipo": "string"},
                    "44 AR-Telefone 2": {"origem": "fone_alt", "tipo": "string"},
                    "45 AS-Email": {"origem": "email_princ", "tipo": "string"},
                    "46 AT-Email alternativo": {"origem": "email_alt", "tipo": "string"},
                    "47 AU-Contato de emergência": {"origem": "contato_emerg", "tipo": "string"},
                    "48 AV-Telefone do contato de emergência": {"origem": "fone_emerg", "tipo": "string"},
                    "49 AW-Parentesco do contato para emergência": {"origem": "parentesco_emerg", "tipo": "string"},
                    "50 AX-Peso": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "peso", "_text"], "tipo": "string"},
                    "51 AY-Altura": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "altura", "_text"], "tipo": "string"},
                    "52 AZ-Calça": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "tamanhoCalca", "_text"], "tipo": "string"},
                    "53 BA-Camisa": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "tamanhoCamisa", "_text"], "tipo": "string"},
                    "54 BB-Calçado": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "tamanhoCalcado", "_text"], "tipo": "string"},
                    "55 BC-Número do CNS": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "documentos", "cns", "nrCns", "_text"], "tipo": "string"},
                    "56 BD-Número do RG": {"origem": "nr_rg", "tipo": "string"},
                    "57 BE-Órgão emissor do RG": {"origem": "orgao_emissor_rg", "tipo": "string"},
                    "58 BF-Data de emissão do RG": {"origem": "dt_exped_rg", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "59 BG-UF de emissão do RG": {"origem": "uf_rg", "tipo": "string"},
                    "60 BH-Número do RNE": {"origem": "nr_rne", "tipo": "string"},
                    "61 BI-Órgão emissor do RNE": {"origem": "orgao_emissor_rne", "tipo": "string"},
                    "62 BJ-UF de emissão do RNE": {"origem": "uf_rne", "tipo": "string"},
                    "63 BK-Data de emissão do RNE": {"origem": "dt_exped_rne", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "64 BL-Data da chegada no país": {"origem": "dt_chegada", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "65 BM-Classificação estrangeiro": {"origem": "class_trab_estrang", "tipo": "string"},
                    "66 BN-Estrangeiro casado com brasileiro": {"origem": "casado_br", "tipo": "string"},
                    "67 BO-Estrangeiro com filhos brasileiros": {"origem": "filhos_br", "tipo": "string"},
                    "68 BP-Número do passaporte": {"origem": "nr_passaporte", "tipo": "string"},
                    "69 BQ-País de origem do passaporte": {"origem": "pais_origem_passaporte", "tipo": "string"},
                    "70 BR-Data de emissão do passaporte": {"origem": "dt_exped_passaporte", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "71 BS-Data de validade do passaporte": {"origem": "dt_valid_passaporte", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "72 BT-Número do RIC": {"origem": "nr_ric", "tipo": "string"},
                    "73 BU-Órgão emissor do RIC": {"origem": "orgao_emissor_ric", "tipo": "string"},
                    "74 BV-UF de emissão do RIC": {"origem": "uf_ric", "tipo": "string"},
                    "75 BW-Data de emissão do RIC": {"origem": "dt_exped_ric", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "76 BXPIS": {"origem": "nis_trabalhador", "tipo": "string"},
                    "77 BY-Data de emissão do PIS": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "documentos", "pis", "dtExped", "_text"], "tipo": "data", "formato": "YYYY-MM-DD"},
                    "78 BZ-Número da CTPS": {"origem": "nr_ctps", "tipo": "string"},
                    "79 CA-Série da CTPS": {"origem": "serie_ctps", "tipo": "string"},
                    "80 CB-UF da CTPS": {"origem": "uf_ctps", "tipo": "string"},
                    "81 CC-Data de emissão da CTPS": {"origem": "dt_exped_ctps", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "82 CD-Número do título de eleitor": {"origem": "nr_titulo", "tipo": "string"},
                    "83 CE-Zona do título de eleitor": {"origem": "zona_titulo", "tipo": "string"},
                    "84 CF-Seção do título de eleitor": {"origem": "secao_titulo", "tipo": "string"},
                    "85 CG-Código da cidade do título de eleitor": {"origem": "cod_munic_titulo", "tipo": "string"},
                    "86 CH-Nome da cidade do título de eleitor": {"origem": "nm_cidade_titulo", "tipo": "string"},
                    "87 CI-UF do título de eleitor": {"origem": "uf_titulo", "tipo": "string"},
                    "88 CJ-Data de emissão do título de eleitor": {"origem": "dt_exped_titulo", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "89 CK-Número da CNH": {"origem": "nr_reg_cnh", "tipo": "string"},
                    "90 CL-Categoria da CNH": {"origem": "categoria_cnh", "tipo": "string"},
                    "91 CM-UF da CNH": {"origem": "uf_cnh", "tipo": "string"},
                    "92 CN-Data de emissão da CNH": {"origem": "dt_exped_cnh", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "93 CO-Data de emissão da primeira CNH": {"origem": "dt_pri_hab", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "94 CP-Data de validade da CNH": {"origem": "dt_valid_cnh", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "95 CQ-Número do certificado de alistamento militar": {"origem": "nr_certidao", "tipo": "string"},
                    "96 CR-Data de expedição da CAM": {"origem": "dt_exped_certidao", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "97 CS-Região militar": {"origem": "regiao_militar", "tipo": "string"},
                    "98 CT-Tipo de certificado militar": {"origem": "tipo_certidao", "tipo": "string"},
                    "99 CU-Número do certificado militar": {"origem": "nr_certidao2", "tipo": "string"},
                    "100 CV-Número de série do certificado militar": {"origem": "nr_serie", "tipo": "string"},
                    "101 CW-Data de expedição do certificado militar": {"origem": "dt_exped_certidao2", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "102 CX-Categoria do certificado militar": {"origem": "categoria_certidao", "tipo": "string"},
                    "103 CY-Observações sobre a situação militar": {"origem": "observacao_def", "tipo": "string"},
                    "104 CZ-Profissão": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "profissao", "_text"], "tipo": "string"},
                    "105 DA-Número de registro no conselho de classe": {"origem": "nr_registro_conselho", "tipo": "string"},
                    "106 DB-Órgão emissor do registro de classe": {"origem": "orgao_emissor_conselho", "tipo": "string"},
                    "107 DC-UF do conselho de classe": {"origem": "uf_conselho", "tipo": "string"},
                    "108 DD-Data de emissão do registro no conselho": {"origem": "dt_exped_conselho", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "109 DE-Data de vencimento do registro no conselho": {"origem": "dt_validade_conselho", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "110 DF-Observações gerais": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "observacoes", "_text"], "tipo": "string"},
                    "111 DG-País de residência no exterior": {"origem": "pais_resid", "tipo": "string"},
                    "112 DH-Bairro de residência no exterior": {"origem": "bairro_ext", "tipo": "string"},
                    "113 DI-Endereço de residência no exterior": {"origem": "dsc_lograd_ext", "tipo": "string"},
                    "114 DJ-Número de residência no exterior": {"origem": "nr_lograd_ext", "tipo": "string"},
                    "115 DK-Complemento no endereço de residência no exterior": {"origem": "complemento_ext", "tipo": "string"},
                    "116 DL-Cidade de residência no exterior": {"origem": "nm_cidade_ext", "tipo": "string"},
                    "117 DM-UF de residência no exterior": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "endereco", "exterior", "uf", "_text"], "tipo": "string"},
                    "118 DN-CEP de residência no exterior": {"origem": "cod_postal_ext", "tipo": "string"},
                    "119 DO-Cadastrado em": {"origem": "data_importacao", "tipo": "datetime", "formato": "YYYY-MM-DDTHH:mm:ss"},
                    "120 DP-Categoria": {"origem": "cod_categoria", "tipo": "string"},
                    "121 DQ-Data de desligamento": {"origem": "dt_deslig", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "122 DR-Tipo pessoa origem": {"origem": "json_data", "caminho_json": ["evtAdmissao", "vinculo", "sucessaoVinc", "origem", "_text"], "tipo": "string"},
                    "123 DS-Tipo pessoa destino": {"origem": "json_data", "caminho_json": ["evtAdmissao", "vinculo", "sucessaoVinc", "destino", "_text"], "tipo": "string"},
                    "124 DT-Início de validade": {"origem": "dt_adm", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "125 DU-Forma de pagamento": {"origem": "json_data", "caminho_json": ["evtAdmissao", "vinculo", "infoContrato", "localTrab", "infoLocalTrab", "endereco", "brasil", "formaPagamento", "_text"], "tipo": "string"},
                    "126 DV-Código do banco para pagamento pessoa": {"origem": "json_data", "caminho_json": ["evtAdmissao", "vinculo", "infoContrato", "localTrab", "infoLocalTrab", "endereco", "brasil", "banco", "codBanco", "_text"], "tipo": "string"},
                    "127 DW-Agência sem dígito": {"origem": "json_data", "caminho_json": ["evtAdmissao", "vinculo", "infoContrato", "localTrab", "infoLocalTrab", "endereco", "brasil", "banco", "nrAgencia", "_text"], "tipo": "string"},
                    "128 DX-Dígito da agência": {"origem": "json_data", "caminho_json": ["evtAdmissao", "vinculo", "infoContrato", "localTrab", "infoLocalTrab", "endereco", "brasil", "banco", "dvAgencia", "_text"], "tipo": "string"},
                    "129 DY-Conta bancária sem dígito": {"origem": "json_data", "caminho_json": ["evtAdmissao", "vinculo", "infoContrato", "localTrab", "infoLocalTrab", "endereco", "brasil", "banco", "nrConta", "_text"], "tipo": "string"},
                    "130 DZ-Dígito da conta": {"origem": "json_data", "caminho_json": ["evtAdmissao", "vinculo", "infoContrato", "localTrab", "infoLocalTrab", "endereco", "brasil", "banco", "dvConta", "_text"], "tipo": "string"},
                    "131 EA-Tipo de conta": {"origem": "json_data", "caminho_json": ["evtAdmissao", "vinculo", "infoContrato", "localTrab", "infoLocalTrab", "endereco", "brasil", "banco", "tpConta", "_text"], "tipo": "string"},
                    "132 EB-Tipo de operação": {"origem": "json_data", "caminho_json": ["evtAdmissao", "vinculo", "infoContrato", "localTrab", "infoLocalTrab", "endereco", "brasil", "banco", "tpOperacao", "_text"], "tipo": "string"},
                    "2 B-Código referência": {
                        "origem": "cnpj_empregador",
                        "caminho_json_alternativos": [
                            ["evtAdmissao", "ideEmpregador", "nrInsc", "_text"],
                            ["evtAltCadastral", "ideEmpregador", "nrInsc", "_text"]
                        ],
                        "tipo": "string", "obrigatorio": True, "valor_padrao": ""
                    },
                    "3 C-CPF trabalhador": {
                        "origem": "json_data",
                        "caminho_json": ["evtAdmissao", "trabalhador", "cpfTrab", "_text"],
                        "caminho_json_alternativos": [
                            ["trabalhador", "cpfTrab", "_text"],
                            ["trabalhador", "cpf", "_text"],
                            ["evtAltCadastral", "ideTrabalhador", "cpfTrab", "_text"],
                            ["ideTrabalhador", "cpfTrab", "_text"],
                            ["ideTrabalhador", "cpf", "_text"],
                            ["cpfTrab", "_text"],
                            ["cpf", "_text"]
                        ],
                        "tipo": "string", "obrigatorio": True, "valor_padrao": ""
                    },
                    "4 D-Nome trabalhador": {
                        "origem": "json_data",
                        "caminho_json": ["evtAdmissao", "trabalhador", "nmTrab", "_text"],
                        "caminho_json_alternativos": [
                            ["trabalhador", "nmTrab", "_text"],
                            ["trabalhador", "nome", "_text"],
                            ["evtAltCadastral", "alteracao", "dadosTrabalhador", "nmTrab", "_text"],
                            ["alteracao", "dadosTrabalhador", "nmTrab", "_text"],
                            ["evtAltContratual", "ideTrabalhador", "nmTrab", "_text"],
                            ["ideTrabalhador", "nmTrab", "_text"],
                            ["nome", "_text"]
                        ],
                        "tipo": "string", "obrigatorio": True, "valor_padrao": ""
                    },
                    "5 E-Data nascimento trabalhador": {
                        "origem": "json_data",
                        "caminho_json": ["evtAdmissao", "trabalhador", "nascimento", "dtNascto", "_text"],
                        "caminho_json_alternativos": [
                            ["trabalhador", "nascimento", "dtNascto", "_text"],
                            ["trabalhador", "dtNascto", "_text"],
                            ["nascimento", "dtNascto", "_text"],
                            ["dtNascto", "_text"],
                            ["trabalhador", "dataNascimento", "_text"],
                            ["dataNascimento", "_text"]
                        ],
                        "tipo": "data", "formato": "YYYY-MM-DD", "valor_padrao": ""
                    },
                    "6 F-Apelido trabalhador": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "nmSoc", "_text"], "tipo": "string"},
                    "7 G-Nome social trabalhador": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "nmSoc", "_text"], "tipo": "string"},
                    "8 H-Nome mae trabalhador": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "nascimento", "nmMae", "_text"], "tipo": "string"},
                    "9 I-Nome pai trabalhador": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "nascimento", "nmPai", "_text"], "tipo": "string"},
                    "10 J-Sexo trabalhador": {"origem": "sexo", "tipo": "string", "valores_validos": ["M", "F"]},
                    "11 K-Grau de instrução": {"origem": "grau_instrucao", "tipo": "string"},
                    "12 L-Raça/Cor do trabalhador": {"origem": "raca_cor", "tipo": "string"},
                    "Solteiro3 M-Estado civil do trabalhador": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "estCiv", "_text"], "tipo": "string"},
                    "76 BXPIS": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "nisTrab", "_text"], "tipo": "string"},
                    "119 DO-Cadastrado em": {"origem": "data_importacao", "tipo": "datetime", "formato": "YYYY-MM-DDTHH:mm:ss"},
                    "120 DP-Categoria": {"origem": "json_data", "caminho_json": ["evtAdmissao", "vinculo", "infoContrato", "codCateg", "_text"], "tipo": "string"},
                    "124 DT-Início de validade": {"origem": "json_data", "caminho_json": ["evtAdmissao", "vinculo", "infoRegimeTrab", "infoCeletista", "dtAdm", "_text"], "tipo": "data", "formato": "YYYY-MM-DD"},
                    "33 AG-Código do tipo de logradouro": {
                        "origem": "json_data",
                        "caminho_json": ["evtAdmissao", "trabalhador", "endereco", "brasil", "tpLograd", "_text"],
                        "caminho_json_alternativos": [
                            ["trabalhador", "endereco", "brasil", "tpLograd", "_text"],
                            ["endereco", "brasil", "tpLograd", "_text"],
                            ["trabalhador", "endereco", "tpLograd", "_text"],
                            ["endereco", "tpLograd", "_text"],
                            ["tpLograd", "_text"]
                        ],
                        "tipo": "string", "valor_padrao": ""
                    },
                    "34 AH-Endereço do trabalhador": {
                        "origem": "json_data",
                        "caminho_json": ["evtAdmissao", "trabalhador", "endereco", "brasil", "dscLograd", "_text"],
                        "caminho_json_alternativos": [
                            ["trabalhador", "endereco", "brasil", "dscLograd", "_text"],
                            ["endereco", "brasil", "dscLograd", "_text"],
                            ["trabalhador", "endereco", "dscLograd", "_text"],
                            ["endereco", "dscLograd", "_text"],
                            ["dscLograd", "_text"],
                            ["trabalhador", "endereco", "logradouro", "_text"],
                            ["endereco", "logradouro", "_text"],
                            ["logradouro", "_text"]
                        ],
                        "tipo": "string", "valor_padrao": ""
                    },
                    "35 AI-Número de endereço do trabalhador": {
                        "origem": "json_data",
                        "caminho_json": ["evtAdmissao", "trabalhador", "endereco", "brasil", "nrLograd", "_text"],
                        "caminho_json_alternativos": [
                            ["trabalhador", "endereco", "brasil", "nrLograd", "_text"],
                            ["endereco", "brasil", "nrLograd", "_text"],
                            ["trabalhador", "endereco", "nrLograd", "_text"],
                            ["endereco", "nrLograd", "_text"],
                            ["nrLograd", "_text"],
                            ["trabalhador", "endereco", "numero", "_text"],
                            ["endereco", "numero", "_text"],
                            ["numero", "_text"]
                        ],
                        "tipo": "string", "valor_padrao": ""
                    },
                    "36 AJ-Complemento do endereço de trabalhador": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "endereco", "brasil", "complemento", "_text"], "tipo": "string"},
                    "37 AK-CEP do trabalhador": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "endereco", "brasil", "cep", "_text"], "tipo": "string"},
                    "38 AL-Bairro do trabalhador": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "endereco", "brasil", "bairro", "_text"], "tipo": "string"},
                    "39 AM-Código da cidade de residência do trabalhador": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "endereco", "brasil", "codMunic", "_text"], "tipo": "string"},
                    "41 AO-UF de residência": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "endereco", "brasil", "uf", "_text"], "tipo": "string"},
                    "43 AQ-Telefone": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "contato", "fonePrinc", "_text"], "tipo": "string"},
                    "45 AS-Email": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "contato", "emailPrinc", "_text"], "tipo": "string"},
                    "78 BZ-Número da CTPS": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "documentos", "ctps", "nrCtps", "_text"], "tipo": "string"},
                    "79 CA-Série da CTPS": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "documentos", "ctps", "serieCtps", "_text"], "tipo": "string"},
                    "80 CB-UF da CTPS": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "documentos", "ctps", "ufCtps", "_text"], "tipo": "string"},
                    "56 BD-Número do RG": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "documentos", "rg", "nrRg", "_text"], "tipo": "string"},
                    "57 BE-Órgão emissor do RG": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "documentos", "rg", "orgaoEmissor", "_text"], "tipo": "string"},
                    "58 BF-Data de emissão do RG": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "documentos", "rg", "dtExped", "_text"], "tipo": "data", "formato": "YYYY-MM-DD"},
                    "24 X-UF da cidade de nascimento": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "nascimento", "uf", "_text"], "tipo": "string"},
                    "25 Y-Código do país de nascimento": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "nascimento", "paisNascto", "_text"], "tipo": "string"},
                    "27 AA-Código de país de nacionalidade": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "nascimento", "paisNac", "_text"], "tipo": "string"},
                    "111 DG-País de residência no exterior": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "endereco", "exterior", "paisResid", "_text"], "tipo": "string"},
                    "112 DH-Bairro de residência no exterior": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "endereco", "exterior", "bairro", "_text"], "tipo": "string"},
                    "113 DI-Endereço de residência no exterior": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "endereco", "exterior", "dscLograd", "_text"], "tipo": "string"},
                    "114 DJ-Número de residência no exterior": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "endereco", "exterior", "nrLograd", "_text"], "tipo": "string"},
                    "115 DK-Complemento no endereço de residência no exterior": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "endereco", "exterior", "complemento", "_text"], "tipo": "string"},
                    "116 DL-Cidade de residência no exterior": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "endereco", "exterior", "nmCid", "_text"], "tipo": "string"},
                    "118 DN-CEP de residência no exterior": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "endereco", "exterior", "codPostal", "_text"], "tipo": "string"},
                    "14 N-Indicativo de deficiência": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "infoDeficiencia", "defFisica", "_text"], "tipo": "string"},
                    "15 O-Indicativo de deficiência física": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "infoDeficiencia", "defFisica", "_text"], "tipo": "string"},
                    "16 P-Indicativo de deficiência visual": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "infoDeficiencia", "defVisual", "_text"], "tipo": "string"},
                    "17 Q-Indicativo de deficiência auditiva": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "infoDeficiencia", "defAuditiva", "_text"], "tipo": "string"},
                    "18 R-Indicativo de deficiência mental": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "infoDeficiencia", "defMental", "_text"], "tipo": "string"},
                    "19 S-Indicativo de deficiência intelectual": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "infoDeficiencia", "defIntelectual", "_text"], "tipo": "string"},
                    "20 T-Trabalhador reabilitado ou adaptado": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "infoDeficiencia", "reabReadap", "_text"], "tipo": "string"},
                    "21 U-Trabalhador faz parte de cota de deficiente": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "infoDeficiencia", "infoCota", "_text"], "tipo": "string"},
                    "103 CY-Observações sobre a situação militar": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "infoDeficiencia", "observacao", "_text"], "tipo": "string"},
                    "89 CK-Número da CNH": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "documentos", "cnh", "nrRegCnh", "_text"], "tipo": "string"},
                    "90 CL-Categoria da CNH": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "documentos", "cnh", "categoriaCnh", "_text"], "tipo": "string"},
                    "91 CM-UF da CNH": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "documentos", "cnh", "ufCnh", "_text"], "tipo": "string"},
                    "92 CN-Data de emissão da CNH": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "documentos", "cnh", "dtExped", "_text"], "tipo": "string"},
                    "93 CO-Data de emissão da primeira CNH": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "documentos", "cnh", "dtPriHab", "_text"], "tipo": "string"},
                    "94 CP-Data de validade da CNH": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "documentos", "cnh", "dtValid", "_text"], "tipo": "string"},
                    "60 BH-Número do RNE": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "documentos", "rne", "nrRne", "_text"], "tipo": "string"},
                    "61 BI-Órgão emissor do RNE": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "documentos", "rne", "orgaoEmissor", "_text"], "tipo": "string"},
                    "63 BK-Data de emissão do RNE": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "documentos", "rne", "dtExped", "_text"], "tipo": "data", "formato": "YYYY-MM-DD"},
                    "64 BL-Data da chegada no país": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "trabEstrangeiro", "dtChegada", "_text"], "tipo": "data", "formato": "YYYY-MM-DD"},
                    "65 BM-Classificação estrangeiro": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "trabEstrangeiro", "classTrabEstrang", "_text"], "tipo": "string"},
                    "66 BN-Estrangeiro casado com brasileiro": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "trabEstrangeiro", "casadoBr", "_text"], "tipo": "string"},
                    "67 BO-Estrangeiro com filhos brasileiros": {"origem": "json_data", "caminho_json": ["evtAdmissao", "trabalhador", "trabEstrangeiro", "filhosBr", "_text"], "tipo": "string"},
                    # --- INÍCIO CAMPOS EXPANDIDOS S-2200 ---
                    "cpf_trabalhador": {"origem": "cpf_trabalhador", "tipo": "string"},
                    "nis_trabalhador": {"origem": "nis_trabalhador", "tipo": "string"},
                    "nome_trabalhador": {"origem": "nome_trabalhador", "tipo": "string"},
                    "sexo": {"origem": "sexo", "tipo": "string"},
                    "raca_cor": {"origem": "raca_cor", "tipo": "string"},
                    "estado_civil": {"origem": "estado_civil", "tipo": "string"},
                    "grau_instrucao": {"origem": "grau_instrucao", "tipo": "string"},
                    "data_nascimento": {"origem": "data_nascimento", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "nm_mae": {"origem": "nm_mae", "tipo": "string"},
                    "nm_pai": {"origem": "nm_pai", "tipo": "string"},
                    "uf_nasc": {"origem": "uf_nasc", "tipo": "string"},
                    "pais_nasc": {"origem": "pais_nasc", "tipo": "string"},
                    "pais_nac": {"origem": "pais_nac", "tipo": "string"},
                    "tp_lograd": {"origem": "tp_lograd", "tipo": "string"},
                    "dsc_lograd": {"origem": "dsc_lograd", "tipo": "string"},
                    "nr_lograd": {"origem": "nr_lograd", "tipo": "string"},
                    "complemento": {"origem": "complemento", "tipo": "string"},
                    "cep": {"origem": "cep", "tipo": "string"},
                    "bairro": {"origem": "bairro", "tipo": "string"},
                    "cod_munic": {"origem": "cod_munic", "tipo": "string"},
                    "nm_cidade": {"origem": "nm_cidade", "tipo": "string"},
                    "uf_resid": {"origem": "uf_resid", "tipo": "string"},
                    "pais_resid": {"origem": "pais_resid", "tipo": "string"},
                    "bairro_ext": {"origem": "bairro_ext", "tipo": "string"},
                    "dsc_lograd_ext": {"origem": "dsc_lograd_ext", "tipo": "string"},
                    "nr_lograd_ext": {"origem": "nr_lograd_ext", "tipo": "string"},
                    "complemento_ext": {"origem": "complemento_ext", "tipo": "string"},
                    "nm_cidade_ext": {"origem": "nm_cidade_ext", "tipo": "string"},
                    "cod_postal_ext": {"origem": "cod_postal_ext", "tipo": "string"},
                    "fone_princ": {"origem": "fone_princ", "tipo": "string"},
                    "fone_alt": {"origem": "fone_alt", "tipo": "string"},
                    "email_princ": {"origem": "email_princ", "tipo": "string"},
                    "email_alt": {"origem": "email_alt", "tipo": "string"},
                    "contato_emerg": {"origem": "contato_emerg", "tipo": "string"},
                    "fone_emerg": {"origem": "fone_emerg", "tipo": "string"},
                    "parentesco_emerg": {"origem": "parentesco_emerg", "tipo": "string"},
                    "ctps_numero": {"origem": "ctps_numero", "tipo": "string"},
                    "ctps_serie": {"origem": "ctps_serie", "tipo": "string"},
                    "ctps_uf": {"origem": "ctps_uf", "tipo": "string"},
                    "rg_numero": {"origem": "rg_numero", "tipo": "string"},
                    "rg_orgao": {"origem": "rg_orgao", "tipo": "string"},
                    "rg_data": {"origem": "rg_data", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "rg_uf": {"origem": "rg_uf", "tipo": "string"},
                    "rne_numero": {"origem": "rne_numero", "tipo": "string"},
                    "rne_orgao": {"origem": "rne_orgao", "tipo": "string"},
                    "rne_uf": {"origem": "rne_uf", "tipo": "string"},
                    "cnh_numero": {"origem": "cnh_numero", "tipo": "string"},
                    "cnh_categoria": {"origem": "cnh_categoria", "tipo": "string"},
                    "cnh_uf": {"origem": "cnh_uf", "tipo": "string"},
                    "cnh_data": {"origem": "cnh_data", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "cnh_pri_hab": {"origem": "cnh_pri_hab", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "cnh_validade": {"origem": "cnh_validade", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "def_fisica": {"origem": "def_fisica", "tipo": "string"},
                    "def_visual": {"origem": "def_visual", "tipo": "string"},
                    "def_auditiva": {"origem": "def_auditiva", "tipo": "string"},
                    "def_mental": {"origem": "def_mental", "tipo": "string"},
                    "def_intelectual": {"origem": "def_intelectual", "tipo": "string"},
                    "reab_readap": {"origem": "reab_readap", "tipo": "string"},
                    "info_cota": {"origem": "info_cota", "tipo": "string"},
                    "observacao_def": {"origem": "observacao_def", "tipo": "string"},
                    "dt_chegada": {"origem": "dt_chegada", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "class_estrangeiro": {"origem": "class_estrangeiro", "tipo": "string"},
                    "casado_br": {"origem": "casado_br", "tipo": "string"},
                    "filhos_br": {"origem": "filhos_br", "tipo": "string"},
                    "matricula": {"origem": "matricula", "tipo": "string"},
                    "data_admissao": {"origem": "data_admissao", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "tipo_admissao": {"origem": "tipo_admissao", "tipo": "string"},
                    "tipo_regime_jornada": {"origem": "tipo_regime_jornada", "tipo": "string"},
                    "natureza_atividade": {"origem": "natureza_atividade", "tipo": "string"},
                    "cnpj_empregador": {"origem": "cnpj_empregador", "tipo": "string"},
                    "cod_categoria": {"origem": "cod_categoria", "tipo": "string"},
                    "cod_cargo": {"origem": "cod_cargo", "tipo": "string"},
                    "cod_funcao": {"origem": "cod_funcao", "tipo": "string"},
                    "cod_lotacao": {"origem": "cod_lotacao", "tipo": "string"},
                    "salario_contratual": {"origem": "salario_contratual", "tipo": "decimal"},
                    "und_sal_fixo": {"origem": "und_sal_fixo", "tipo": "string"},
                    "tipo_contrato": {"origem": "tipo_contrato", "tipo": "string"},
                    "duracao_contrato": {"origem": "duracao_contrato", "tipo": "string"},
                    "passaporte_numero": {"origem": "passaporte_numero", "tipo": "string"},
                    "passaporte_pais_origem": {"origem": "passaporte_pais_origem", "tipo": "string"},
                    "passaporte_data_emissao": {"origem": "passaporte_data_emissao", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "passaporte_validade": {"origem": "passaporte_validade", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "ric_numero": {"origem": "ric_numero", "tipo": "string"},
                    "ric_orgao": {"origem": "ric_orgao", "tipo": "string"},
                    "ric_uf": {"origem": "ric_uf", "tipo": "string"},
                    "ric_data_emissao": {"origem": "ric_data_emissao", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "pis_numero": {"origem": "pis_numero", "tipo": "string"},
                    "pis_data_emissao": {"origem": "pis_data_emissao", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "titulo_eleitor_numero": {"origem": "titulo_eleitor_numero", "tipo": "string"},
                    "titulo_eleitor_zona": {"origem": "titulo_eleitor_zona", "tipo": "string"},
                    "titulo_eleitor_secao": {"origem": "titulo_eleitor_secao", "tipo": "string"},
                    "titulo_eleitor_cod_munic": {"origem": "titulo_eleitor_cod_munic", "tipo": "string"},
                    "titulo_eleitor_nm_cidade": {"origem": "titulo_eleitor_nm_cidade", "tipo": "string"},
                    "titulo_eleitor_uf": {"origem": "titulo_eleitor_uf", "tipo": "string"},
                    "titulo_eleitor_data_emissao": {"origem": "titulo_eleitor_data_emissao", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "cert_militar_numero": {"origem": "cert_militar_numero", "tipo": "string"},
                    "cert_militar_data_exped": {"origem": "cert_militar_data_exped", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "cert_militar_regiao": {"origem": "cert_militar_regiao", "tipo": "string"},
                    "cert_militar_tipo": {"origem": "cert_militar_tipo", "tipo": "string"},
                    "cert_militar_numero2": {"origem": "cert_militar_numero2", "tipo": "string"},
                    "cert_militar_serie": {"origem": "cert_militar_serie", "tipo": "string"},
                    "cert_militar_data_exped2": {"origem": "cert_militar_data_exped2", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "cert_militar_categoria": {"origem": "cert_militar_categoria", "tipo": "string"},
                    "cert_militar_observacoes": {"origem": "cert_militar_observacoes", "tipo": "string"},
                    "profissao": {"origem": "profissao", "tipo": "string"},
                    "conselho_numero": {"origem": "conselho_numero", "tipo": "string"},
                    "conselho_orgao": {"origem": "conselho_orgao", "tipo": "string"},
                    "conselho_uf": {"origem": "conselho_uf", "tipo": "string"},
                    "conselho_data_emissao": {"origem": "conselho_data_emissao", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "conselho_data_validade": {"origem": "conselho_data_validade", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "conselho_observacoes": {"origem": "conselho_observacoes", "tipo": "string"},
                    "banco_forma_pagamento": {"origem": "banco_forma_pagamento", "tipo": "string"},
                    "banco_codigo": {"origem": "banco_codigo", "tipo": "string"},
                    "banco_agencia": {"origem": "banco_agencia", "tipo": "string"},
                    "banco_agencia_dv": {"origem": "banco_agencia_dv", "tipo": "string"},
                    "banco_conta": {"origem": "banco_conta", "tipo": "string"},
                    "banco_conta_dv": {"origem": "banco_conta_dv", "tipo": "string"},
                    "banco_tipo_conta": {"origem": "banco_tipo_conta", "tipo": "string"},
                    "banco_tipo_operacao": {"origem": "banco_tipo_operacao", "tipo": "string"},
                    "peso": {"origem": "peso", "tipo": "string"},
                    "altura": {"origem": "altura", "tipo": "string"},
                    "tamanho_calca": {"origem": "tamanho_calca", "tipo": "string"},
                    "tamanho_camisa": {"origem": "tamanho_camisa", "tipo": "string"},
                    "tamanho_calcado": {"origem": "tamanho_calcado", "tipo": "string"},
                    "cns_numero": {"origem": "cns_numero", "tipo": "string"},
                    "observacoes_gerais": {"origem": "observacoes_gerais", "tipo": "string"},
                    # --- FIM CAMPOS EXPANDIDOS S-2200 ---
                }
            },
            
            "03_CONVCONTRATOALT": {
                "fonte_principal": "esocial_s2205",
                "fontes_adicionais": ["esocial_s2206"],
                "campos": {
                    # --- CAMPOS PRINCIPAIS MAPEADOS DIRETAMENTE DO BANCO ---
                    "1 A-ID do empregador": {"origem": "cnpj_empregador", "tipo": "string"},
                    "2 B-Nome do trabalhador": {"origem": "nome_trabalhador", "tipo": "string"},
                    "3 C -Código do contrato": {"origem": "matricula", "tipo": "string"},
                    "4 D-Tipo de transferência": {"origem": "json_data", "caminho_json": ["altContratual", "tpRegJor", "_text"], "tipo": "string"},
                    "5 E-Data da alteração": {"origem": "json_data", "caminho_json": ["alteracao", "dtAlteracao", "_text"], "tipo": "data", "formato": "YYYY-MM-DD"},
                    "6 F-Alteração registrada em": {"origem": "data_importacao", "tipo": "datetime", "formato": "YYYY-MM-DDTHH:mm:ss"},
                    "7 G-ID do novo empregador": {"origem": "json_data", "caminho_json": ["altContratual", "infoContrato", "codCateg", "_text"], "tipo": "string"},
                    "8 H-Código do novo estabelecimento": {"origem": "json_data", "caminho_json": ["altContratual", "infoContrato", "localTrabalho", "localTrabGeral", "nrInsc", "_text"], "tipo": "string"},
                    "9 I-Código do novo departamento": {"origem": "json_data", "caminho_json": ["altContratual", "infoContrato", "localTrabalho", "localTrabGeral", "descComp", "_text"], "tipo": "string"},
                    "10 J-Código do novo cargo": {"origem": "json_data", "caminho_json": ["altContratual", "infoContrato", "codCargo", "_text"], "tipo": "string"},
                    "11 K-Valor do novo salário": {"origem": "json_data", "caminho_json": ["altContratual", "infoContrato", "remuneracao", "vrSalFx", "_text"], "tipo": "decimal"},
                    "12 L-Tipo do novo salário": {"origem": "json_data", "caminho_json": ["altContratual", "infoContrato", "remuneracao", "undSalFixo", "_text"], "tipo": "string"},
                    "13 M-Código do motivo de reajuste": {"origem": "json_data", "caminho_json": ["altContratual", "infoContrato", "motivoReajuste", "_text"], "tipo": "string"},
                    "14 N-Código da nova jornada de trabalho": {"origem": "json_data", "caminho_json": ["altContratual", "infoContrato", "horContratual", "tpJornada", "_text"], "tipo": "string"},
                    "15 O-Código do novo sindicato": {"origem": "json_data", "caminho_json": ["altContratual", "infoContrato", "sindicato", "cnpjSindicato", "_text"], "tipo": "string"}
                }
            },
            "04_CONVDEPENDENTE": {
                "fonte_principal": "esocial_dependentes",
                "fontes_adicionais": [],
                "campos": {
                    "1 A-ID do empregador": {
                        "origem": "cnpj_empregador",
                        "tipo": "string", 
                        "obrigatorio": True, 
                        "valor_padrao": ""
                    },
                    "2 B  - Código do trabalhador": {
                        "origem": "cpf_trabalhador",
                        "tipo": "string", 
                        "obrigatorio": True, 
                        "valor_padrao": ""
                    },
                    "3 C  - Código do tipo de dependente": {
                        "origem": "tipo_dependente",
                        "tipo": "string", 
                        "valor_padrao": ""
                    },
                    "4 D  - Código do dependente": {
                        "origem": "cpf_dependente",
                        "tipo": "string", 
                        "valor_padrao": ""
                    },
                    "5 E  - Nome do dependente": {
                        "origem": "nome_dependente",
                        "tipo": "string", 
                        "obrigatorio": True, 
                        "valor_padrao": ""
                    },
                    "6 F  - Início da vigência": {
                        "origem": "json_data",
                        "caminho_json": ["dtIniVig", "_text"],
                        "tipo": "data", 
                        "formato": "YYYY-MM-DD", 
                        "valor_padrao": ""
                    },
                    "7 G  - Término da vigência": {
                        "origem": "json_data",
                        "caminho_json": ["dtFimVig", "_text"],
                        "tipo": "data", 
                        "formato": "YYYY-MM-DD", 
                        "valor_padrao": ""
                    },
                    "8 H  - Sexo do dependente": {
                        "origem": "sexo_dependente",
                        "tipo": "string", 
                        "valor_padrao": ""
                    },
                    "9 I  - Data de nascimento do dependente": {
                        "origem": "data_nascimento",
                        "tipo": "data", 
                        "formato": "YYYY-MM-DD", 
                        "valor_padrao": ""
                    },
                    "10 J  - Nome da mãe": {
                        "origem": "json_data",
                        "caminho_json": ["nmMae", "_text"],
                        "tipo": "string", 
                        "valor_padrao": ""
                    },
                    "11 K  - CPF do dependente": {
                        "origem": "cpf_dependente",
                        "tipo": "string", 
                        "valor_padrao": ""
                    },
                    "12 L  - Paga salário família": {
                        "origem": "dep_sf",
                        "tipo": "string", 
                        "valor_padrao": ""
                    },
                    "13 M  - Data de baixa do salário  família": {
                        "origem": "json_data",
                        "caminho_json": ["dtBaixaSF", "_text"],
                        "tipo": "data", 
                        "formato": "YYYY-MM-DD", 
                        "valor_padrao": ""
                    },
                    "14 N  - Dependente para IRRF": {
                        "origem": "dep_irrf",
                        "tipo": "string", 
                        "valor_padrao": ""
                    },
                    "15 O  - Data de baixa de dependente para IRRF": {
                        "origem": "json_data",
                        "caminho_json": ["dtBaixaIRRF", "_text"],
                        "tipo": "data", 
                        "formato": "YYYY-MM-DD", 
                        "valor_padrao": ""
                    },
                    "16 P  - Filho deficiente recebe salário família": {
                        "origem": "json_data",
                        "caminho_json": ["defSF", "_text"],
                        "tipo": "string", 
                        "valor_padrao": ""
                    },
                    "17 Q  - Código da cidade de nascimento": {
                        "origem": "json_data",
                        "caminho_json": ["codMunic", "_text"],
                        "tipo": "string", 
                        "valor_padrao": ""
                    },
                    "18 R  - Número da certidão de nascimento do dependente": {
                        "origem": "json_data",
                        "caminho_json": ["numCert", "_text"],
                        "tipo": "string", 
                        "valor_padrao": ""
                    },
                    "19 S  - Nome do cartório de registro": {
                        "origem": "json_data",
                        "caminho_json": ["nmCartorio", "_text"],
                        "tipo": "string", 
                        "valor_padrao": ""
                    },
                    "20 T  - Número de registro": {
                        "origem": "json_data",
                        "caminho_json": ["numReg", "_text"],
                        "tipo": "string", 
                        "valor_padrao": ""
                    },
                    "21 U  - Número no livro de registro": {
                        "origem": "json_data",
                        "caminho_json": ["numLivro", "_text"],
                        "tipo": "string", 
                        "valor_padrao": ""
                    },
                    "22 V  - Número na folha de registro": {
                        "origem": "json_data",
                        "caminho_json": ["numFolha", "_text"],
                        "tipo": "string", 
                        "valor_padrao": ""
                    },
                    "23 W  - Data de registro em cartório": {
                        "origem": "json_data",
                        "caminho_json": ["dtRegCartorio", "_text"],
                        "tipo": "data", 
                        "formato": "YYYY-MM-DD", 
                        "valor_padrao": ""
                    },
                    "24 X  - Data de entrega do documento": {
                        "origem": "json_data",
                        "caminho_json": ["dtEntDoc", "_text"],
                        "tipo": "data", 
                        "formato": "YYYY-MM-DD", 
                        "valor_padrao": ""
                    },
                    "25 Y  - Endereço do dependente": {
                        "origem": "json_data",
                        "caminho_json": ["endDep", "_text"],
                        "tipo": "string", 
                        "valor_padrao": ""
                    },
                    "26 Z  - Número de endereço": {
                        "origem": "json_data",
                        "caminho_json": ["numEnd", "_text"],
                        "tipo": "string", 
                        "valor_padrao": ""
                    },
                    "27 AA  - Bairro": {
                        "origem": "json_data",
                        "caminho_json": ["bairro", "_text"],
                        "tipo": "string", 
                        "valor_padrao": ""
                    },
                    "28 AB  - Código da cidade": {
                        "origem": "json_data",
                        "caminho_json": ["codMunic", "_text"],
                        "tipo": "string", 
                        "valor_padrao": ""
                    },
                    "29 AC  - CEP do dependente": {
                        "origem": "json_data",
                        "caminho_json": ["cep", "_text"],
                        "tipo": "string", 
                        "valor_padrao": ""
                    },
                    "30 AD  - Telefone 1 do dependente": {
                        "origem": "json_data",
                        "caminho_json": ["fone1", "_text"],
                        "tipo": "string", 
                        "valor_padrao": ""
                    },
                    "31 AE  - Telefone 2 do dependente": {
                        "origem": "json_data",
                        "caminho_json": ["fone2", "_text"],
                        "tipo": "string", 
                        "valor_padrao": ""
                    },
                    "32 AF  - Observações": {
                        "origem": "descr_dep",
                        "tipo": "string", 
                        "valor_padrao": ""
                    },
                    "33 AG  - Data de registro": {
                        "origem": "json_data",
                        "caminho_json": ["dtRegistro", "_text"],
                        "tipo": "data", 
                        "formato": "YYYY-MM-DD", 
                        "valor_padrao": ""
                    },
                    "34 AH  - Número do cartão nacional de saúde": {
                        "origem": "json_data",
                        "caminho_json": ["numCNS", "_text"],
                        "tipo": "string", 
                        "valor_padrao": ""
                    },
                    "35 AI  - Número da declaração de nascimento vivo": {
                        "origem": "json_data",
                        "caminho_json": ["numDNV", "_text"],
                        "tipo": "string", 
                        "valor_padrao": ""
                    },
                    "36 AJ  - Número do RG do dependente": {
                        "origem": "json_data",
                        "caminho_json": ["numRG", "_text"],
                        "tipo": "string", 
                        "valor_padrao": ""
                    },
                    "37 AK  - Origem": {
                        "origem": "json_data",
                        "caminho_json": ["origem", "_text"],
                        "tipo": "string", 
                        "valor_padrao": ""
                    },
                    "38 AL  - Destino": {
                        "origem": "json_data",
                        "caminho_json": ["destino", "_text"],
                        "tipo": "string", 
                        "valor_padrao": ""
                    }
                }
            },
            "05_FERIAS": {
                "fonte_principal": "esocial_s2230",
                "filtros": {"tipo_afastamento": "ferias"},
                "campos": {
                    "1 A-ID do empregador": {
                        "origem": "cnpj_empregador",
                        "caminho_json": ["evtAfastTemp", "ideEmpregador", "nrInsc", "_text"],
                        "tipo": "string",
                        "obrigatorio": True
                    },
                    "2 B-CPF trabalhador": {
                        "origem": "cpf_trabalhador",
                        "caminho_json": ["evtAfastTemp", "ideTrabalhador", "cpfTrab", "_text"],
                        "tipo": "string",
                        "obrigatorio": True
                    },
                    "3 C-Matrícula": {
                        "origem": "matricula",
                        "caminho_json": ["evtAfastTemp", "ideTrabalhador", "matricula", "_text"],
                        "tipo": "string"
                    },
                    "4 D-Data início": {
                        "origem": "data_inicio",
                        "caminho_json": ["iniAfastamento", "dtIniAfast", "_text"],
                        "tipo": "data",
                        "formato": "YYYY-MM-DD"
                    },
                    "5 E-Data fim": {
                        "origem": "data_fim",
                        "caminho_json": ["fimAfastamento", "dtTermAfast", "_text"],
                        "tipo": "data",
                        "formato": "YYYY-MM-DD"
                    },
                    "6 F-Data início do abono": {
                        "origem": "json_data",
                        "caminho_json": ["iniAfastamento", "dtIniAbono", "_text"],
                        "tipo": "data",
                        "formato": "YYYY-MM-DD"
                    },
                    "7 G-Data fim do abono": {
                        "origem": "json_data",
                        "caminho_json": ["fimAfastamento", "dtFimAbono", "_text"],
                        "tipo": "data",
                        "formato": "YYYY-MM-DD"
                    },
                    "8 H-Período aquisitivo início": {
                        "origem": "json_data",
                        "caminho_json": ["iniAfastamento", "perAquis", "dtInicio", "_text"],
                        "tipo": "data",
                        "formato": "YYYY-MM-DD"
                    },
                    "9 I-Período aquisitivo fim": {
                        "origem": "json_data",
                        "caminho_json": ["iniAfastamento", "perAquis", "dtFim", "_text"],
                        "tipo": "data",
                        "formato": "YYYY-MM-DD"
                    },
                    "10 J-Número de dias de férias": {
                        "origem": "json_data",
                        "caminho_json": ["iniAfastamento", "qtdDiasFerias", "_text"],
                        "tipo": "string"
                    },
                    "11 K-Indicativo de férias coletivas": {
                        "origem": "json_data",
                        "caminho_json": ["iniAfastamento", "indFeriasColetivas", "_text"],
                        "tipo": "string"
                    }
                }
            },
            "06_CONVFICHA": {
                "fonte_principal": "esocial_s1200",
                "campos": {
                    "1 A-ID do empregador": {"origem": "cnpj_empregador", "tipo": "string", "obrigatorio": True},
                    "2 B-Código do estabelecimento": {"origem": "estabelecimento", "tipo": "string"},
                    "3 C - Código do tipo de cálculo": {"origem": "tipo_calculo", "tipo": "string"},
                    "4 D  - Data do pagamento": {"origem": "data_pagamento", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "5 E  - Data inicial do cálculo": {"origem": "data_inicio_calculo", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "6 F  - Data final do cálculo": {"origem": "data_fim_calculo", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "7 G  - Data de cálculo da folha": {"origem": "data_calculo_folha", "tipo": "data", "formato": "YYYY-MM-DD"},
                    "8 H  - Código do trabalhador": {"origem": "cpf_trabalhador", "tipo": "string"},
                    "9 I  - Nome do trabalhador": {"origem": "nome_trabalhador", "tipo": "string"},
                    "10 J-Código do contrato": {"origem": "matricula", "tipo": "string"},
                    "11 K-Código da categoria": {"origem": "cod_categoria", "tipo": "string"},
                    "12 L-Código da rubrica": {"origem": "codigo_rubrica", "tipo": "string"},
                    "13 M-Descrição da rubrica": {"origem": "descricao_rubrica", "tipo": "string"},
                    "14 N-Código do estabelecimento": {"origem": "estabelecimento", "tipo": "string"},
                    "15 O-Código da lotação tributária": {"origem": "lotacao_tributaria", "tipo": "string"},
                    "16 P-Código da rubrica para o recibo": {"origem": "codigo_rubrica", "tipo": "string"},
                    "17 Q-Descrição da rubrica para o recibo": {"origem": "descricao_rubrica", "tipo": "string"},
                    "18 R-Qtde dependentes para IR": {"origem": "qtd_dep_ir", "tipo": "string"},
                    "19 S  - Qtde dependentes para SF": {"origem": "qtd_dep_sf", "tipo": "string"},
                    "20 T  - Código de exposição à agentes nocivos": {"origem": "cod_exposicao", "tipo": "string"},
                    "21 U  - Grau de insalubridade": {"origem": "grau_insalubridade", "tipo": "string"},
                    "22 V  - Tem periculosidade": {"origem": "tem_periculosidade", "tipo": "string"},
                    "23 W  - Ensejo de aposentadoria especial": {"origem": "ensejo_aposentadoria", "tipo": "string"},
                    "24 X  - Período de referência": {"origem": "periodo_apuracao", "tipo": "string"},
                    "25 Y  - Sigla da rubrica": {"origem": "json_data", "caminho_json": ["cod", "_text"], "tipo": "string"},
                    "26 Z  - Sigla da rubrica para o recibo": {"origem": "json_data", "caminho_json": ["cod", "_text"], "tipo": "string"},
                    "27 AA  - Descrição da rubrica para o recibo": {"origem": "descricao_rubrica", "tipo": "string"},
                    "28 AB  - Razão ou qtde": {"origem": "json_data", "caminho_json": ["qtdRubr", "_text"], "valor_padrao": "1", "tipo": "decimal"},
                    "29 AC  - Valor da rubrica": {"origem": "json_data", "caminho_json": ["vrRubr", "_text"], "tipo": "decimal"},
                    "30 AD  - Classe da rubrica": {"origem": "tipo_rubrica", "valor_padrao": "M", "tipo": "string"},
                    "31 AE  - Período de referência": {"origem": "periodo_apuracao", "tipo": "string"}
                }
            },
            "07_CARGOS": {
                "fonte_principal": "esocial_s1030",
                "campos": {
                    "1 A-ID do empregador": {"origem": "cnpj_empregador", "tipo": "string"},
                    "2 B-Código do cargo": {"origem": "codigo", "tipo": "string"},
                    "3 C-Nome do cargo": {"origem": "descricao", "tipo": "string"},
                    "4 D-ID do tipo de código": {"origem": "nivel_cargo", "tipo": "string"},
                    "5 E-ID do nível organizacional": {"origem": "nivel_cargo", "tipo": "string"},
                    "6 F-Código do CBO": {"origem": "cbo", "tipo": "string"},
                    "7 G-Início da validade": {"origem": "inicio_validade", "tipo": "string"},
                    "8 H-Término da validade": {"origem": "fim_validade", "tipo": "string"},
                    "9 I-Descrição sumária": {"origem": "desc_sumaria", "tipo": "string"},
                    "10 J-Permite acúmulo de cargo": {"origem": "permite_acumulo", "tipo": "string"},
                    "11 L-Permite contagem especial do acúmulo de cargo": {"origem": "permite_contagem_esp", "tipo": "string"},
                    "12 M-Cargo de dedicação exclusiva": {"origem": "dedicacao_exclusiva", "tipo": "string"},
                    "13 N-Número da Lei que criou e/ou extinguiu e/ou restruturou o": {"origem": "num_lei", "tipo": "string"},
                    "14 O-Data da Lei que criou e/ou extinguiu e/ou restruturou o ca": {"origem": "dt_lei", "tipo": "string"},
                    "15 P-Situação gerada pela Lei": {"origem": "situacao_lei", "tipo": "string"},
                    "16 Q-O cargo tem função": {"origem": "tem_funcao", "tipo": "string"}
                }
            },
            "08_CONVAFASTAMENTO": {
                "fonte_principal": "esocial_s2230",
                "campos": {
                    "1 A-ID do empregador": {"origem": "cnpj_empregador", "tipo": "string", "obrigatorio": True},
                    "2-Nome do trabalhador": {"origem": "cpf_trabalhador", "tipo": "string", "obrigatorio": True},
                    "3-Código do contrato": {"origem": "matricula", "tipo": "string", "obrigatorio": True},
                    "4-Código do motivo de afastamento": {"origem": "json_data", "caminho_json": ["iniAfastamento", "codMotAfast", "_text"], "tipo": "string"},
                    "5-Data inicial de afastamento": {"origem": "json_data", "caminho_json": ["iniAfastamento", "dtIniAfast", "_text"], "tipo": "data", "formato": "YYYY-MM-DD"},
                    "6-Data final de afastamento": {"origem": "json_data", "caminho_json": ["fimAfastamento", "dtTermAfast", "_text"], "tipo": "data", "formato": "YYYY-MM-DD"},
                    "7-Observações do afastamento": {"origem": "json_data", "caminho_json": ["iniAfastamento", "observacao", "_text"], "tipo": "string"},
                    "8-Descrição do motivo de afastamento": {"origem": "descricao_motivo", "tipo": "string"},
                    "9-Mesmo motivo anterior": {"origem": "json_data", "caminho_json": ["iniAfastamento", "infoMesmoMtv", "_text"], "tipo": "string"},
                    "10-Tipo acidente trânsito": {"origem": "json_data", "caminho_json": ["iniAfastamento", "tpAcidTransito", "_text"], "tipo": "string"},
                    "11-Período aquisitivo início": {"origem": "json_data", "caminho_json": ["iniAfastamento", "perAquis", "dtInicio", "_text"], "tipo": "data", "formato": "YYYY-MM-DD"},
                    "12-Período aquisitivo fim": {"origem": "json_data", "caminho_json": ["iniAfastamento", "perAquis", "dtFim", "_text"], "tipo": "data", "formato": "YYYY-MM-DD"},
                    "13-Cessão CNPJ": {"origem": "json_data", "caminho_json": ["iniAfastamento", "infoCessao", "cnpjCess", "_text"], "tipo": "string"},
                    "14-Cessão ônus": {"origem": "json_data", "caminho_json": ["iniAfastamento", "infoCessao", "infOnus", "_text"], "tipo": "string"},
                    "15-Mandato sindical CNPJ": {"origem": "json_data", "caminho_json": ["iniAfastamento", "infoMandSind", "cnpjSind", "_text"], "tipo": "string"},
                    "16-Mandato sindical ônus remuneração": {"origem": "json_data", "caminho_json": ["iniAfastamento", "infoMandSind", "infOnusRemun", "_text"], "tipo": "string"},
                    "17-Mandato eletivo CNPJ": {"origem": "json_data", "caminho_json": ["iniAfastamento", "infoMandElet", "cnpjMandElet", "_text"], "tipo": "string"},
                    "18-Mandato eletivo remuneração cargo": {"origem": "json_data", "caminho_json": ["iniAfastamento", "infoMandElet", "indRemunCargo", "_text"], "tipo": "string"},
                    "19-Retificação origem": {"origem": "json_data", "caminho_json": ["infoRetif", "origRetif", "_text"], "tipo": "string"},
                    "20-Retificação tipo processo": {"origem": "json_data", "caminho_json": ["infoRetif", "tpProc", "_text"], "tipo": "string"},
                    "21-Retificação número processo": {"origem": "json_data", "caminho_json": ["infoRetif", "nrProc", "_text"], "tipo": "string"}
                }
            },
            "09_CONVATESTADO": {
                "fonte_principal": "esocial_s2230",
                "campos": {
                    "1 - ID do empregador": {"origem": "cnpj_empregador", "tipo": "string", "obrigatorio": True},
                    "9 - Código de identificação do contrato": {"origem": "matricula", "tipo": "string", "obrigatorio": True},
                    "2 - Data da consulta": {"origem": "json_data", "caminho_json": ["iniAfastamento", "infoAtestado", 0, "dtDiagnostico", "_text"], "tipo": "data", "formato": "YYYY-MM-DD"},
                    "4 - Data inicial": {"origem": "json_data", "caminho_json": ["iniAfastamento", "dtIniAfast", "_text"], "tipo": "data", "formato": "YYYY-MM-DD"},
                    "6 - Data final": {"origem": "json_data", "caminho_json": ["fimAfastamento", "dtTermAfast", "_text"], "tipo": "data", "formato": "YYYY-MM-DD"},
                    "8 - Qtde de dias do atestado": {"origem": "json_data", "caminho_json": ["iniAfastamento", "infoAtestado", 0, "qtdDiasAfast", "_text"], "tipo": "string"},
                    "10 - Código CID": {"origem": "json_data", "caminho_json": ["iniAfastamento", "infoAtestado", 0, "codCID", "_text"], "tipo": "string"},
                    "11 - MedicoTpCons": {"origem": "json_data", "caminho_json": ["iniAfastamento", "infoAtestado", 0, "tpConsulta", "_text"], "tipo": "string"},
                    "12 - Número de inscrição do médico": {"origem": "json_data", "caminho_json": ["iniAfastamento", "infoAtestado", 0, "emitente", "nrOC", "_text"], "tipo": "string"},
                    "13 - UF do CRM do médico": {"origem": "json_data", "caminho_json": ["iniAfastamento", "infoAtestado", 0, "emitente", "ufOC", "_text"], "tipo": "string"},
                    "14 - Mesmo motivo anterior": {"origem": "json_data", "caminho_json": ["iniAfastamento", "infoMesmoMtv", "_text"], "tipo": "string"},
                    "15 - Tipo acidente trânsito": {"origem": "json_data", "caminho_json": ["iniAfastamento", "tpAcidTransito", "_text"], "tipo": "string"},
                    "16 - Observações do afastamento": {"origem": "json_data", "caminho_json": ["iniAfastamento", "observacao", "_text"], "tipo": "string"},
                    "17 - Período aquisitivo início": {"origem": "json_data", "caminho_json": ["iniAfastamento", "perAquis", "dtInicio", "_text"], "tipo": "data", "formato": "YYYY-MM-DD"},
                    "18 - Período aquisitivo fim": {"origem": "json_data", "caminho_json": ["iniAfastamento", "perAquis", "dtFim", "_text"], "tipo": "data", "formato": "YYYY-MM-DD"},
                    "19 - Cessão CNPJ": {"origem": "json_data", "caminho_json": ["iniAfastamento", "infoCessao", "cnpjCess", "_text"], "tipo": "string"},
                    "20 - Cessão ônus": {"origem": "json_data", "caminho_json": ["iniAfastamento", "infoCessao", "infOnus", "_text"], "tipo": "string"},
                    "21 - Mandato sindical CNPJ": {"origem": "json_data", "caminho_json": ["iniAfastamento", "infoMandSind", "cnpjSind", "_text"], "tipo": "string"},
                    "22 - Mandato sindical ônus remuneração": {"origem": "json_data", "caminho_json": ["iniAfastamento", "infoMandSind", "infOnusRemun", "_text"], "tipo": "string"},
                    "23 - Mandato eletivo CNPJ": {"origem": "json_data", "caminho_json": ["iniAfastamento", "infoMandElet", "cnpjMandElet", "_text"], "tipo": "string"},
                    "24 - Mandato eletivo remuneração cargo": {"origem": "json_data", "caminho_json": ["iniAfastamento", "infoMandElet", "indRemunCargo", "_text"], "tipo": "string"},
                    "25 - Retificação origem": {"origem": "json_data", "caminho_json": ["infoRetif", "origRetif", "_text"], "tipo": "string"},
                    "26 - Retificação tipo processo": {"origem": "json_data", "caminho_json": ["infoRetif", "tpProc", "_text"], "tipo": "string"},
                    "27 - Retificação número processo": {"origem": "json_data", "caminho_json": ["infoRetif", "nrProc", "_text"], "tipo": "string"}
                }
            },
        }
    
    def _extrair_valor_json_com_alternativos(self, json_data: str, definicao_campo: Dict[str, Any]) -> Any:
        """
        Extrai valor de um campo JSON usando caminho principal e alternativos, com fallback para valor padrão.
        """
        caminhos = []
        if "caminho_json" in definicao_campo:
            caminhos.append(definicao_campo["caminho_json"])
        caminhos += definicao_campo.get("caminho_json_alternativos", [])
        for caminho in caminhos:
            valor = self._extrair_valor_json(json_data, caminho)
            if valor is not None and (not isinstance(valor, str) or valor.strip()):
                return valor
        # Fallback para valor padrão
        return definicao_campo.get("valor_padrao", None)

    def obter_valor_campo(self, template: str, campo: str, registro_bd: Dict[str, Any]) -> Any:
        """
        Obtém o valor de um campo específico do template, considerando caminhos alternativos e valor padrão.
        """
        if template not in self.mapeamentos:
            return None
        mapeamento_template = self.mapeamentos[template]
        if campo not in mapeamento_template["campos"]:
            return None
        definicao_campo = mapeamento_template["campos"][campo]
        # Obter valor baseado na origem
        if definicao_campo["origem"] == "json_data":
            json_str = registro_bd.get("json_data") or ""
            return self._extrair_valor_json_com_alternativos(json_str, definicao_campo)
        else:
            return registro_bd.get(definicao_campo["origem"])
    
    def _extrair_valor_json(self, json_data: str, caminho: List[str]) -> Any:
        """
        Extrai valor de um campo JSON usando caminho
        Args:
            json_data: String JSON
            caminho: Lista com caminho para o campo
        Returns:
            Valor extraído ou None
        """
        if not json_data or not caminho:
            return None
        try:
            dados = json.loads(json_data) if isinstance(json_data, str) else json_data
            for chave in caminho:
                if isinstance(dados, dict) and chave in dados:
                    dados = dados[chave]
                else:
                    return None
            # Se chegou ao final do caminho:
            if isinstance(dados, dict):
                # Se tem _text, retorna
                if '_text' in dados:
                    return dados['_text']
                # Se só tem um valor, retorna esse valor
                if len(dados) == 1:
                    return list(dados.values())[0]
                return None
            return dados  # Se for string, número, etc.
        except (json.JSONDecodeError, AttributeError, KeyError, TypeError):
            return None
    
    def _extrair_do_json(self, json_data: str, caminho: List[str]) -> Any:
        """
        Alias para _extrair_valor_json para compatibilidade com testes.
        """
        return self._extrair_valor_json(json_data, caminho)
    
    def obter_mapeamento_template(self, template: str) -> Dict[str, Any]:
        """
        Obtém o mapeamento completo de um template
        
        Args:
            template: Nome do template
            
        Returns:
            Dicionário com o mapeamento do template
        """
        return self.mapeamentos.get(template, {})
    
    def listar_templates(self) -> List[str]:
        """
        Lista todos os templates disponíveis
        
        Returns:
            Lista com nomes dos templates
        """
        return list(self.mapeamentos.keys())
    
    def validar_filtros_template(self, template: str, registro_bd: Dict[str, Any]) -> bool:
        """
        Valida se um registro atende aos filtros de um template
        
        Args:
            template: Nome do template
            registro_bd: Registro do banco de dados
            
        Returns:
            True se atende aos filtros, False caso contrário
        """
        if template not in self.mapeamentos:
            return True
            
        mapeamento = self.mapeamentos[template]
        filtros = mapeamento.get("filtros", {})
        
        if not filtros:
            return True
            
        # Implementar validação específica de filtros
        if "dias_afastamento" in filtros:
            return self._validar_filtro_dias_afastamento(registro_bd, filtros["dias_afastamento"])
            
        if "tipo_afastamento" in filtros:
            return self._validar_filtro_tipo_afastamento(registro_bd, filtros["tipo_afastamento"])
            
        return True
        
    def _validar_filtro_tipo_afastamento(self, registro_bd: Dict[str, Any], tipo: str) -> bool:
        """
        Valida filtro de tipo de afastamento
        
        Args:
            registro_bd: Registro do banco de dados
            tipo: Tipo de afastamento esperado (ex: "ferias", "doenca", etc.)
            
        Returns:
            True se atende ao filtro
        """
        try:
            # Verificar pelo código_motivo diretamente
            codigo_motivo = registro_bd.get("codigo_motivo", "")
            
            # Mapear tipos para códigos do eSocial
            mapa_tipos = {
                "ferias": ["15"],
                "doenca": ["01"],
                "acidente": ["02"],
                "licenca_maternidade": ["03"],
                "servico_militar": ["04"]
            }
            
            codigos_validos = mapa_tipos.get(tipo, [])
            if codigo_motivo in codigos_validos:
                return True
                
            # Se não encontrou pelo código, verificar no JSON
            if "json_data" in registro_bd and registro_bd["json_data"]:
                json_str = registro_bd["json_data"]
                if isinstance(json_str, str):
                    try:
                        json_data = json.loads(json_str)
                        
                        # Verificar no JSON aninhado
                        if "iniAfastamento" in json_data and "codMotAfast" in json_data["iniAfastamento"]:
                            cod_mot = json_data["iniAfastamento"]["codMotAfast"].get("_text", "")
                            if cod_mot in codigos_validos:
                                return True
                    except json.decoder.JSONDecodeError:
                        pass
            
            # Se o tipo for "todos" ou não especificado, aceitar qualquer afastamento
            if not tipo or tipo == "todos":
                return True
                
            return False
                    
        except (AttributeError, ValueError):
            # Em caso de erro, aceita o registro
            return True
    
    def _validar_filtro_dias_afastamento(self, registro_bd: Dict[str, Any], dias: int) -> bool:
        """
        Valida filtro de dias de afastamento
        
        Args:
            registro_bd: Registro do banco de dados
            dias: Quantidade mínima de dias para filtrar
            
        Returns:
            True se atende ao filtro
        """
        try:
            data_inicio = registro_bd.get("data_inicio")
            data_fim = registro_bd.get("data_fim")
            
            # Se não houver data de término, não é possível calcular os dias
            if not data_inicio or not data_fim:
                return False
                
            # Calcular os dias de afastamento
            from datetime import datetime
            formato = "%Y-%m-%d"
            inicio = datetime.strptime(data_inicio, formato)
            fim = datetime.strptime(data_fim, formato)
            dias_afastamento = (fim - inicio).days + 1  # Inclusivo
            
            # Verificar se atende ao filtro
            return dias_afastamento >= dias
                    
        except (AttributeError, ValueError):
            # Em caso de erro, aceita o registro
            return True
    
    def extrair_dependentes(self, json_data: str) -> List[dict]:
        """
        Extrai todos os dependentes do JSON do eSocial (S-2200, S-2205, S-2206).
        Retorna uma lista de dicts, cada um representando um dependente com todos os campos necessários.
        """
        dependentes = []
        try:
            dados = json.loads(json_data) if isinstance(json_data, str) else json_data

            # Extrair CNPJ do empregador
            cnpj_empregador = ""
            caminhos_empregador = [
                ["evtAdmissao", "ideEmpregador", "nrInsc"],
                ["evtAltCadastral", "ideEmpregador", "nrInsc"],
                ["evtAltContratual", "ideEmpregador", "nrInsc"],
                ["ideEmpregador", "nrInsc"]
            ]
            for caminho in caminhos_empregador:
                valor = self._extrair_valor_json(dados, caminho)
                if valor and isinstance(valor, dict) and "_text" in valor:
                    cnpj_empregador = valor["_text"]
                    break
                elif valor and isinstance(valor, str):
                    cnpj_empregador = valor
                    break

            # Extrair CPF do trabalhador
            cpf_trabalhador = ""
            caminhos_trabalhador = [
                ["evtAdmissao", "trabalhador", "cpfTrab"],
                ["evtAltCadastral", "ideTrabalhador", "cpfTrab"],
                ["evtAltContratual", "ideTrabalhador", "cpfTrab"],
                ["ideTrabalhador", "cpfTrab"]
            ]
            for caminho in caminhos_trabalhador:
                valor = self._extrair_valor_json(dados, caminho)
                if valor and isinstance(valor, dict) and "_text" in valor:
                    cpf_trabalhador = valor["_text"]
                    break
                elif valor and isinstance(valor, str):
                    cpf_trabalhador = valor
                    break

            # Caminhos possíveis para dependentes
            caminhos_dependentes = [
                ["evtAltCadastral", "alteracao", "dadosTrabalhador", "dependente"],
                ["evtAdmissao", "trabalhador", "dependente"],
                ["evtAltContratual", "alteracao", "dadosTrabalhador", "dependente"],
                ["trabalhador", "dependente"],
                ["alteracao", "dadosTrabalhador", "dependente"]
            ]
            for caminho in caminhos_dependentes:
                atual = dados
                for chave in caminho:
                    if isinstance(atual, dict) and chave in atual:
                        atual = atual[chave]
                    else:
                        atual = None
                        break
                if atual:
                    # Se for dict, transforma em lista
                    if isinstance(atual, dict):
                        atual = [atual]
                    if isinstance(atual, list):
                        for dep in atual:
                            dep_dict = {
                                "1 A-ID do empregador": cnpj_empregador,
                                "2 B-CPF trabalhador": cpf_trabalhador,
                                "3 C-Nome dependente": self._extrair_texto_json(dep, "nmDep"),
                                "4 D-Data nascimento": self._extrair_texto_json(dep, "dtNascto"),
                                "5 E-CPF dependente": self._extrair_texto_json(dep, "cpfDep"),
                                "6 F-Tipo dependência": self._extrair_texto_json(dep, "tpDep"),
                                "7 G-Possui pensão alimentícia": self._extrair_texto_json(dep, "depSF"),
                                "8 H-Nome mãe dependente": self._extrair_texto_json(dep, "nmMae"),
                                "9 I-Indicativo de deficiência": self._extrair_texto_json(dep, "incTrab"),
                                "10 J-É dependente IR": self._extrair_texto_json(dep, "depIRRF")
                            }
                            # Só adiciona se tiver nome do dependente
                            if dep_dict["3 C-Nome dependente"]:
                                dependentes.append(dep_dict)
                    if dependentes:
                        break
        except Exception as e:
            print(f"[Mapeador] Erro ao extrair dependentes: {e}")
        return dependentes
    
    def _extrair_texto_json(self, objeto: dict, chave: str) -> str:
        """
        Extrai texto de um campo JSON considerando diferentes formatos possíveis
        
        Args:
            objeto: Dicionário com dados JSON
            chave: Nome do campo a extrair
            
        Returns:
            String com o valor extraído ou vazio se não encontrado
        """
        if not objeto or not isinstance(objeto, dict):
            return ""
            
        # Formato padrão: {"chave": {"_text": "valor"}}
        if chave in objeto and isinstance(objeto[chave], dict) and "_text" in objeto[chave]:
            return objeto[chave]["_text"]
            
        # Formato alternativo: {"chave": "valor"}
        if chave in objeto and isinstance(objeto[chave], str):
            return objeto[chave]
            
        return ""

    def extrair_atestados(self, json_data: str) -> List[dict]:
        """
        Extrai todos os atestados do JSON do eSocial (S-2230).
        Retorna uma lista de dicts, cada um representando um atestado com todos os campos necessários.
        Filtrado para afastamentos menores que 15 dias, tipicamente atestados médicos.
        """
        import logging
        self.logger = logging.getLogger('mapeador_campos')
        self.logger.info("Iniciando extração de atestados")
        atestados = []
        try:
            dados = json.loads(json_data) if isinstance(json_data, str) else json_data
            ini = dados.get("iniAfastamento", {})
            info_atestados = ini.get("infoAtestado", [])
            if isinstance(info_atestados, dict):
                info_atestados = [info_atestados]
            for atestado in info_atestados:
                qtd_dias = atestado.get("qtdDiasAfast", {}).get("_text", "")
                if qtd_dias and int(qtd_dias) < 15:
                    # Extract all mapped fields for 09_CONVATESTADO
                    atestados.append({
                        "1 - ID do empregador": dados.get("cnpj_empregador", ""),
                        "9 - Código de identificação do contrato": dados.get("matricula", ""),
                        "2 - Data da consulta": atestado.get("dtDiagnostico", {}).get("_text", ""),
                        "4 - Data inicial": ini.get("dtIniAfast", {}).get("_text", ""),
                        "6 - Data final": dados.get("fimAfastamento", {}).get("dtTermAfast", {}).get("_text", ""),
                        "8 - Qtde de dias do atestado": atestado.get("qtdDiasAfast", {}).get("_text", ""),
                        "10 - Código CID": atestado.get("codCID", {}).get("_text", ""),
                        "11 - MedicoTpCons": atestado.get("tpConsulta", {}).get("_text", ""),
                        "12 - Número de inscrição do médico": atestado.get("emitente", {}).get("nrOC", {}).get("_text", ""),
                        "13 - UF do CRM do médico": atestado.get("emitente", {}).get("ufOC", {}).get("_text", ""),
                        "14 - Mesmo motivo anterior": ini.get("infoMesmoMtv", {}).get("_text", ""),
                        "15 - Tipo acidente trânsito": ini.get("tpAcidTransito", {}).get("_text", ""),
                        "16 - Observações do afastamento": ini.get("observacao", {}).get("_text", ""),
                        "17 - Período aquisitivo início": ini.get("perAquis", {}).get("dtInicio", {}).get("_text", ""),
                        "18 - Período aquisitivo fim": ini.get("perAquis", {}).get("dtFim", {}).get("_text", ""),
                        "19 - Cessão CNPJ": ini.get("infoCessao", {}).get("cnpjCess", {}).get("_text", ""),
                        "20 - Cessão ônus": ini.get("infoCessao", {}).get("infOnus", {}).get("_text", ""),
                        "21 - Mandato sindical CNPJ": ini.get("infoMandSind", {}).get("cnpjSind", {}).get("_text", ""),
                        "22 - Mandato sindical ônus remuneração": ini.get("infoMandSind", {}).get("infOnusRemun", {}).get("_text", ""),
                        "23 - Mandato eletivo CNPJ": ini.get("infoMandElet", {}).get("cnpjMandElet", {}).get("_text", ""),
                        "24 - Mandato eletivo remuneração cargo": ini.get("infoMandElet", {}).get("indRemunCargo", {}).get("_text", ""),
                        "25 - Retificação origem": dados.get("infoRetif", {}).get("origRetif", {}).get("_text", ""),
                        "26 - Retificação tipo processo": dados.get("infoRetif", {}).get("tpProc", {}).get("_text", ""),
                        "27 - Retificação número processo": dados.get("infoRetif", {}).get("nrProc", {}).get("_text", "")
                    })
        except Exception as e:
            self.logger.error(f"Erro ao extrair atestados: {e}")
        return atestados
    
    def extrair_cargos(self, json_data: str) -> List[dict]:
        """
 Extrai todos os cargos do JSON do eSocial (S-1030).
        Retorna uma lista de dicts, cada um representando um cargo com todos os campos necessários.
        """
        cargos = []
        try:
            dados = json.loads(json_data) if isinstance(json_data, str) else json_data
            
            # Extrair CNPJ do empregador para contexto
            cnpj_empregador = ""
            caminhos_empregador = [
                ["evtTabCargo", "ideEmpregador", "nrInsc"],
                ["ideEmpregador", "nrInsc"]
            ]
            
            for caminho in caminhos_empregador:
                valor = self._extrair_valor_json(dados, caminho)
                if valor and isinstance(valor, dict) and "_text" in valor:
                    cnpj_empregador = valor["_text"]
                    break
                elif valor and isinstance(valor, str):
                    cnpj_empregador = valor
                    break
            
            # Primeiro, buscar o ideCargo (contém código e datas de validade)
            caminhos_ide_cargo = [
                ["evtTabCargo", "infoCargo", "inclusao", "ideCargo"],
                ["evtTabCargo", "infoCargo", "alteracao", "ideCargo"],
                ["infoCargo", "inclusao", "ideCargo"],
                ["infoCargo", "alteracao", "ideCargo"]
            ]
            
            ide_cargo_data = {}
            for caminho in caminhos_ide_cargo:
                atual = dados
                valido = True
                for chave in caminho:
                    if isinstance(atual, dict) and chave in atual:
                        atual = atual.get(chave, {})
                    else:
                        valido = False
                        break
                        
                if valido and isinstance(atual, dict) and atual:
                    # Extrair informações do ideCargo
                    ide_cargo_data = {
                        "codCargo": self._extrair_texto_json(atual, "codCargo"),
                        "iniValid": self._extrair_texto_json(atual, "iniValid"),
                        "fimValid": self._extrair_texto_json(atual, "fimValid")
                    }
                    break
            
            # Depois, buscar o dadosCargo (contém nome, CBO, etc.)
            caminhos_dados_cargo = [
                ["evtTabCargo", "infoCargo", "inclusao", "dadosCargo"],
                ["evtTabCargo", "infoCargo", "alteracao", "dadosCargo"],
                ["infoCargo", "inclusao", "dadosCargo"],
                ["infoCargo", "alteracao", "dadosCargo"]
            ]
            
            for caminho in caminhos_dados_cargo:
                atual = dados
                valido = True
                for chave in caminho:
                    if isinstance(atual, dict) and chave in atual:
                        atual = atual.get(chave, {})
                    else:
                        valido = False
                        break
                
                if valido and isinstance(atual, dict) and atual:
                    # Combinar dados do ideCargo com dadosCargo
                    cargo = {
                        # Dados contextuais para o mapeamento
                        "cnpj_empregador": cnpj_empregador,
                        
                        # Dados do cargo
                        "codCargo": self._extrair_texto_json(atual, "codCargo") or ide_cargo_data.get("codCargo", ""),
                        "nmCargo": self._extrair_texto_json(atual, "nmCargo"),
                        "codCBO": self._extrair_texto_json(atual, "codCBO"),
                        "iniValid": self._extrair_texto_json(atual, "iniValid") or ide_cargo_data.get("iniValid", ""),
                        "fimValid": self._extrair_texto_json(atual, "fimValid") or ide_cargo_data.get("fimValid", ""),
                        "observacao": self._extrair_texto_json(atual, "observacao")
                    }
                    
                    # Adicionar apenas se tiver código ou nome do cargo
                    if cargo.get("codCargo") or cargo.get("nmCargo"):
                        cargos.append(cargo)
        
        except Exception as e:
            print(f"[Mapeador] Erro ao extrair cargos: {e}")
            
        return cargos

    def extrair_afastamentos(self, json_data: str) -> List[dict]:
        """
        Extrai todos os afastamentos do JSON do eSocial (S-2230).
        Retorna uma lista de dicts, cada um representando um afastamento com todos os campos necessários.
        """
        afastamentos = []
        try:
            dados = json.loads(json_data) if isinstance(json_data, str) else json_data
            ini = dados.get("iniAfastamento", {})
            fim = dados.get("fimAfastamento", {})
            # Extract all mapped fields for 08_CONVAFASTAMENTO
            afastamentos.append({
                "1 A-ID do empregador": dados.get("cnpj_empregador", ""),
                "2-Nome do trabalhador": dados.get("cpf_trabalhador", ""),
                "3-Código do contrato": dados.get("matricula", ""),
                "4-Código do motivo de afastamento": ini.get("codMotAfast", {}).get("_text", ""),
                "5-Data inicial de afastamento": ini.get("dtIniAfast", {}).get("_text", ""),
                "6-Data final de afastamento": fim.get("dtTermAfast", {}).get("_text", ""),
                "7-Observações do afastamento": ini.get("observacao", {}).get("_text", ""),
                "8-Descrição do motivo de afastamento": dados.get("descricao_motivo", ""),
                "9-Mesmo motivo anterior": ini.get("infoMesmoMtv", {}).get("_text", ""),
                "10-Tipo acidente trânsito": ini.get("tpAcidTransito", {}).get("_text", ""),
                "11-Período aquisitivo início": ini.get("perAquis", {}).get("dtInicio", {}).get("_text", ""),
                "12-Período aquisitivo fim": ini.get("perAquis", {}).get("dtFim", {}).get("_text", ""),
                "13-Cessão CNPJ": ini.get("infoCessao", {}).get("cnpjCess", {}).get("_text", ""),
                "14-Cessão ônus": ini.get("infoCessao", {}).get("infOnus", {}).get("_text", ""),
                "15-Mandato sindical CNPJ": ini.get("infoMandSind", {}).get("cnpjSind", {}).get("_text", ""),
                "16-Mandato sindical ônus remuneração": ini.get("infoMandSind", {}).get("infOnusRemun", {}).get("_text", ""),
                "17-Mandato eletivo CNPJ": ini.get("infoMandElet", {}).get("cnpjMandElet", {}).get("_text", ""),
                "18-Mandato eletivo remuneração cargo": ini.get("infoMandElet", {}).get("indRemunCargo", {}).get("_text", ""),
                "19-Retificação origem": dados.get("infoRetif", {}).get("origRetif", {}).get("_text", ""),
                "20-Retificação tipo processo": dados.get("infoRetif", {}).get("tpProc", {}).get("_text", ""),
                "21-Retificação número processo": dados.get("infoRetif", {}).get("nrProc", {}).get("_text", "")
            })
        except Exception as e:
            print(f"[Mapeador] Erro ao extrair afastamentos: {e}")
        return afastamentos
    
    def validar_campos_obrigatorios(self, template: str, registro_bd: Dict[str, Any]) -> List[str]:
        """
        Valida campos obrigatórios de um template
        
        Args:
            template: Nome do template
            registro_bd: Registro do banco de dados
            
        Returns:
            Lista com nomes dos campos obrigatórios ausentes
        """
        campos_ausentes = []
        
        if template not in self.mapeamentos:
            return campos_ausentes
            
        mapeamento = self.mapeamentos[template]
        
        for campo, definicao in mapeamento.get("campos", {}).items():
            if definicao.get("obrigatorio", False):
                valor = self.obter_valor_campo(template, campo, registro_bd)
                if valor is None or (isinstance(valor, str) and not valor.strip()):
                    campos_ausentes.append(campo)
                    
        return campos_ausentes
    
    def formatar_valor(self, valor: Any, definicao_campo: Dict[str, Any]) -> Any:
        """
        Formata um valor de acordo com a definição do campo (padrão Empresa: datas DD/MM/YYYY, números 2 casas e vírgula)
        """
        if valor is None:
            return None
        tipo = definicao_campo.get("tipo", "string")
        formato = definicao_campo.get("formato")
        from datetime import datetime
        try:
            if tipo == "string":
                return str(valor) if valor is not None else None
            elif tipo == "decimal":
                # Sempre retorna string com 2 casas e vírgula
                try:
                    f = float(str(valor).replace(",", "."))
                    return f"{f:.2f}".replace(".", ",")
                except Exception:
                    return valor
            elif tipo == "data":
                if isinstance(valor, str) and valor:
                    formatos_entrada = ["%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%dT%H:%M:%S"]
                    for fmt_entrada in formatos_entrada:
                        try:
                            dt = datetime.strptime(valor.split("T")[0], fmt_entrada)
                            return dt.strftime("%d/%m/%Y")
                        except ValueError:
                            continue
                return valor
            elif tipo == "datetime":
                if isinstance(valor, str) and valor:
                    try:
                        if "T" in valor:
                            dt = datetime.fromisoformat(valor.replace("Z", "+00:00"))
                        else:
                            dt = datetime.strptime(valor, "%Y-%m-%d %H:%M:%S")
                        return dt.strftime("%d/%m/%Y")
                    except ValueError:
                        pass
                return valor
            else:
                return valor
        except (ValueError, TypeError, AttributeError):
            return valor
    
    def obter_valor_campo_formatado(self, template: str, campo: str, registro_bd: Dict[str, Any]) -> Any:
        """
        Obtém e formata o valor de um campo específico do template
        
        Args:
            template: Nome do template
            campo: Nome do campo no template
            registro_bd: Registro do banco de dados
            
        Returns:
            Valor do campo formatado ou None se não encontrado
        """
        if template not in self.mapeamentos:
            return None
            
        mapeamento_template = self.mapeamentos[template]
        if campo not in mapeamento_template["campos"]:
            return None
            
        definicao_campo = mapeamento_template["campos"][campo]
        valor = self.obter_valor_campo(template, campo, registro_bd)
        
        return self.formatar_valor(valor, definicao_campo)
    
    def extrair_rubricas(self, json_data: str) -> List[dict]:
        """
        Extrai todas as rubricas do JSON do eSocial (S-1200).
        Retorna uma lista de dicts, cada um representando uma rubrica.
        """
        rubricas = []
        try:
            dados = json.loads(json_data) if isinstance(json_data, str) else json_data
            
            # Extrair dados básicos que serão usados em todas as rubricas
            evt_remun = dados.get("evtRemun", {})
            periodo_apuracao = evt_remun.get("ideEvento", {}).get("perApur", {}).get("_text", "")
            cpf_trab = evt_remun.get("ideTrabalhador", {}).get("cpfTrab", {}).get("_text", "")
            cnpj_empregador = evt_remun.get("ideEmpregador", {}).get("nrInsc", {}).get("_text", "")
            
            dm_dev = evt_remun.get("dmDev", [])
            if isinstance(dm_dev, dict):
                dm_dev = [dm_dev]
                
            for dm in dm_dev:
                # Dados do demonstrativo
                ide_dm_dev = dm.get("ideDmDev", {}).get("_text", "")
                cod_categ = dm.get("codCateg", {}).get("_text", "")
                
                # infoPerApur
                info_per_apur = dm.get("infoPerApur", {})
                if isinstance(info_per_apur, list):
                    info_per_apur = info_per_apur[0] if info_per_apur else {}
                    
                ide_estab_lot = info_per_apur.get("ideEstabLot", [])
                if isinstance(ide_estab_lot, dict):
                    ide_estab_lot = [ide_estab_lot]
                    
                for estab in ide_estab_lot:
                    nr_insc_estab = estab.get("nrInsc", {}).get("_text", "")
                    cod_lotacao = estab.get("codLotacao", {}).get("_text", "")
                    
                    remun_per_apur = estab.get("remunPerApur", [])
                    if isinstance(remun_per_apur, dict):
                        remun_per_apur = [remun_per_apur]
                        
                    for remun in remun_per_apur:
                        matricula = remun.get("matricula", {}).get("_text", "")
                        
                        # Processar rubricas (itens de remuneração)
                        itens_remun = remun.get("itensRemun", [])
                        if isinstance(itens_remun, dict):
                            itens_remun = [itens_remun]
                            
                        for item in itens_remun:
                            if item:
                                # Adaptar os nomes dos campos para compatibilizar com o mapeamento
                                item_completo = {
                                    "cpfTrab": cpf_trab,
                                    "perApur": periodo_apuracao,
                                    "ideDmDev": ide_dm_dev,
                                    "codCateg": cod_categ,
                                    "nrInscEstab": nr_insc_estab,
                                    "codLotacao": cod_lotacao,
                                    "matricula": matricula,
                                    # Mapear campos específicos das rubricas 
                                    # Usar cod como codRubr pois é o campo correto no S-1200
                                    "codRubr": item.get("cod", {}).get("_text", ""),
                                    "cod": item.get("cod", {}).get("_text", ""),  # Manter o campo original também
                                    "vrRubr": item.get("vrRubr", {}).get("_text", "0"),
                                    "ideTabRubr": item.get("ideTabRubr", {}).get("_text", "") or item.get("cod", {}).get("_text", ""),
                                    "qtdRubr": item.get("qtdRubr", {}).get("_text", ""),
                                    "fatorRubr": item.get("fatorRubr", {}).get("_text", ""),
                                    "vrUnit": item.get("vrUnit", {}).get("_text", "")
                                }
                                rubricas.append(item_completo)
        except Exception as e:
            print(f"[Mapeador] Erro ao extrair rubricas: {e}")
        return rubricas
    
    def validar_valores_validos(self, template: str, campo: str, valor: Any) -> bool:
        """
        Valida se um valor está dentro dos valores válidos para um campo
        
        Args:
            template: Nome do template
            campo: Nome do campo
            valor: Valor a ser validado
            
        Returns:
            True se o valor é válido
        """
        if template not in self.mapeamentos:
            return True
            
        mapeamento_template = self.mapeamentos[template]
        if campo not in mapeamento_template["campos"]:
            return True
            
        definicao_campo = mapeamento_template["campos"][campo]
        valores_validos = definicao_campo.get("valores_validos")
        
        if valores_validos and valor is not None:
            return str(valor) in valores_validos
            
        return True
    
    def obter_estatisticas_mapeamento(self, template: str) -> Dict[str, Any]:
        """
        Obtém estatísticas sobre o mapeamento de um template
        
        Args:
            template: Nome do template
            
        Returns:
            Dicionário com estatísticas do mapeamento
        """
        if template not in self.mapeamentos:
            return {}
            
        mapeamento = self.mapeamentos[template]
        campos = mapeamento.get("campos", {})
        
        stats = {
            "total_campos": len(campos),
            "campos_obrigatorios": len([c for c in campos.values() if c.get("obrigatorio", False)]),
            "campos_com_json_path": len([c for c in campos.values() if "caminho_json" in c]),
            "campos_com_validacao": len([c for c in campos.values() if "valores_validos" in c]),
            "tipos_de_dados": {}
        }
        
        # Contar tipos de dados
        for campo in campos.values():
            tipo = campo.get("tipo", "string")
            stats["tipos_de_dados"][tipo] = stats["tipos_de_dados"].get(tipo, 0) + 1
            
        return stats
    
    def validar_estrutura_xml(self, json_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Valida a estrutura do XML convertido para JSON
        
        Args:
            json_data: Dados JSON convertidos do XML
            
        Returns:
            Dicionário com avisos e erros encontrados
        """
        resultado = {
            "avisos": [],
            "erros": []
        }
        
        # Verifica estrutura básica do eSocial
        if "eSocial" not in json_data:
            resultado["erros"].append("Estrutura raiz 'eSocial' não encontrada")
            return resultado
            
        esocial = json_data["eSocial"]
        
        # Verifica eventos suportados
        eventos_suportados = [
            "evtInfoEmpregador", "evtTabEstab", "evtAdmissao", 
            "evtAltCadastral", "evtDesligamento", "evtDependente",
            "evtAfastTemp", "evtAtestMed", "evtFechaEvPer"
        ]
        
        eventos_encontrados = []
        for evento in eventos_suportados:
            if self._buscar_no_json(esocial, [evento]):
                eventos_encontrados.append(evento)
                
        if not eventos_encontrados:
            resultado["avisos"].append("Nenhum evento eSocial reconhecido encontrado")
        else:
            resultado["avisos"].append(f"Eventos encontrados: {', '.join(eventos_encontrados)}")
            
        return resultado
    
    def extrair_rubricas_folha(self, json_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extrai rubricas de folha de pagamento do JSON
        
        Args:
            json_data: Dados JSON do eSocial
            
        Returns:
            Lista de rubricas encontradas
        """
        rubricas = []
        
        # Busca rubricas em diferentes eventos
        caminhos_rubricas = [
            ["evtFechaEvPer", "ideVinculo", "infoFechamento", "remunPerApur", "itensRemun"],
            ["evtFechaEvPer", "ideVinculo", "infoFechamento", "remunPerAnt", "itensRemun"],
            ["evtRemun", "dmDev", "infoPerApur", "ideEstabLot", "remunPerApur", "itensRemun"]
        ]
        
        for caminho in caminhos_rubricas:
            itens = self._buscar_no_json(json_data, caminho)
            if isinstance(itens, list):
                for item in itens:
                    if isinstance(item, dict):
                        rubrica = {
                            "codigo": item.get("codRubr", {}).get("_text", ""),
                            "descricao": item.get("ideRubr", {}).get("_text", ""),
                            "valor": self._extrair_valor_numerico(item.get("vrRubr", {}).get("_text", "0"))
                        }
                        if rubrica["codigo"]:
                            rubricas.append(rubrica)
            elif isinstance(itens, dict):
                rubrica = {
                    "codigo": itens.get("codRubr", {}).get("_text", ""),
                    "descricao": itens.get("ideRubr", {}).get("_text", ""),
                    "valor": self._extrair_valor_numerico(itens.get("vrRubr", {}).get("_text", "0"))
                }
                if rubrica["codigo"]:
                    rubricas.append(rubrica)
                    
        return rubricas
    
    def _buscar_no_json(self, json_data, caminho: List[str]):
        """
        Busca recursivamente um caminho em um dicionário (ou string JSON).
        Retorna o valor encontrado ou [] se não existir.
        """
        if isinstance(json_data, str):
            try:
                obj = json.loads(json_data)
            except Exception:
                return []
        else:
            obj = json_data
        atual = obj
        for chave in caminho:
            if isinstance(atual, dict) and chave in atual:
                atual = atual[chave]
            else:
                return []
        return atual
    
    def gerar_relatorio_mapeamento(self, template: str) -> str:
        """
        Gera relatório detalhado sobre o mapeamento de um template
        
        Args:
            template: Nome do template
            
        Returns:
            Relatório em formato texto
        """
        if template not in self.mapeamentos:
            return f"Template '{template}' não encontrado"
            
        mapeamento = self.mapeamentos[template]
        stats = self.obter_estatisticas_mapeamento(template)
        
        relatorio = []
        relatorio.append(f"=== RELATÓRIO DE MAPEAMENTO: {template} ===")
        relatorio.append(f"Fonte principal: {mapeamento.get('fonte_principal', 'N/A')}")
        relatorio.append(f"Fontes adicionais: {', '.join(mapeamento.get('fontes_adicionais', []))}")
        relatorio.append("")
        
        relatorio.append("=== ESTATÍSTICAS ===")
        relatorio.append(f"Total de campos: {stats['total_campos']}")
        relatorio.append(f"Campos obrigatórios: {stats['campos_obrigatorios']}")
        relatorio.append(f"Campos com JSON path: {stats['campos_com_json_path']}")
        relatorio.append(f"Campos com validação: {stats['campos_com_validacao']}")
        relatorio.append("")
        
        relatorio.append("=== TIPOS DE DADOS ===")
        for tipo, count in stats['tipos_de_dados'].items():
            relatorio.append(f"{tipo}: {count} campos")
        relatorio.append("")
        
        relatorio.append("=== CAMPOS OBRIGATÓRIOS ===")
        campos = mapeamento.get("campos", {})
        obrigatorios = [nome for nome, def_campo in campos.items() if def_campo.get("obrigatorio", False)]
        for campo in obrigatorios:
            relatorio.append(f"- {campo}")
        relatorio.append("")
        
        relatorio.append("=== CAMPOS SEM JSON PATH ===")
        sem_path = [nome for nome, def_campo in campos.items() if "caminho_json" not in def_campo]
        for campo in sem_path:
            relatorio.append(f"- {campo}: {campos[campo].get('origem', 'N/A')}")
        
        return "\n".join(relatorio)
    
    def _extrair_valor_numerico(self, valor: str) -> float:
        """
        Extrai valor numérico de string, tratando formatos brasileiros
        
        Args:
            valor: String com valor
            
        Returns:
            Valor numérico
        """
        if not valor:
            return 0.0
            
        # Remove espaços e caracteres não numéricos exceto vírgula e ponto
        valor_limpo = ''.join(c for c in str(valor) if c.isdigit() or c in '.,')
        
        # Trata formato brasileiro (vírgula como decimal)
        if ',' in valor_limpo and '.' in valor_limpo:
            # Se tem ambos, assume formato brasileiro: 1.234,56
            valor_limpo = valor_limpo.replace('.', '').replace(',', '.')
        elif ',' in valor_limpo:
            # Se só tem vírgula, pode ser decimal brasileiro
            partes = valor_limpo.split(',')
            if len(partes) == 2 and len(partes[1]) <= 2:
                valor_limpo = valor_limpo.replace(',', '.')
                
        try:
            return float(valor_limpo)
        except ValueError:
            return 0.0
