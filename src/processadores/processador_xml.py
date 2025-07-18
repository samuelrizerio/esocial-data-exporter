"""
Processador de arquivos XML do eSocial
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import xml.etree.ElementTree as ET
import json
from datetime import datetime
from tqdm import tqdm

from utils.validador_dados import ValidadorDados

# Base de namespaces do eSocial - versão agnóstica
NAMESPACE_BASE = 'http://www.esocial.gov.br/schema/evt'

# Padrões de eventos eSocial independentes de versão
ESOCIAL_EVENT_PATTERNS = {
    'evtTabLotacao': 'S-1020', 
    'evtTabCargo': 'S-1030',
    'evtRemun': 'S-1200',
    'evtAdmissao': 'S-2200',
    'evtAltCadastral': 'S-2205',
    'evtAltContratual': 'S-2206',
    'evtAfastTemp': 'S-2230'
}

def extrair_namespace_dinamico(root):
    """
    Extrai o namespace de um elemento XML de forma dinâmica
    
    Args:
        root: Elemento raiz do XML
        
    Returns:
        String do namespace ou None se não encontrado
    """
    if root is None:
        return None
        
    # Verificar se o tag contém namespace
    if '}' in root.tag:
        namespace = root.tag.split('}')[0].strip('{')
        return namespace
    
    # Verificar nos atributos do elemento
    for attr_name, attr_value in root.attrib.items():
        if 'xmlns' in attr_name and 'esocial.gov.br' in attr_value:
            return attr_value
    
    # Procurar nos elementos filhos
    for child in root:
        if '}' in child.tag:
            namespace = child.tag.split('}')[0].strip('{')
            if 'esocial.gov.br' in namespace:
                return namespace
    
    return None

def obter_namespaces_dinamicos(root):
    """
    Obtém todos os namespaces de um elemento XML de forma dinâmica
    
    Args:
        root: Elemento raiz do XML
        
    Returns:
        Dicionário com namespaces encontrados
    """
    namespaces = {}
    
    if root is None:
        return namespaces
    
    # Extrair namespace principal
    namespace_principal = extrair_namespace_dinamico(root)
    if namespace_principal:
        namespaces['default'] = namespace_principal
        namespaces['es'] = namespace_principal
    
    # Adicionar namespaces padrão
    namespaces.update({
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        'xsd': 'http://www.w3.org/2001/XMLSchema'
    })
    
    return namespaces

def encontrar_elemento(root, nome_elemento, usar_namespace_dinamico=True):
    """
    Busca um elemento considerando namespaces de forma dinâmica
    
    Args:
        root: Elemento raiz para buscar
        nome_elemento: Nome do elemento a ser encontrado
        usar_namespace_dinamico: Se True, detecta namespaces automaticamente
    
    Returns:
        Elemento encontrado ou None
    """
    if root is None:
        return None
        
    # Primeiro, tentar encontrar diretamente (sem namespace)
    try:
        elem = root.find(f".//{nome_elemento}")
        if elem is not None:
            return elem
    except Exception:
        pass
    
    if usar_namespace_dinamico:
        # Extrair namespace do elemento raiz
        namespace = extrair_namespace_dinamico(root)
        if namespace:
            try:
                elem = root.find(f".//{{{namespace}}}{nome_elemento}")
                if elem is not None:
                    return elem
            except Exception:
                pass
    
    return None

def encontrar_todos_elementos(root, nome_elemento, usar_namespace_dinamico=True):
    """
    Busca todos os elementos de um tipo considerando namespaces de forma dinâmica
    
    Args:
        root: Elemento raiz para buscar
        nome_elemento: Nome do elemento a ser encontrado
        usar_namespace_dinamico: Se True, detecta namespaces automaticamente
    
    Returns:
        Lista de elementos encontrados
    """
    resultados = []
    
    if root is None:
        return resultados
        
    # Tenta encontrar diretamente
    try:
        elems = root.findall(f".//{nome_elemento}")
        if elems:
            return elems
    except Exception:
        pass
    
    if usar_namespace_dinamico:
        # Obter namespaces dinâmicos
        namespaces = obter_namespaces_dinamicos(root)
        
        # Tenta com diferentes namespaces
        for prefix, uri in namespaces.items():
            try:
                elems = root.findall(f".//{{{uri}}}{nome_elemento}")
                if elems:
                    return elems
            except Exception:
                pass
                
            try:
                elems = root.findall(f".//{prefix}:{nome_elemento}", namespaces)
                if elems:
                    return elems
            except Exception:
                pass
    
    return resultados

def obter_texto_elemento(root, nome_elemento, usar_namespace_dinamico=True):
    """
    Busca o texto de um elemento considerando namespaces
    
    Args:
        root: Elemento raiz para buscar
        nome_elemento: Nome do elemento a ser encontrado
        usar_namespace_dinamico: Se True, detecta namespaces automaticamente
        
    Returns:
        Texto do elemento ou string vazia
    """
    elemento = encontrar_elemento(root, nome_elemento, usar_namespace_dinamico)
    if elemento is not None and elemento.text:
        return elemento.text.strip()
    return ""

def extrair_tipo_evento(root):
    """
    Extrai o tipo de evento do XML
    
    Args:
        root: Elemento raiz do XML
        
    Returns:
        Tipo de evento (ex: evtTabLotacao) ou None
    """
    # Extrair do namespace
    if '}' in root.tag:
        namespace = root.tag.split('}')[0].strip('{')
        # Verificar se é um namespace do eSocial
        if 'esocial.gov.br' in namespace:
            # Extrair tipo de evento do namespace
            for evento in ESOCIAL_EVENT_PATTERNS.keys():
                if evento in namespace:
                    return evento
    
    # Verificar elementos filhos diretos
    for child in root:
        tag_name = child.tag
        if '}' in tag_name:
            tag_name = tag_name.split('}')[1]
        
        # Verificar se é um evento conhecido
        if tag_name in ESOCIAL_EVENT_PATTERNS:
            return tag_name
    
    # Verificar atributos
    for attr, value in root.attrib.items():
        if attr.endswith('type') or attr.endswith('Type'):
            if 'evt' in value:
                return value
    
    return None

def encontrar_primeiro_esocial(root):
    """
    Busca recursivamente o primeiro elemento <eSocial> em qualquer profundidade.
    Retorna o elemento encontrado ou None.
    """
    if root is None:
        return None
    if root.tag.endswith('eSocial') or root.tag.endswith('eSocial>'):
        return root
    for el in root.iter():
        if el.tag.endswith('eSocial') or el.tag.endswith('eSocial>'):
            return el
    return None

def identificar_layout(root):
    """
    Identifica o layout do eSocial, mesmo que o root não seja <eSocial>.
    
    Args:
        root: Elemento raiz do XML
        
    Returns:
        Código do layout (ex: S-1020) ou None
    """
    # NOVO: busca o primeiro <eSocial> se não for root
    esocial_elem = encontrar_primeiro_esocial(root)
    if esocial_elem is not None and esocial_elem is not root:
        root = esocial_elem
    mapeamento = ESOCIAL_EVENT_PATTERNS
    # Se o root for <eSocial>, procurar filhos
    if root.tag.endswith('eSocial'):
        for child in root:
            tag_name = child.tag
            if '}' in tag_name:
                tag_name = tag_name.split('}')[1]
            if tag_name in mapeamento:
                return mapeamento[tag_name]
    else:
        # Se o root já for um evento
        tag_name = root.tag
        if '}' in tag_name:
            tag_name = tag_name.split('}')[1]
        if tag_name in mapeamento:
            return mapeamento[tag_name]
    # Fallback: procurar recursivamente
    for el in root.iter():
        tag_name = el.tag
        if '}' in tag_name:
            tag_name = tag_name.split('}')[1]
        if tag_name in mapeamento:
            return mapeamento[tag_name]
    # NOVO: Se não encontrou, retorna o nome do primeiro evento eSocial encontrado (para layouts futuros)
    for el in root.iter():
        tag_name = el.tag
        if '}' in tag_name:
            tag_name = tag_name.split('}')[1]
        if tag_name.startswith('evt'):
            return tag_name  # Ex: evtTabRubrica, evtTSVInicio, etc.
    return None


class ProcessadorXML:
    """
    Classe para processamento de arquivos XML do eSocial
    """
    
    def __init__(self, gerenciador_bd, configuracoes):
        """
        Inicializa o processador XML
        
        Args:
            gerenciador_bd: Gerenciador de banco de dados
            configuracoes: Configurações da aplicação
        """
        self.gerenciador_bd = gerenciador_bd
        self.configuracoes = configuracoes
        self.logger = logging.getLogger(__name__)
        
        # Variáveis de controle
        self.arquivos_processados = 0
        self.arquivos_com_erro = 0
        
        # Inicializar processadores de layouts
        self._inicializar_processadores()
    
    def _inicializar_processadores(self):
        """Inicializa os processadores para cada layout suportado"""
        self.processadores = {
            'S-1020': self._processar_s1020,
            'S-1030': self._processar_s1030,
            'S-1200': self._processar_s1200,
            'S-2200': self._processar_s2200,
            'S-2205': self._processar_s2205,
            'S-2206': self._processar_s2206,
            'S-2230': self._processar_s2230
        }
        
        # Layouts obrigatorios que devem estar presentes
        self.layouts_obrigatorios = list(self.processadores.keys())
    
    def processar_arquivo(self, caminho_arquivo: str) -> bool:
        """
        Processa um arquivo XML individual - método público
        
        Args:
            caminho_arquivo: Caminho do arquivo XML como string
            
        Returns:
            True se o processamento foi bem-sucedido, False caso contrário
        """
        self.logger.info(f"Processando arquivo XML: {caminho_arquivo}")
        return self._processar_arquivo(Path(caminho_arquivo))
    
    def processar_diretorio(self, caminho_diretorio: Path) -> int:
        """
        Processa todos os arquivos XML em um diretório
        
        Args:
            caminho_diretorio: Caminho do diretório com arquivos XML
            
        Returns:
            Número de arquivos processados com sucesso
        """
        self.logger.info(f"Processando arquivos XML em: {caminho_diretorio}")
        
        # Resetar contadores
        self.arquivos_processados = 0
        self.arquivos_com_erro = 0
        
        # Criar contadores por tipo de layout para verificar layouts obrigatórios
        layouts_encontrados = {layout: 0 for layout in self.layouts_obrigatorios}
        
        # Encontrar todos os arquivos XML
        arquivos_xml = list(caminho_diretorio.glob('**/*.xml'))
        total_arquivos = len(arquivos_xml)
        self.logger.info(f"Encontrados {total_arquivos} arquivos XML")
        if total_arquivos == 0:
            return 0
        
        # Filtro: aceitar arquivos cujo nome contenha S2200, S-2200, S_2200, etc. para cada layout suportado
        def gera_variacoes(layout):
            base = layout.replace('S-', 'S') if layout.startswith('S-') else layout
            return [base, base.replace('S', 'S-'), base.replace('S', 'S_')]
        # Definir explicitamente os 7 layouts suportados
        layouts_suportados = ['S-1020', 'S-1030', 'S-1200', 'S-2200', 'S-2205', 'S-2206', 'S-2230']
        padroes = []
        for layout in layouts_suportados:
            padroes.extend(gera_variacoes(layout))
        arquivos_suportados = [arq for arq in arquivos_xml if any(pat.lower() in arq.name.lower() for pat in padroes)]
        self.logger.info(f"Arquivos suportados: {len(arquivos_suportados)}")
        if len(arquivos_suportados) == 0:
            self.logger.warning("Nenhum arquivo suportado encontrado pelo padrão de nome.")
            return 0
        
        # Processar todos os arquivos suportados com barra de progresso
        for caminho_arquivo in tqdm(arquivos_suportados, desc="Processando arquivos XML", unit="arquivo"):
            resultado = self._processar_arquivo(caminho_arquivo)
            if resultado and caminho_arquivo:
                try:
                    tree = ET.parse(caminho_arquivo)
                    root = tree.getroot()
                    layout = identificar_layout(root)
                    if layout in layouts_encontrados:
                        layouts_encontrados[layout] += 1
                except:
                    pass
        layouts_faltando = [layout for layout, count in layouts_encontrados.items() if count == 0]
        if layouts_faltando:
            self.logger.warning(f"ATENÇÃO: Os seguintes layouts obrigatórios não foram encontrados: {', '.join(layouts_faltando)}")
        self.logger.info(f"Processamento concluído: {self.arquivos_processados} arquivos processados, "
                       f"{self.arquivos_com_erro} arquivos com erro")
        for layout, count in layouts_encontrados.items():
            self.logger.info(f"  {layout}: {count} arquivos")
        return self.arquivos_processados
    
    def _processar_arquivo(self, caminho_arquivo: Path) -> bool:
        """
        Processa um arquivo XML individual
        
        Args:
            caminho_arquivo: Caminho do arquivo XML
        
        Returns:
            True se o processamento foi bem-sucedido, False caso contrário
        """
        # Verificar se o arquivo existe
        if not caminho_arquivo.exists():
            self.logger.error(f"Arquivo não encontrado: {caminho_arquivo}")
            self.arquivos_com_erro += 1
            return False
        
        # Verificar tamanho mínimo do arquivo
        if caminho_arquivo.stat().st_size < 50:  # Menos de 50 bytes provavelmente está vazio ou corrompido
            self.logger.error(f"Arquivo XML muito pequeno ou vazio: {caminho_arquivo} ({caminho_arquivo.stat().st_size} bytes)")
            self.arquivos_com_erro += 1
            return False
        
        try:
            # Tentar carregar XML diretamente - mais eficiente que validar conteúdo primeiro
            try:
                tree = ET.parse(caminho_arquivo)
                root = tree.getroot()
            except ET.ParseError as e:
                self.logger.error(f"Erro ao analisar XML: {caminho_arquivo}: {e}")
                self.arquivos_com_erro += 1
                return False
            except UnicodeDecodeError:
                # Tentar com encoding alternativo apenas se necessário
                try:
                    tree = ET.parse(caminho_arquivo, parser=ET.XMLParser(encoding='latin-1'))
                    root = tree.getroot()
                except Exception as e:
                    self.logger.error(f"Erro ao ler arquivo XML (problema de codificação): {caminho_arquivo}: {e}")
                    self.arquivos_com_erro += 1
                    return False
            except Exception as e:
                self.logger.error(f"Erro desconhecido ao carregar XML: {caminho_arquivo}: {e}")
                self.arquivos_com_erro += 1
                return False
            
            # --- NOVO: iterar sobre todos os eventos filhos de <eSocial> ---
            if root.tag.endswith('eSocial'):
                sucesso = True
                for evento in list(root):
                    layout = identificar_layout(evento)
                    if not layout:
                        self.logger.warning(f"Layout não identificado para evento em {caminho_arquivo.name}")
                        continue
                    if layout not in self.processadores:
                        self.logger.warning(f"Layout não suportado: {layout} para {caminho_arquivo.name}")
                        continue
                    processador = self.processadores[layout]
                    resultado = processador(evento, caminho_arquivo)
                    if resultado:
                        self.arquivos_processados += 1
                    else:
                        self.arquivos_com_erro += 1
                        sucesso = False
                return sucesso
            # --- FIM NOVO ---
            
            # Identificar o layout normalmente para arquivos de evento único
            codigo_layout = identificar_layout(root)
            if not codigo_layout:
                self.logger.warning(f"Layout não identificado para {caminho_arquivo.name}")
                self.arquivos_com_erro += 1
                return False
                
            if codigo_layout not in self.processadores:
                self.logger.warning(f"Layout não suportado: {codigo_layout} para {caminho_arquivo.name}")
                self.arquivos_com_erro += 1
                return False
                
            processador = self.processadores[codigo_layout]
            resultado = processador(root, caminho_arquivo)
            if resultado:
                self.arquivos_processados += 1
                return True
            else:
                self.arquivos_com_erro += 1
                return False
                
        except Exception as e:
            self.logger.error(f"Erro ao processar arquivo {caminho_arquivo}: {e}")
            self.arquivos_com_erro += 1
            return False
    
    # Implementações dos processadores específicos para cada layout
    
    def _processar_s1020(self, root, caminho_arquivo):
        """Processa arquivo XML do layout S-1020 (Tabela de Lotações Tributárias) - 100% Coverage"""
        try:
            # Extrair CNPJ do empregador
            ide_empregador = encontrar_elemento(root, "ideEmpregador")
            cnpj_empregador = obter_texto_elemento(ide_empregador, "nrInsc") if ide_empregador else ""
            
            # Encontrar as lotações no XML
            lotacoes_list = []
            
            # Buscar inclusao, alteracao e exclusao
            info_lotacao = encontrar_elemento(root, "infoLotacao")
            if info_lotacao is not None:
                for bloco in ["inclusao", "alteracao", "exclusao"]:
                    for evento in encontrar_todos_elementos(info_lotacao, bloco):
                        ide_lotacao = encontrar_elemento(evento, "ideLotacao")
                        dados_lotacao = encontrar_elemento(evento, "dadosLotacao") if bloco != "exclusao" else None
                        nova_validade = encontrar_elemento(evento, "novaValidade") if bloco == "alteracao" else None

                        # ideLotacao
                        cod_lotacao = obter_texto_elemento(ide_lotacao, "codLotacao") if ide_lotacao else ""
                        ini_valid = obter_texto_elemento(ide_lotacao, "iniValid") if ide_lotacao else ""
                        fim_valid = obter_texto_elemento(ide_lotacao, "fimValid") if ide_lotacao else ""

                        # novaValidade (only for alteracao)
                        nova_ini_valid = obter_texto_elemento(nova_validade, "iniValid") if nova_validade else ""
                        nova_fim_valid = obter_texto_elemento(nova_validade, "fimValid") if nova_validade else ""

                        # dadosLotacao
                        tipo_lotacao = obter_texto_elemento(dados_lotacao, "tpLotacao") if dados_lotacao else ""
                        tipo_inscricao = obter_texto_elemento(dados_lotacao, "tpInsc") if dados_lotacao else ""
                        nr_inscricao = obter_texto_elemento(dados_lotacao, "nrInsc") if dados_lotacao else ""
                        desc_lotacao = obter_texto_elemento(dados_lotacao, "descLotacao") if dados_lotacao else ""

                        # fpasLotacao
                        fpas_lotacao = encontrar_elemento(dados_lotacao, "fpasLotacao") if dados_lotacao else None
                        fpas = obter_texto_elemento(fpas_lotacao, "fpas") if fpas_lotacao else ""
                        cod_tercs = obter_texto_elemento(fpas_lotacao, "codTercs") if fpas_lotacao else ""
                        cod_tercs_susp = obter_texto_elemento(fpas_lotacao, "codTercsSusp") if fpas_lotacao else ""
                        
                        # infoProcJudTerceiros
                        info_proc_jud_terceiros = encontrar_elemento(fpas_lotacao, "infoProcJudTerceiros") if fpas_lotacao else None
                        proc_jud_terceiros_cod_susp = obter_texto_elemento(info_proc_jud_terceiros, "codSusp") if info_proc_jud_terceiros else ""
                        proc_jud_terceiros_cod_terc = obter_texto_elemento(info_proc_jud_terceiros, "codTerc") if info_proc_jud_terceiros else ""
                        proc_jud_terceiros_nr_proc_jud = obter_texto_elemento(info_proc_jud_terceiros, "nrProcJud") if info_proc_jud_terceiros else ""
                        
                        # procJudTerceiro
                        proc_jud_terceiro = encontrar_elemento(info_proc_jud_terceiros, "procJudTerceiro") if info_proc_jud_terceiros else None
                        proc_jud_terceiro_cod_susp = obter_texto_elemento(proc_jud_terceiro, "codSusp") if proc_jud_terceiro else ""
                        proc_jud_terceiro_cod_terc = obter_texto_elemento(proc_jud_terceiro, "codTerc") if proc_jud_terceiro else ""
                        proc_jud_terceiro_nr_proc_jud = obter_texto_elemento(proc_jud_terceiro, "nrProcJud") if proc_jud_terceiro else ""

                        # infoEmprParcial
                        info_empr_parcial = encontrar_elemento(dados_lotacao, "infoEmprParcial") if dados_lotacao else None
                        tp_insc_contrat = obter_texto_elemento(info_empr_parcial, "tpInscContrat") if info_empr_parcial else ""
                        nr_insc_contrat = obter_texto_elemento(info_empr_parcial, "nrInscContrat") if info_empr_parcial else ""
                        tp_insc_prop = obter_texto_elemento(info_empr_parcial, "tpInscProp") if info_empr_parcial else ""
                        nr_insc_prop = obter_texto_elemento(info_empr_parcial, "nrInscProp") if info_empr_parcial else ""

                        # dadosOpPort
                        dados_op_port = encontrar_elemento(dados_lotacao, "dadosOpPort") if dados_lotacao else None
                        aliq_rat = obter_texto_elemento(dados_op_port, "aliqRat") if dados_op_port else ""
                        fap = obter_texto_elemento(dados_op_port, "fap") if dados_op_port else ""

                        # Montar dicionário com TODOS os dados (100% coverage)
                        lotacao_dict = {
                            # Identificação
                            'codigo': cod_lotacao,
                            'cod_lotacao': cod_lotacao,
                            'descricao': ini_valid,
                            'desc_lotacao': desc_lotacao,
                            'tipo_lotacao': tipo_lotacao,
                            'tipo_inscricao': tipo_inscricao,
                            'nr_inscricao': nr_inscricao,
                            
                            # Validade
                            'inicio_validade': ini_valid,
                            'fim_validade': fim_valid,
                            'nova_ini_valid': nova_ini_valid,
                            'nova_fim_valid': nova_fim_valid,
                            
                            # FPAS
                            'fpas': fpas,
                            'cod_tercs': cod_tercs,
                            'cod_tercs_susp': cod_tercs_susp,
                            
                            # Processo Judicial Terceiros
                            'proc_jud_terceiros_cod_susp': proc_jud_terceiros_cod_susp,
                            'proc_jud_terceiros_cod_terc': proc_jud_terceiros_cod_terc,
                            'proc_jud_terceiros_nr_proc_jud': proc_jud_terceiros_nr_proc_jud,
                            'proc_jud_terceiro_cod_susp': proc_jud_terceiro_cod_susp,
                            'proc_jud_terceiro_cod_terc': proc_jud_terceiro_cod_terc,
                            'proc_jud_terceiro_nr_proc_jud': proc_jud_terceiro_nr_proc_jud,
                            
                            # Empresa Parcial
                            'tp_insc_contrat': tp_insc_contrat,
                            'nr_insc_contrat': nr_insc_contrat,
                            'tp_insc_prop': tp_insc_prop,
                            'nr_insc_prop': nr_insc_prop,
                            
                            # Dados Operacionais
                            'aliq_rat': aliq_rat,
                            'fap': fap,
                            
                            # Dados do empregador
                            'cnpj_empregador': cnpj_empregador,
                            
                            # JSON completo para análise
                            'json_data': json.dumps(self._elemento_para_dict(evento))
                        }
                        lotacoes_list.append(lotacao_dict)

            # Validar e sanitizar dados antes de inserir
            lotacoes_validadas = []
            for lotacao_dict in lotacoes_list:
                # Validar dados da lotação
                valido, mensagens_erro = ValidadorDados.validar_registro_s1020(lotacao_dict)
                if not valido:
                    for erro in mensagens_erro:
                        self.logger.warning(f"Validação para lotação {lotacao_dict.get('codigo')}, arquivo {caminho_arquivo}: {erro}")
                    
                    # Tentar corrigir dados problemáticos
                    lotacao_dict = ValidadorDados.sanitizar_dados(lotacao_dict, 'S-1020')
                    
                    # Revalidar após correções
                    valido, mensagens_erro = ValidadorDados.validar_registro_s1020(lotacao_dict)
                    if not valido:
                        self.logger.warning(f"Dados ainda apresentam problemas após correções: {', '.join(mensagens_erro)}")
                    else:
                        self.logger.info(f"Dados corrigidos com sucesso para lotação {lotacao_dict.get('codigo')}")
                
                lotacoes_validadas.append(lotacao_dict)
                
            # Inserir no banco de dados
            if lotacoes_validadas:
                self.gerenciador_bd.inserir_dados("esocial_s1020", lotacoes_validadas)
                return True
                
            return False
        except Exception as e:
            self.logger.error(f"Erro ao processar S-1020 {caminho_arquivo}: {e}", exc_info=True)
            return False
    
    def _processar_s1030(self, root, caminho_arquivo):
        """Processa arquivo XML do layout S-1030 (Tabela de Cargos) - 100% Coverage"""
        try:
            # Extrair dados do empregador
            ide_empregador = encontrar_elemento(root, "ideEmpregador")
            cnpj_empregador = obter_texto_elemento(ide_empregador, "nrInsc") if ide_empregador else ""
            tipo_inscricao = obter_texto_elemento(ide_empregador, "tpInsc") if ide_empregador else ""
            
            # Extrair dados do evento
            ide_evento = encontrar_elemento(root, "ideEvento")
            tipo_ambiente = obter_texto_elemento(ide_evento, "tpAmb") if ide_evento else ""
            processo_emissor = obter_texto_elemento(ide_evento, "procEmi") if ide_evento else ""
            versao_processo = obter_texto_elemento(ide_evento, "verProc") if ide_evento else ""
            
            cargos_list = []

            # Encontrar todos os blocos de inclusao, alteracao e exclusao
            info_cargo = encontrar_elemento(root, "infoCargo")
            if info_cargo is not None:
                for bloco in ["inclusao", "alteracao", "exclusao"]:
                    for evento in encontrar_todos_elementos(info_cargo, bloco):
                        ide_cargo = encontrar_elemento(evento, "ideCargo")
                        dados_cargo = encontrar_elemento(evento, "dadosCargo")
                        
                        if ide_cargo is not None:
                            # Dados de identificação do cargo
                            codigo = obter_texto_elemento(ide_cargo, "codCargo")
                            inicio_validade = obter_texto_elemento(ide_cargo, "iniValid")
                            fim_validade = obter_texto_elemento(ide_cargo, "fimValid")
                            
                            # Dados do cargo (apenas para inclusao e alteracao)
                            descricao = ""
                            cbo = ""
                            cargo_publico = ""
                            nivel_cargo = ""
                            desc_sumaria = ""
                            dt_criacao = ""
                            dt_extincao = ""
                            situacao = ""
                            permite_acumulo = ""
                            permite_contagem_esp = ""
                            dedicacao_exclusiva = ""
                            num_lei = ""
                            dt_lei = ""
                            situacao_lei = ""
                            tem_funcao = ""
                            
                            if dados_cargo is not None:
                                # Dados básicos do cargo
                                descricao = obter_texto_elemento(dados_cargo, "nmCargo")
                                cbo = obter_texto_elemento(dados_cargo, "codCBO")
                                cargo_publico = obter_texto_elemento(dados_cargo, "cargoPublico")
                                
                                # Dados complementares do cargo
                                nivel_cargo = obter_texto_elemento(dados_cargo, "nivelCargo")
                                desc_sumaria = obter_texto_elemento(dados_cargo, "descSumar")
                                dt_criacao = obter_texto_elemento(dados_cargo, "dtCriacao")
                                dt_extincao = obter_texto_elemento(dados_cargo, "dtExtincao")
                                situacao = obter_texto_elemento(dados_cargo, "situacao")
                                permite_acumulo = obter_texto_elemento(dados_cargo, "permiteAcumulo")
                                permite_contagem_esp = obter_texto_elemento(dados_cargo, "permiteContagemEspecial")
                                dedicacao_exclusiva = obter_texto_elemento(dados_cargo, "dedicacaoExclusiva")
                                num_lei = obter_texto_elemento(dados_cargo, "numLei")
                                dt_lei = obter_texto_elemento(dados_cargo, "dtLei")
                                situacao_lei = obter_texto_elemento(dados_cargo, "situacaoLei")
                                tem_funcao = obter_texto_elemento(dados_cargo, "temFuncao")
                            
                            cargo_dict = {
                                # Dados do evento
                                'tipo_ambiente': tipo_ambiente,
                                'processo_emissor': processo_emissor,
                                'versao_processo': versao_processo,
                                'tipo_inscricao': tipo_inscricao,
                                
                                # Dados de identificação do cargo
                                'codigo': codigo,
                                'inicio_validade': inicio_validade,
                                'fim_validade': fim_validade,
                                
                                # Dados básicos do cargo
                                'descricao': descricao,
                                'cbo': cbo,
                                'cargo_publico': cargo_publico,
                                
                                # Dados complementares do cargo
                                'nivel_cargo': nivel_cargo,
                                'desc_sumaria': desc_sumaria,
                                'dt_criacao': dt_criacao,
                                'dt_extincao': dt_extincao,
                                'situacao': situacao,
                                'permite_acumulo': permite_acumulo,
                                'permite_contagem_esp': permite_contagem_esp,
                                'dedicacao_exclusiva': dedicacao_exclusiva,
                                'num_lei': num_lei,
                                'dt_lei': dt_lei,
                                'situacao_lei': situacao_lei,
                                'tem_funcao': tem_funcao,
                                
                                # Dados do empregador
                                'cnpj_empregador': cnpj_empregador,
                                
                                # JSON completo para análise
                                'json_data': json.dumps(self._elemento_para_dict(evento))
                            }
                            cargos_list.append(cargo_dict)

            # Validar e sanitizar dados antes de inserir
            cargos_validados = []
            for cargo_dict in cargos_list:
                valido, mensagens_erro = ValidadorDados.validar_registro_s1030(cargo_dict)
                if not valido:
                    for erro in mensagens_erro:
                        self.logger.warning(f"Validação para cargo {cargo_dict.get('codigo')}, arquivo {caminho_arquivo}: {erro}")
                    cargo_dict = ValidadorDados.sanitizar_dados(cargo_dict, 'S-1030')
                    valido, mensagens_erro = ValidadorDados.validar_registro_s1030(cargo_dict)
                    if not valido:
                        self.logger.warning(f"Dados ainda apresentam problemas após correções: {', '.join(mensagens_erro)}")
                    else:
                        self.logger.info(f"Dados corrigidos com sucesso para cargo {cargo_dict.get('codigo')}")
                cargos_validados.append(cargo_dict)

            if cargos_validados:
                self.gerenciador_bd.inserir_dados("esocial_s1030", cargos_validados)
                return True
            return False
        except Exception as e:
            self.logger.error(f"Erro ao processar S-1030 {caminho_arquivo}: {e}", exc_info=True)
            return False
    
    def _processar_s1200(self, root, caminho_arquivo):
        """Processa arquivo XML do layout S-1200 (Remuneração do Trabalhador)"""
        try:
            # Extrair CNPJ do empregador
            ide_empregador = encontrar_elemento(root, "ideEmpregador")
            cnpj_empregador = obter_texto_elemento(ide_empregador, "nrInsc") if ide_empregador else ""
            
            # Extrair dados do período
            ide_evento = encontrar_elemento(root, "ideEvento")
            periodo_apuracao = obter_texto_elemento(ide_evento, "perApur") if ide_evento else ""
            
            # Extrair dados do trabalhador
            ide_trabalhador = encontrar_elemento(root, "ideTrabalhador")
            cpf_trabalhador = obter_texto_elemento(ide_trabalhador, "cpfTrab") if ide_trabalhador else ""
            
            # Buscar todas as remunerações
            remuneracoes_list = []
            
            # Processar demonstrativo de valores
            demonstrativos = encontrar_todos_elementos(root, "dmDev")
            
            for demonstrativo in demonstrativos:
                # Dados básicos do demonstrativo
                id_dm_dev = obter_texto_elemento(demonstrativo, "ideDmDev")
                cod_categ = obter_texto_elemento(demonstrativo, "codCateg")
                
                # Buscar informações de período de apuração
                info_per_apur = encontrar_elemento(demonstrativo, "infoPerApur")
                if info_per_apur is not None:
                    # Buscar estabelecimentos e lotações
                    estab_lots = encontrar_todos_elementos(info_per_apur, "ideEstabLot")
                    
                    for estab_lot in estab_lots:
                        # Dados do estabelecimento
                        nr_insc_estab = obter_texto_elemento(estab_lot, "nrInsc")
                        cod_lotacao = obter_texto_elemento(estab_lot, "codLotacao")
                        
                        # Buscar remuneração por período de apuração
                        remun_per_apur = encontrar_todos_elementos(estab_lot, "remunPerApur")
                        
                        for remun in remun_per_apur:
                            matricula = obter_texto_elemento(remun, "matricula")
                            
                            # Processar todas as rubricas
                            rubricas = encontrar_todos_elementos(remun, "itensRemun")
                            
                            for rubrica in rubricas:
                                # O XML S-1200 usa "cod" em vez de "codRubr" para o código da rubrica
                                codigo_rubrica = obter_texto_elemento(rubrica, "cod") or obter_texto_elemento(rubrica, "codRubr")
                                valor_str = obter_texto_elemento(rubrica, "vrRubr")
                                ide_tab_rubr = obter_texto_elemento(rubrica, "ideTabRubr") or codigo_rubrica  # Se não tiver ideTabRubr, usa o código
                                
                                # Converter valor para float
                                try:
                                    valor_rubrica = float(valor_str.replace(',', '.'))
                                except (ValueError, AttributeError):
                                    valor_rubrica = 0.0
                                
                                self.logger.debug(f"Rubrica encontrada: código={codigo_rubrica}, valor={valor_rubrica}")
                                
                                # Montar dicionário com os dados
                                # Incluir dados completos no JSON para permitir acesso a todos os campos
                                json_item = self._elemento_para_dict(rubrica)
                                # Adicionar dados contextuais ao JSON para facilitar a extração posteriormente
                                json_completo = {
                                    'evtRemun': {
                                        'ideEvento': {
                                            'perApur': {'_text': periodo_apuracao}
                                        },
                                        'ideEmpregador': {
                                            'nrInsc': {'_text': cnpj_empregador}
                                        },
                                        'ideTrabalhador': {
                                            'cpfTrab': {'_text': cpf_trabalhador}
                                        },
                                        'dmDev': {
                                            'ideDmDev': {'_text': id_dm_dev},
                                            'codCateg': {'_text': cod_categ}
                                        }
                                    }
                                }
                                # Combinar o JSON do item com dados de contexto
                                json_item.update({
                                    'matricula': {'_text': matricula},
                                    'perApur': {'_text': periodo_apuracao},
                                    'ideDmDev': {'_text': id_dm_dev},
                                    'codCateg': {'_text': cod_categ},
                                    'nrInscEstab': {'_text': nr_insc_estab}
                                })
                                
                                # Assegurar que temos o valor correto da rubrica como float
                                try:
                                    if isinstance(valor_rubrica, str):
                                        valor_rubrica_float = float(valor_rubrica.replace(',', '.'))
                                    else:
                                        valor_rubrica_float = float(valor_rubrica) if valor_rubrica is not None else 0.0
                                except (ValueError, AttributeError):
                                    valor_rubrica_float = 0.0

                                remuneracao_dict = {
                                    'periodo_apuracao': periodo_apuracao,
                                    'cpf_trabalhador': cpf_trabalhador,
                                    'matricula': matricula,
                                    'categoria': cod_categ,
                                    'estabelecimento': nr_insc_estab,
                                    'codigo_rubrica': codigo_rubrica,
                                    'descricao_rubrica': ide_tab_rubr,  # Using ideTabRubr as description for now
                                    'valor_rubrica': valor_rubrica_float,  # Usar float para garantir formato correto
                                    'tipo_rubrica': 'M',  # M para Mensal como padrão
                                    'cnpj_empregador': cnpj_empregador,
                                    'json_data': json.dumps(json_item)  # JSON enriquecido com dados de contexto
                                }
                                
                                remuneracoes_list.append(remuneracao_dict)
            
            # Inserir no banco de dados
            if remuneracoes_list:
                self.gerenciador_bd.inserir_dados("esocial_s1200", remuneracoes_list)
                return True
                
            return False
        except Exception as e:
            self.logger.error(f"Erro ao processar S-1200 {caminho_arquivo}: {e}", exc_info=True)
            return False
    
    def _processar_s2200(self, root, caminho_arquivo):
        """Processa arquivo XML do layout S-2200 (Cadastramento Inicial do Vínculo) - Enhanced Coverage"""
        try:
            # Extrair CNPJ do empregador
            ide_empregador = encontrar_elemento(root, "ideEmpregador")
            cnpj_empregador = obter_texto_elemento(ide_empregador, "nrInsc") if ide_empregador else ""
            
            # Extrair dados do trabalhador
            trabalhador = encontrar_elemento(root, "trabalhador")
            cpf_trabalhador = obter_texto_elemento(trabalhador, "cpfTrab") if trabalhador else ""
            nome_trabalhador = obter_texto_elemento(trabalhador, "nmTrab") if trabalhador else ""
            sexo = obter_texto_elemento(trabalhador, "sexo") if trabalhador else ""
            raca_cor = obter_texto_elemento(trabalhador, "racaCor") if trabalhador else ""
            estado_civil = obter_texto_elemento(trabalhador, "estCiv") if trabalhador else ""
            grau_instrucao = obter_texto_elemento(trabalhador, "grauInstr") if trabalhador else ""
            nome_social = obter_texto_elemento(trabalhador, "nmSoc") if trabalhador else ""
            
            # Data de nascimento
            nascimento = encontrar_elemento(trabalhador, "nascimento")
            data_nascimento = obter_texto_elemento(nascimento, "dtNascto") if nascimento else ""
            nm_mae = obter_texto_elemento(nascimento, "nmMae") if nascimento else ""
            nm_pai = obter_texto_elemento(nascimento, "nmPai") if nascimento else ""
            uf_nasc = obter_texto_elemento(nascimento, "uf") if nascimento else ""
            pais_nasc = obter_texto_elemento(nascimento, "paisNascto") if nascimento else ""
            pais_nac = obter_texto_elemento(nascimento, "paisNac") if nascimento else ""
            
            # Endereço (Brasil)
            endereco = encontrar_elemento(trabalhador, "endereco")
            end_brasil = encontrar_elemento(endereco, "brasil") if endereco else None
            tp_lograd = obter_texto_elemento(end_brasil, "tpLograd") if end_brasil else ""
            dsc_lograd = obter_texto_elemento(end_brasil, "dscLograd") if end_brasil else ""
            nr_lograd = obter_texto_elemento(end_brasil, "nrLograd") if end_brasil else ""
            complemento = obter_texto_elemento(end_brasil, "complemento") if end_brasil else ""
            cep = obter_texto_elemento(end_brasil, "cep") if end_brasil else ""
            bairro = obter_texto_elemento(end_brasil, "bairro") if end_brasil else ""
            cod_munic = obter_texto_elemento(end_brasil, "codMunic") if end_brasil else ""
            nm_cidade = obter_texto_elemento(end_brasil, "nmCid") if end_brasil else ""
            uf_resid = obter_texto_elemento(end_brasil, "uf") if end_brasil else ""
            
            # Endereço (Exterior)
            end_exterior = encontrar_elemento(endereco, "exterior") if endereco else None
            pais_resid = obter_texto_elemento(end_exterior, "paisResid") if end_exterior else ""
            bairro_ext = obter_texto_elemento(end_exterior, "bairro") if end_exterior else ""
            dsc_lograd_ext = obter_texto_elemento(end_exterior, "dscLograd") if end_exterior else ""
            nr_lograd_ext = obter_texto_elemento(end_exterior, "nrLograd") if end_exterior else ""
            complemento_ext = obter_texto_elemento(end_exterior, "complemento") if end_exterior else ""
            nm_cidade_ext = obter_texto_elemento(end_exterior, "nmCid") if end_exterior else ""
            cod_postal_ext = obter_texto_elemento(end_exterior, "codPostal") if end_exterior else ""
            
            # Trabalhador Imigrante
            trab_imig = encontrar_elemento(trabalhador, "trabImig")
            tmp_resid = obter_texto_elemento(trab_imig, "tmpResid") if trab_imig else ""
            cond_ing = obter_texto_elemento(trab_imig, "condIng") if trab_imig else ""
            
            # InfoDeficiencia
            info_def = encontrar_elemento(trabalhador, "infoDeficiencia")
            def_fisica = obter_texto_elemento(info_def, "defFisica") if info_def else ""
            def_visual = obter_texto_elemento(info_def, "defVisual") if info_def else ""
            def_auditiva = obter_texto_elemento(info_def, "defAuditiva") if info_def else ""
            def_mental = obter_texto_elemento(info_def, "defMental") if info_def else ""
            def_intelectual = obter_texto_elemento(info_def, "defIntelectual") if info_def else ""
            reab_readap = obter_texto_elemento(info_def, "reabReadap") if info_def else ""
            info_cota = obter_texto_elemento(info_def, "infoCota") if info_def else ""
            observacao_def = obter_texto_elemento(info_def, "observacao") if info_def else ""
            
            # Contato
            contato = encontrar_elemento(trabalhador, "contato")
            fone_princ = obter_texto_elemento(contato, "fonePrinc") if contato else ""
            fone_alt = obter_texto_elemento(contato, "foneAlternativo") if contato else ""
            email_princ = obter_texto_elemento(contato, "emailPrinc") if contato else ""
            email_alt = obter_texto_elemento(contato, "emailAlternativo") if contato else ""
            contato_emerg = obter_texto_elemento(contato, "contatoEmergencia") if contato else ""
            fone_emerg = obter_texto_elemento(contato, "foneEmergencia") if contato else ""
            parentesco_emerg = obter_texto_elemento(contato, "parentescoEmergencia") if contato else ""
            
            # Documentos - Enhanced extraction
            documentos = encontrar_elemento(trabalhador, "documentos")
            
            # PIS/NIS
            nis_trab = obter_texto_elemento(trabalhador, "nisTrab") if trabalhador else ""
            
            # RG
            rg = encontrar_elemento(documentos, "rg") if documentos else None
            nr_rg = obter_texto_elemento(rg, "nrRg") if rg else ""
            orgao_emissor_rg = obter_texto_elemento(rg, "orgaoEmissor") if rg else ""
            dt_exped_rg = obter_texto_elemento(rg, "dtExped") if rg else ""
            uf_rg = obter_texto_elemento(rg, "uf") if rg else ""
            
            # CTPS
            ctps = encontrar_elemento(documentos, "ctps") if documentos else None
            nr_ctps = obter_texto_elemento(ctps, "nrCtps") if ctps else ""
            serie_ctps = obter_texto_elemento(ctps, "serieCtps") if ctps else ""
            uf_ctps = obter_texto_elemento(ctps, "ufCtps") if ctps else ""
            dt_exped_ctps = obter_texto_elemento(ctps, "dtExped") if ctps else ""
            
            # CNH
            cnh = encontrar_elemento(documentos, "cnh") if documentos else None
            nr_reg_cnh = obter_texto_elemento(cnh, "nrRegCnh") if cnh else ""
            categoria_cnh = obter_texto_elemento(cnh, "categoriaCnh") if cnh else ""
            uf_cnh = obter_texto_elemento(cnh, "ufCnh") if cnh else ""
            dt_exped_cnh = obter_texto_elemento(cnh, "dtExped") if cnh else ""
            dt_pri_hab = obter_texto_elemento(cnh, "dtPriHab") if cnh else ""
            dt_valid_cnh = obter_texto_elemento(cnh, "dtValid") if cnh else ""
            
            # RNE
            rne = encontrar_elemento(documentos, "rne") if documentos else None
            nr_rne = obter_texto_elemento(rne, "nrRne") if rne else ""
            orgao_emissor_rne = obter_texto_elemento(rne, "orgaoEmissor") if rne else ""
            uf_rne = obter_texto_elemento(rne, "uf") if rne else ""
            dt_exped_rne = obter_texto_elemento(rne, "dtExped") if rne else ""
            
            # Passaporte
            passaporte = encontrar_elemento(documentos, "passaporte") if documentos else None
            nr_passaporte = obter_texto_elemento(passaporte, "nrPassaporte") if passaporte else ""
            pais_origem_passaporte = obter_texto_elemento(passaporte, "paisOrigem") if passaporte else ""
            dt_exped_passaporte = obter_texto_elemento(passaporte, "dtExped") if passaporte else ""
            dt_valid_passaporte = obter_texto_elemento(passaporte, "dtValid") if passaporte else ""
            
            # RIC
            ric = encontrar_elemento(documentos, "ric") if documentos else None
            nr_ric = obter_texto_elemento(ric, "nrRic") if ric else ""
            orgao_emissor_ric = obter_texto_elemento(ric, "orgaoEmissor") if ric else ""
            uf_ric = obter_texto_elemento(ric, "uf") if ric else ""
            dt_exped_ric = obter_texto_elemento(ric, "dtExped") if ric else ""
            
            # Título de Eleitor
            titulo_eleitor = encontrar_elemento(documentos, "tituloEleitor") if documentos else None
            nr_titulo = obter_texto_elemento(titulo_eleitor, "nrTitulo") if titulo_eleitor else ""
            zona_titulo = obter_texto_elemento(titulo_eleitor, "zona") if titulo_eleitor else ""
            secao_titulo = obter_texto_elemento(titulo_eleitor, "secao") if titulo_eleitor else ""
            cod_munic_titulo = obter_texto_elemento(titulo_eleitor, "codMunic") if titulo_eleitor else ""
            nm_cidade_titulo = obter_texto_elemento(titulo_eleitor, "nmCid") if titulo_eleitor else ""
            uf_titulo = obter_texto_elemento(titulo_eleitor, "uf") if titulo_eleitor else ""
            dt_exped_titulo = obter_texto_elemento(titulo_eleitor, "dtExped") if titulo_eleitor else ""
            
            # Certidão Militar
            certidao_militar = encontrar_elemento(documentos, "certidaoMilitar") if documentos else None
            nr_certidao = obter_texto_elemento(certidao_militar, "nrCertidao") if certidao_militar else ""
            dt_exped_certidao = obter_texto_elemento(certidao_militar, "dtExped") if certidao_militar else ""
            regiao_militar = obter_texto_elemento(certidao_militar, "regiaoMilitar") if certidao_militar else ""
            tipo_certidao = obter_texto_elemento(certidao_militar, "tipoCertidao") if certidao_militar else ""
            nr_certidao2 = obter_texto_elemento(certidao_militar, "nrCertidao2") if certidao_militar else ""
            nr_serie = obter_texto_elemento(certidao_militar, "nrSerie") if certidao_militar else ""
            dt_exped_certidao2 = obter_texto_elemento(certidao_militar, "dtExped2") if certidao_militar else ""
            categoria_certidao = obter_texto_elemento(certidao_militar, "categoria") if certidao_militar else ""
            
            # Conselho de Classe
            conselho = encontrar_elemento(documentos, "conselho") if documentos else None
            nr_registro_conselho = obter_texto_elemento(conselho, "nrRegistro") if conselho else ""
            orgao_emissor_conselho = obter_texto_elemento(conselho, "orgaoEmissor") if conselho else ""
            uf_conselho = obter_texto_elemento(conselho, "uf") if conselho else ""
            dt_exped_conselho = obter_texto_elemento(conselho, "dtExped") if conselho else ""
            dt_validade_conselho = obter_texto_elemento(conselho, "dtValidade") if conselho else ""
            
            # Trabalhador Estrangeiro
            trab_estrangeiro = encontrar_elemento(trabalhador, "trabEstrangeiro")
            dt_chegada = obter_texto_elemento(trab_estrangeiro, "dtChegada") if trab_estrangeiro else ""
            class_trab_estrang = obter_texto_elemento(trab_estrangeiro, "classTrabEstrang") if trab_estrangeiro else ""
            casado_br = obter_texto_elemento(trab_estrangeiro, "casadoBr") if trab_estrangeiro else ""
            filhos_br = obter_texto_elemento(trab_estrangeiro, "filhosBr") if trab_estrangeiro else ""
            
            # Dados do vínculo
            vinculo = encontrar_elemento(root, "vinculo")
            matricula = obter_texto_elemento(vinculo, "matricula") if vinculo else ""
            tp_reg_trab = obter_texto_elemento(vinculo, "tpRegTrab") if vinculo else ""
            tp_reg_prev = obter_texto_elemento(vinculo, "tpRegPrev") if vinculo else ""
            cad_ini = obter_texto_elemento(vinculo, "cadIni") if vinculo else ""
            
            # InfoRegimeTrab
            info_regime_trab = encontrar_elemento(vinculo, "infoRegimeTrab") if vinculo else None
            info_celetista = encontrar_elemento(info_regime_trab, "infoCeletista") if info_regime_trab else None
            info_estatutario = encontrar_elemento(info_regime_trab, "infoEstatutario") if info_regime_trab else None
            
            # InfoCeletista
            dt_adm = obter_texto_elemento(info_celetista, "dtAdm") if info_celetista else ""
            tp_admissao = obter_texto_elemento(info_celetista, "tpAdmissao") if info_celetista else ""
            ind_admissao = obter_texto_elemento(info_celetista, "indAdmissao") if info_celetista else ""
            nr_proc_trab = obter_texto_elemento(info_celetista, "nrProcTrab") if info_celetista else ""
            tp_reg_jor = obter_texto_elemento(info_celetista, "tpRegJor") if info_celetista else ""
            nat_atividade = obter_texto_elemento(info_celetista, "natAtividade") if info_celetista else ""
            dt_base = obter_texto_elemento(info_celetista, "dtBase") if info_celetista else ""
            cnpj_sind_categ_prof = obter_texto_elemento(info_celetista, "cnpjSindCategProf") if info_celetista else ""
            mat_anot_jud = obter_texto_elemento(info_celetista, "matAnotJud") if info_celetista else ""
            
            # FGTS
            fgts = encontrar_elemento(info_celetista, "FGTS") if info_celetista else None
            dt_opc_fgts = obter_texto_elemento(fgts, "dtOpcFGTS") if fgts else ""
            
            # Trabalho Temporário
            trab_temp = encontrar_elemento(info_celetista, "trabTemporario") if info_celetista else None
            hip_leg = obter_texto_elemento(trab_temp, "hipLeg") if trab_temp else ""
            just_contr = obter_texto_elemento(trab_temp, "justContr") if trab_temp else ""
            tp_insc_estab = obter_texto_elemento(trab_temp, "tpInscEstab") if trab_temp else ""
            nr_insc_estab = obter_texto_elemento(trab_temp, "nrInscEstab") if trab_temp else ""
            cpf_trab_subst = obter_texto_elemento(trab_temp, "cpfTrabSubst") if trab_temp else ""
            
            # InfoEstatutario
            tp_prov = obter_texto_elemento(info_estatutario, "tpProv") if info_estatutario else ""
            dt_exercicio = obter_texto_elemento(info_estatutario, "dtExercicio") if info_estatutario else ""
            tp_plan_rp = obter_texto_elemento(info_estatutario, "tpPlanRP") if info_estatutario else ""
            ind_teto_rgps = obter_texto_elemento(info_estatutario, "indTetoRGPS") if info_estatutario else ""
            ind_abono_perm = obter_texto_elemento(info_estatutario, "indAbonoPerm") if info_estatutario else ""
            dt_ini_abono = obter_texto_elemento(info_estatutario, "dtIniAbono") if info_estatutario else ""
            
            # InfoContrato
            info_contrato = encontrar_elemento(vinculo, "infoContrato") if vinculo else None
            nm_cargo = obter_texto_elemento(info_contrato, "nmCargo") if info_contrato else ""
            cbo_cargo = obter_texto_elemento(info_contrato, "CBOCargo") if info_contrato else ""
            dt_ingr_cargo = obter_texto_elemento(info_contrato, "dtIngrCargo") if info_contrato else ""
            nm_funcao = obter_texto_elemento(info_contrato, "nmFuncao") if info_contrato else ""
            cbo_funcao = obter_texto_elemento(info_contrato, "CBOFuncao") if info_contrato else ""
            acum_cargo = obter_texto_elemento(info_contrato, "acumCargo") if info_contrato else ""
            cod_categoria = obter_texto_elemento(info_contrato, "codCateg") if info_contrato else ""
            
            # Remuneração
            remuneracao = encontrar_elemento(info_contrato, "remuneracao") if info_contrato else None
            salario_contratual = 0.0
            if remuneracao is not None:
                valor_str = obter_texto_elemento(remuneracao, "vrSalFx")
                try:
                    salario_contratual = float(valor_str.replace(',', '.')) if valor_str else 0.0
                except (ValueError, TypeError, AttributeError):
                    self.logger.warning(f"Valor salarial inválido ou não numérico: '{valor_str}'. Usando 0.0 como padrão.")
                    salario_contratual = 0.0
            und_sal_fixo = obter_texto_elemento(remuneracao, "undSalFixo") if remuneracao else ""
            
            # Duração do contrato
            duracao = encontrar_elemento(info_contrato, "duracao") if info_contrato else None
            tipo_contrato = ""
            duracao_contrato = ""
            clau_assec = ""
            obj_det = ""
            if duracao is not None:
                tipo_contrato = obter_texto_elemento(duracao, "tpContr")
                duracao_contrato = obter_texto_elemento(duracao, "dtTerm")
                clau_assec = obter_texto_elemento(duracao, "clauAssec")
                obj_det = obter_texto_elemento(duracao, "objDet")
            
            # Local de Trabalho
            local_trabalho = encontrar_elemento(info_contrato, "localTrabalho") if info_contrato else None
            local_trab_geral = encontrar_elemento(local_trabalho, "localTrabGeral") if local_trabalho else None
            local_temp_dom = encontrar_elemento(local_trabalho, "localTempDom") if local_trabalho else None
            
            # Horário Contratual
            hor_contratual = encontrar_elemento(info_contrato, "horContratual") if info_contrato else None
            
            # Alvará Judicial
            alvara_judicial = encontrar_elemento(info_contrato, "alvaraJudicial") if info_contrato else None
            
            # Observações
            observacoes = encontrar_elemento(info_contrato, "observacoes") if info_contrato else None
            observacao = obter_texto_elemento(observacoes, "observacao") if observacoes else ""
            
            # Treinamentos/Capacitações
            trei_cap = encontrar_elemento(info_contrato, "treiCap") if info_contrato else None
            
            # Sucessão de Vínculo
            sucessao_vinc = encontrar_elemento(vinculo, "sucessaoVinc") if vinculo else None
            sucessao_tp_insc = obter_texto_elemento(sucessao_vinc, "tpInsc") if sucessao_vinc else ""
            sucessao_nr_insc = obter_texto_elemento(sucessao_vinc, "nrInsc") if sucessao_vinc else ""
            sucessao_matric_ant = obter_texto_elemento(sucessao_vinc, "matricAnt") if sucessao_vinc else ""
            sucessao_dt_transf = obter_texto_elemento(sucessao_vinc, "dtTransf") if sucessao_vinc else ""
            sucessao_observacao = obter_texto_elemento(sucessao_vinc, "observacao") if sucessao_vinc else ""
            
            # Transferência Doméstica
            transf_dom = encontrar_elemento(vinculo, "transfDom") if vinculo else None
            cpf_substituido = obter_texto_elemento(transf_dom, "cpfSubstituido") if transf_dom else ""
            transf_matric_ant = obter_texto_elemento(transf_dom, "matricAnt") if transf_dom else ""
            transf_dt_transf = obter_texto_elemento(transf_dom, "dtTransf") if transf_dom else ""
            
            # Mudança de CPF
            mudanca_cpf = encontrar_elemento(vinculo, "mudancaCPF") if vinculo else None
            cpf_ant = obter_texto_elemento(mudanca_cpf, "cpfAnt") if mudanca_cpf else ""
            mudanca_matric_ant = obter_texto_elemento(mudanca_cpf, "matricAnt") if mudanca_cpf else ""
            dt_alt_cpf = obter_texto_elemento(mudanca_cpf, "dtAltCPF") if mudanca_cpf else ""
            mudanca_observacao = obter_texto_elemento(mudanca_cpf, "observacao") if mudanca_cpf else ""
            
            # Afastamento
            afastamento = encontrar_elemento(vinculo, "afastamento") if vinculo else None
            dt_ini_afast = obter_texto_elemento(afastamento, "dtIniAfast") if afastamento else ""
            cod_mot_afast = obter_texto_elemento(afastamento, "codMotAfast") if afastamento else ""
            
            # Desligamento
            desligamento = encontrar_elemento(vinculo, "desligamento") if vinculo else None
            dt_deslig = obter_texto_elemento(desligamento, "dtDeslig") if desligamento else ""
            
            # Cessão
            cessao = encontrar_elemento(vinculo, "cessao") if vinculo else None
            dt_ini_cessao = obter_texto_elemento(cessao, "dtIniCessao") if cessao else ""
            
            # Montar dicionário com TODOS os dados do trabalhador (Enhanced Coverage)
            vinculo_dict = {
                # Dados básicos do trabalhador
                'cpf_trabalhador': cpf_trabalhador,
                'nome_trabalhador': nome_trabalhador,
                'sexo': sexo,
                'raca_cor': raca_cor,
                'estado_civil': estado_civil,
                'grau_instrucao': grau_instrucao,
                'nome_social': nome_social,
                
                # Nascimento
                'data_nascimento': data_nascimento,
                'nm_mae': nm_mae,
                'nm_pai': nm_pai,
                'uf_nasc': uf_nasc,
                'pais_nasc': pais_nasc,
                'pais_nac': pais_nac,
                
                # Endereço Brasil
                'tp_lograd': tp_lograd,
                'dsc_lograd': dsc_lograd,
                'nr_lograd': nr_lograd,
                'complemento': complemento,
                'cep': cep,
                'bairro': bairro,
                'cod_munic': cod_munic,
                'nm_cidade': nm_cidade,
                'uf_resid': uf_resid,
                
                # Endereço Exterior
                'pais_resid': pais_resid,
                'bairro_ext': bairro_ext,
                'dsc_lograd_ext': dsc_lograd_ext,
                'nr_lograd_ext': nr_lograd_ext,
                'complemento_ext': complemento_ext,
                'nm_cidade_ext': nm_cidade_ext,
                'cod_postal_ext': cod_postal_ext,
                
                # Trabalhador Imigrante
                'tmp_resid': tmp_resid,
                'cond_ing': cond_ing,
                
                # InfoDeficiencia
                'def_fisica': def_fisica,
                'def_visual': def_visual,
                'def_auditiva': def_auditiva,
                'def_mental': def_mental,
                'def_intelectual': def_intelectual,
                'reab_readap': reab_readap,
                'info_cota': info_cota,
                'observacao_def': observacao_def,
                
                # Contato
                'fone_princ': fone_princ,
                'fone_alt': fone_alt,
                'email_princ': email_princ,
                'email_alt': email_alt,
                'contato_emerg': contato_emerg,
                'fone_emerg': fone_emerg,
                'parentesco_emerg': parentesco_emerg,
                
                # Documentos - Enhanced
                'nis_trabalhador': nis_trab,
                'nr_rg': nr_rg,
                'orgao_emissor_rg': orgao_emissor_rg,
                'dt_exped_rg': dt_exped_rg,
                'uf_rg': uf_rg,
                'nr_ctps': nr_ctps,
                'serie_ctps': serie_ctps,
                'uf_ctps': uf_ctps,
                'dt_exped_ctps': dt_exped_ctps,
                'nr_reg_cnh': nr_reg_cnh,
                'categoria_cnh': categoria_cnh,
                'uf_cnh': uf_cnh,
                'dt_exped_cnh': dt_exped_cnh,
                'dt_pri_hab': dt_pri_hab,
                'dt_valid_cnh': dt_valid_cnh,
                'nr_rne': nr_rne,
                'orgao_emissor_rne': orgao_emissor_rne,
                'uf_rne': uf_rne,
                'dt_exped_rne': dt_exped_rne,
                'nr_passaporte': nr_passaporte,
                'pais_origem_passaporte': pais_origem_passaporte,
                'dt_exped_passaporte': dt_exped_passaporte,
                'dt_valid_passaporte': dt_valid_passaporte,
                'nr_ric': nr_ric,
                'orgao_emissor_ric': orgao_emissor_ric,
                'uf_ric': uf_ric,
                'dt_exped_ric': dt_exped_ric,
                'nr_titulo': nr_titulo,
                'zona_titulo': zona_titulo,
                'secao_titulo': secao_titulo,
                'cod_munic_titulo': cod_munic_titulo,
                'nm_cidade_titulo': nm_cidade_titulo,
                'uf_titulo': uf_titulo,
                'dt_exped_titulo': dt_exped_titulo,
                'nr_certidao': nr_certidao,
                'dt_exped_certidao': dt_exped_certidao,
                'regiao_militar': regiao_militar,
                'tipo_certidao': tipo_certidao,
                'nr_certidao2': nr_certidao2,
                'nr_serie': nr_serie,
                'dt_exped_certidao2': dt_exped_certidao2,
                'categoria_certidao': categoria_certidao,
                'nr_registro_conselho': nr_registro_conselho,
                'orgao_emissor_conselho': orgao_emissor_conselho,
                'uf_conselho': uf_conselho,
                'dt_exped_conselho': dt_exped_conselho,
                'dt_validade_conselho': dt_validade_conselho,
                
                # Trabalhador Estrangeiro
                'dt_chegada': dt_chegada,
                'class_trab_estrang': class_trab_estrang,
                'casado_br': casado_br,
                'filhos_br': filhos_br,
                
                # Vínculo
                'matricula': matricula,
                'tp_reg_trab': tp_reg_trab,
                'tp_reg_prev': tp_reg_prev,
                'cad_ini': cad_ini,
                
                # InfoCeletista
                'dt_adm': dt_adm,
                'tp_admissao': tp_admissao,
                'ind_admissao': ind_admissao,
                'nr_proc_trab': nr_proc_trab,
                'tp_reg_jor': tp_reg_jor,
                'nat_atividade': nat_atividade,
                'dt_base': dt_base,
                'cnpj_sind_categ_prof': cnpj_sind_categ_prof,
                'mat_anot_jud': mat_anot_jud,
                'dt_opc_fgts': dt_opc_fgts,
                
                # Trabalho Temporário
                'hip_leg': hip_leg,
                'just_contr': just_contr,
                'tp_insc_estab': tp_insc_estab,
                'nr_insc_estab': nr_insc_estab,
                'cpf_trab_subst': cpf_trab_subst,
                
                # InfoEstatutario
                'tp_prov': tp_prov,
                'dt_exercicio': dt_exercicio,
                'tp_plan_rp': tp_plan_rp,
                'ind_teto_rgps': ind_teto_rgps,
                'ind_abono_perm': ind_abono_perm,
                'dt_ini_abono': dt_ini_abono,
                
                # InfoContrato
                'nm_cargo': nm_cargo,
                'cbo_cargo': cbo_cargo,
                'dt_ingr_cargo': dt_ingr_cargo,
                'nm_funcao': nm_funcao,
                'cbo_funcao': cbo_funcao,
                'acum_cargo': acum_cargo,
                'cod_categoria': cod_categoria,
                'salario_contratual': salario_contratual,
                'und_sal_fixo': und_sal_fixo,
                'tipo_contrato': tipo_contrato,
                'duracao_contrato': duracao_contrato,
                'clau_assec': clau_assec,
                'obj_det': obj_det,
                
                # Sucessão de Vínculo
                'sucessao_tp_insc': sucessao_tp_insc,
                'sucessao_nr_insc': sucessao_nr_insc,
                'sucessao_matric_ant': sucessao_matric_ant,
                'sucessao_dt_transf': sucessao_dt_transf,
                'sucessao_observacao': sucessao_observacao,
                
                # Transferência Doméstica
                'cpf_substituido': cpf_substituido,
                'transf_matric_ant': transf_matric_ant,
                'transf_dt_transf': transf_dt_transf,
                
                # Mudança de CPF
                'cpf_ant': cpf_ant,
                'mudanca_matric_ant': mudanca_matric_ant,
                'dt_alt_cpf': dt_alt_cpf,
                'mudanca_observacao': mudanca_observacao,
                
                # Afastamento
                'dt_ini_afast': dt_ini_afast,
                'cod_mot_afast': cod_mot_afast,
                
                # Desligamento
                'dt_deslig': dt_deslig,
                
                # Cessão
                'dt_ini_cessao': dt_ini_cessao,
                
                # Dados do empregador
                'cnpj_empregador': cnpj_empregador,
                
                # JSON completo para análise (corrigido: wrap em 'evtAdmissao')
                'json_data': json.dumps({'evtAdmissao': self._elemento_para_dict(root)})
            }
            
            # Validar dados do trabalhador
            valido, mensagens_erro = ValidadorDados.validar_registro_s2200(vinculo_dict)
            if not valido:
                for erro in mensagens_erro:
                    self.logger.warning(f"Validação para CPF {cpf_trabalhador}, arquivo {caminho_arquivo}: {erro}")
                
                # Tentar corrigir dados problemáticos
                vinculo_dict = ValidadorDados.sanitizar_dados(vinculo_dict, 'S-2200')
                
                # Revalidar após correções
                valido, mensagens_erro = ValidadorDados.validar_registro_s2200(vinculo_dict)
                if not valido:
                    self.logger.warning(f"Dados ainda apresentam problemas após correções: {', '.join(mensagens_erro)}")
                else:
                    self.logger.info(f"Dados corrigidos com sucesso para CPF {cpf_trabalhador}")
            
            # Processar dependentes
            dependentes_list = []
            dependentes = encontrar_todos_elementos(trabalhador, "dependente")
            
            for dependente in dependentes:
                try:
                    # Extrair dados do dependente
                    nome_dependente = obter_texto_elemento(dependente, "nmDep")
                    data_nascimento_dep = obter_texto_elemento(dependente, "dtNascto")
                    cpf_dependente = obter_texto_elemento(dependente, "cpfDep")
                    tipo_dependente = obter_texto_elemento(dependente, "tpDep")
                    sexo_dependente = obter_texto_elemento(dependente, "sexoDep")
                    dep_irrf = obter_texto_elemento(dependente, "depIRRF")
                    dep_sf = obter_texto_elemento(dependente, "depSF")
                    inc_trab = obter_texto_elemento(dependente, "incTrab")
                    descr_dep = obter_texto_elemento(dependente, "descrDep")
                    
                    # Montar dicionário do dependente
                    dependente_dict = {
                        'cpf_trabalhador': cpf_trabalhador,
                        'matricula': matricula,
                        'nome_dependente': nome_dependente,
                        'cpf_dependente': cpf_dependente,
                        'data_nascimento': data_nascimento_dep,
                        'tipo_dependente': tipo_dependente,
                        'sexo_dependente': sexo_dependente,
                        'dep_irrf': dep_irrf,
                        'dep_sf': dep_sf,
                        'inc_trab': inc_trab,
                        'descr_dep': descr_dep,
                        'cnpj_empregador': cnpj_empregador,
                        'json_data': json.dumps(self._elemento_para_dict(dependente))
                    }
                    
                    # Validar CPF do dependente se estiver preenchido
                    if cpf_dependente and not ValidadorDados.validar_cpf(cpf_dependente):
                        self.logger.warning(f"CPF de dependente inválido: {cpf_dependente}")
                        # Sanitizar CPF ou limpar se for inválido
                        dependente_dict['cpf_dependente'] = ValidadorDados.formatar_cpf(cpf_dependente)
                        if not ValidadorDados.validar_cpf(dependente_dict['cpf_dependente']):
                            dependente_dict['cpf_dependente'] = ""
                    
                    # Validar data de nascimento
                    if data_nascimento_dep and not ValidadorDados.validar_data(data_nascimento_dep):
                        self.logger.warning(f"Data de nascimento de dependente inválida: {data_nascimento_dep}")
                        dependente_dict['data_nascimento'] = ""
                    
                    dependentes_list.append(dependente_dict)
                except Exception as e:
                    self.logger.warning(f"Erro ao processar dependente: {e}", exc_info=True)
                    continue  # Continuar com o próximo dependente
            
            # Inserir no banco de dados em transação única
            try:
                # Inserir trabalhador
                self.gerenciador_bd.inserir_dados("esocial_s2200", [vinculo_dict])
                
                # Inserir dependentes se houver
                if dependentes_list:
                    inseridos = self.gerenciador_bd.inserir_dados("esocial_dependentes", dependentes_list)
                    self.logger.info(f"Inseridos {inseridos} dependentes para o trabalhador {cpf_trabalhador}")
                
                return True
            except Exception as e:
                self.logger.error(f"Erro ao inserir dados no banco: {e}", exc_info=True)
                return False
            
        except Exception as e:
            self.logger.error(f"Erro ao processar S-2200 {caminho_arquivo}: {e}", exc_info=True)
            return False
    
    def _processar_s2205(self, root, caminho_arquivo):
        """Processa arquivo XML do layout S-2205 (Alteração de Dados Cadastrais)"""
        try:
            # Extrair CNPJ do empregador
            ide_empregador = encontrar_elemento(root, "ideEmpregador")
            cnpj_empregador = obter_texto_elemento(ide_empregador, "nrInsc") if ide_empregador else ""

            # Extrair dados do trabalhador
            ide_trabalhador = encontrar_elemento(root, "ideTrabalhador")
            cpf_trabalhador = obter_texto_elemento(ide_trabalhador, "cpfTrab") if ide_trabalhador else ""
            matricula = obter_texto_elemento(root, "matricula")  # S-2205 may not have matricula at root, try alteracao/matricula
            
            # Extrair bloco de alteracao
            alteracao = encontrar_elemento(root, "alteracao")
            data_alteracao = obter_texto_elemento(alteracao, "dtAlteracao") if alteracao else ""
            dados_gerais = encontrar_elemento(alteracao, "dadosTrabalhador") if alteracao else None

            # Extrair novos dados do trabalhador
            nome_trabalhador = obter_texto_elemento(dados_gerais, "nmTrab") if dados_gerais else ""
            sexo = obter_texto_elemento(dados_gerais, "sexo") if dados_gerais else ""
            raca_cor = obter_texto_elemento(dados_gerais, "racaCor") if dados_gerais else ""
            estado_civil = obter_texto_elemento(dados_gerais, "estCiv") if dados_gerais else ""
            grau_instrucao = obter_texto_elemento(dados_gerais, "grauInstr") if dados_gerais else ""
            nascimento = encontrar_elemento(dados_gerais, "nascimento") if dados_gerais else None
            data_nascimento = obter_texto_elemento(nascimento, "dtNascto") if nascimento else ""

            # Montar dicionário com os dados
            alteracao_dict = {
                'cpf_trabalhador': cpf_trabalhador,
                'nome_trabalhador': nome_trabalhador,
                'data_alteracao': data_alteracao,
                'sexo': sexo,
                'raca_cor': raca_cor,
                'estado_civil': estado_civil,
                'grau_instrucao': grau_instrucao,
                'data_nascimento': data_nascimento,
                'cnpj_empregador': cnpj_empregador,
                'matricula': matricula,
                'json_data': json.dumps(self._elemento_para_dict(root))
            }

            # Inserir no banco de dados
            self.gerenciador_bd.inserir_dados("esocial_s2205", [alteracao_dict])
            return True
        except Exception as e:
            self.logger.error(f"Erro ao processar S-2205 {caminho_arquivo}: {e}", exc_info=True)
            return False
    
    def _processar_s2206(self, root, caminho_arquivo):
        """Processa arquivo XML do layout S-2206 (Alteração de Contrato de Trabalho)"""
        try:
            self.logger.debug(f"Iniciando processamento de S-2206: {caminho_arquivo}")
            
            # Extrair CNPJ do empregador
            ide_empregador = encontrar_elemento(root, "ideEmpregador")
            cnpj_empregador = obter_texto_elemento(ide_empregador, "nrInsc") if ide_empregador else ""
            self.logger.debug(f"S-2206: CNPJ empregador = {cnpj_empregador}")
            
            # Extrair dados do trabalhador - tenta em ideVinculo primeiro, depois em ideTrabalhador
            cpf_trabalhador = ""
            matricula = ""
            
            # Tenta em ideVinculo
            ide_vinculo = encontrar_elemento(root, "ideVinculo")
            if ide_vinculo is not None:
                cpf_trabalhador = obter_texto_elemento(ide_vinculo, "cpfTrab")
                matricula = obter_texto_elemento(ide_vinculo, "matricula")
                
            # Se não encontrou em ideVinculo, tenta em ideTrabalhador
            if not cpf_trabalhador:
                ide_trabalhador = encontrar_elemento(root, "ideTrabalhador")
                if ide_trabalhador is not None:
                    cpf_trabalhador = obter_texto_elemento(ide_trabalhador, "cpfTrab")
                    matricula = obter_texto_elemento(ide_trabalhador, "matricula")
            
            self.logger.debug(f"S-2206: CPF = {cpf_trabalhador}, Matricula = {matricula}")
            
            # Data da alteração
            alteracao_info = encontrar_elemento(root, "altContratual")
            data_alteracao = obter_texto_elemento(alteracao_info, "dtAlteracao") if alteracao_info else ""
            self.logger.debug(f"S-2206: Data alteração = {data_alteracao}")
            
            # Dados do contrato alterado - procurar dentro de altContratual/vinculo/infoContrato ou altContratual/infoContrato
            vinculo_alt = encontrar_elemento(alteracao_info, "vinculo") if alteracao_info else None
            info_contrato = None
            
            # Tenta encontrar infoContrato dentro de vinculo
            if vinculo_alt is not None:
                info_contrato = encontrar_elemento(vinculo_alt, "infoContrato")
            
            # Se não encontrou, tenta diretamente em altContratual
            if info_contrato is None and alteracao_info is not None:
                info_contrato = encontrar_elemento(alteracao_info, "infoContrato")
            
            # Valores padrão para os campos
            cod_cargo = ""
            cod_funcao = ""
            cod_categoria = ""
            salario_contratual = 0.0
            tipo_contrato = ""
            
            if info_contrato is not None:
                self.logger.debug("S-2206: Encontrou infoContrato")
                # Informações de cargo
                cod_cargo = obter_texto_elemento(info_contrato, "codCargo")
                cod_funcao = obter_texto_elemento(info_contrato, "codFuncao")
                cod_categoria = obter_texto_elemento(info_contrato, "codCateg")
                
                self.logger.debug(f"S-2206: cod_cargo = {cod_cargo}, cod_funcao = {cod_funcao}, cod_categoria = {cod_categoria}")
                
                # Se não encontrar codCargo, tenta CBOCargo como alternativa
                if not cod_cargo:
                    cod_cargo = obter_texto_elemento(info_contrato, "CBOCargo")
                
                # Remuneração
                remuneracao = encontrar_elemento(info_contrato, "remuneracao")
                salario_str = obter_texto_elemento(remuneracao, "vrSalFx") if remuneracao else "0"
                try:
                    salario_contratual = float(salario_str.replace(',', '.'))
                except (ValueError, AttributeError):
                    salario_contratual = 0.0
                
                self.logger.debug(f"S-2206: salario_contratual = {salario_contratual}")
                
                # Duração do contrato
                duracao_elemento = encontrar_elemento(info_contrato, "duracao")
                tipo_contrato = obter_texto_elemento(duracao_elemento, "tpContr") if duracao_elemento else ""
            
            # Montar dicionário com os dados coletados
            alteracao_dict = {
                'cpf_trabalhador': cpf_trabalhador,
                'matricula': matricula,
                'data_alteracao': data_alteracao,
                'cod_cargo': cod_cargo,
                'cod_funcao': cod_funcao,
                'cod_lotacao': '',  # Não presente nesta estrutura
                'salario_contratual': salario_contratual,
                'tipo_contrato': tipo_contrato,
                'duracao_contrato': '',  # Sem data fim específica
                'cnpj_empregador': cnpj_empregador,
                'json_data': json.dumps(self._elemento_para_dict(root))
            }
            
            self.logger.info(f"S-2206: Inserindo dados para CPF {cpf_trabalhador}, alteração de {data_alteracao}")
            
            # Inserir no banco de dados
            registros = self.gerenciador_bd.inserir_dados("esocial_s2206", [alteracao_dict])
            self.logger.info(f"S-2206: {registros} registros inseridos no banco")
            return registros > 0
            
        except Exception as e:
            self.logger.error(f"Erro ao processar S-2206 {caminho_arquivo}: {e}", exc_info=True)
            return False
    
    def _processar_s2230(self, root, caminho_arquivo):
        """Processa arquivo XML do layout S-2230 (Afastamento Temporário)"""
        try:
            # Extrair CNPJ do empregador
            cnpj_empregador = obter_texto_elemento(root, "nrInsc")
            
            # Extrair dados do trabalhador
            cpf_trabalhador = obter_texto_elemento(root, "cpfTrab")
            matricula = obter_texto_elemento(root, "matricula")
            
            # Informações do afastamento
            info_afastamento = encontrar_elemento(root, "infoAfastamento")
            
            # Lista para armazenar afastamentos
            afastamentos_list = []
            
            if info_afastamento is not None:
                # Dados do início do afastamento
                inicio = encontrar_elemento(info_afastamento, "iniAfastamento")
                if inicio is not None:
                    data_inicio = obter_texto_elemento(inicio, "dtIniAfast")
                    codigo_motivo = obter_texto_elemento(inicio, "codMotAfast")
                    
                    # Buscar descrição do motivo
                    descricoes_motivo = {
                        '01': 'Acidente/Doença do trabalho',
                        '03': 'Acidente/Doença não relacionada ao trabalho',
                        '05': 'Afastamento/Licença prevista em regime próprio, sem remuneração',
                        '06': 'Aposentadoria por invalidez',
                        '07': 'Acompanhamento de membro da família enfermo',
                        '08': 'Afastamento/Licença prevista em regime próprio, com remuneração',
                        '10': 'Licença-maternidade',
                        '11': 'Licença-maternidade - (prorrogação)',
                        '12': 'Licença-paternidade',
                        '13': 'Licença-paternidade - (prorrogação)',
                        '14': 'Licença remunerada prevista em CCT/ACT',
                        '15': 'Serviço militar obrigatório',
                        '16': 'Sustação do contrato de trabalho em virtude de inquérito',
                        '17': 'Aposentadoria por invalidez',
                        '18': 'Afastamento pelo INSS por acidente ou doença',
                        '19': 'Afastamento sem remuneração',
                        '20': 'Férias',
                        '21': 'Férias coletivas',
                        '22': 'Licença-prêmio',
                        '23': 'Mandato eleitoral',
                        '24': 'Mandato sindical',
                        '25': 'Suspensão temporária do contrato',
                    }
                    descricao_motivo = descricoes_motivo.get(codigo_motivo, 'Motivo não especificado')
                    
                    # Dados do término do afastamento (se houver)
                    termino = encontrar_elemento(info_afastamento, "fimAfastamento")
                    data_fim = obter_texto_elemento(termino, "dtTermAfast") if termino else ""
                    
                    # Montar dicionário com os dados
                    afastamento_dict = {
                        'cpf_trabalhador': cpf_trabalhador,
                        'matricula': matricula,
                        'data_inicio': data_inicio,
                        'data_fim': data_fim,
                        'codigo_motivo': codigo_motivo,
                        'descricao_motivo': descricao_motivo,
                        'cnpj_empregador': cnpj_empregador,
                        'json_data': json.dumps(self._elemento_para_dict(info_afastamento))
                    }
                    
                    afastamentos_list.append(afastamento_dict)
            
            # Inserir no banco de dados
            if afastamentos_list:
                self.gerenciador_bd.inserir_dados("esocial_s2230", afastamentos_list)
                return True
                
            return False
            
        except Exception as e:
            self.logger.error(f"Erro ao processar S-2230 {caminho_arquivo}: {e}", exc_info=True)
            return False
    
    def _processar_s2299(self, root, caminho_arquivo):
        """Processa arquivo XML do layout S-2299 (Desligamento)"""
        try:
            # Extrair CNPJ do empregador
            ide_empregador = encontrar_elemento(root, "ideEmpregador")
            cnpj_empregador = obter_texto_elemento(ide_empregador, "nrInsc") if ide_empregador else ""
            
            # Extrair dados do trabalhador
            ide_vinculo = encontrar_elemento(root, "ideVinculo")
            cpf_trabalhador = obter_texto_elemento(ide_vinculo, "cpfTrab") if ide_vinculo else ""
            matricula = obter_texto_elemento(ide_vinculo, "matricula") if ide_vinculo else ""
            
            # Dados do desligamento
            info_deslig = encontrar_elemento(root, "infoDeslig")
            if info_deslig is None:
                self.logger.warning(f"Dados de desligamento não encontrados em {caminho_arquivo}")
                return False
                
            # Data do desligamento
            data_desligamento = obter_texto_elemento(info_deslig, "dtDeslig")
            
            # Motivo do desligamento
            motivo_desligamento = obter_texto_elemento(info_deslig, "mtvDeslig")
            descricao_motivo = self._obter_descricao_motivo_desligamento(motivo_desligamento)
            
            # Aviso prévio
            aviso_previo = encontrar_elemento(info_deslig, "infoAvPrevio")
            data_aviso = obter_texto_elemento(aviso_previo, "dtAvPrv") if aviso_previo else ""
            
            # Dados de rescisão
            valores_rescisao = {}
            verba_rescisoria = encontrar_elemento(info_deslig, "verbasResc")
            
            if verba_rescisoria is not None:
                # Processar verbas rescisórias (saldo, férias, décimo terceiro, etc.)
                dmdev_elements = encontrar_todos_elementos(verba_rescisoria, "dmDev")
                for dmdev in dmdev_elements:
                    id_dmdev = obter_texto_elemento(dmdev, "ideDmDev")
                    
                    # Processar cada item da rescisão
                    itens_remuneracao = encontrar_todos_elementos(dmdev, "itensRemun")
                    for item in itens_remuneracao:
                        cod_rubrica = obter_texto_elemento(item, "codRubr")
                        valor_str = obter_texto_elemento(item, "vrRubr")
                        
                        try:
                            valor = float(valor_str.replace(',', '.'))
                        except (ValueError, AttributeError, TypeError):
                            valor = 0.0
                        
                        # Armazenar a rubrica
                        valores_rescisao[cod_rubrica] = valor
            
            # Calcular valor total da rescisão (soma de todas as rubricas)
            valor_total_rescisao = sum(valores_rescisao.values())
            
            # Informações de FGTS
            info_fgts = encontrar_elemento(info_deslig, "infoPerApur")
            valor_multa_fgts = 0.0
            
            # Montar dicionário com os dados do desligamento
            desligamento_dict = {
                'cpf_trabalhador': cpf_trabalhador,
                'matricula': matricula,
                'data_desligamento': data_desligamento,
                'motivo_desligamento': motivo_desligamento,
                'descricao_motivo': descricao_motivo,
                'data_aviso_previo': data_aviso,
                'valor_rescisao': valor_total_rescisao,
                'valor_multa_fgts': valor_multa_fgts,
                'cnpj_empregador': cnpj_empregador,
                'json_data': json.dumps(self._elemento_para_dict(root))
            }
            
            # Validar dados do desligamento
            valido, mensagens_erro = ValidadorDados.validar_registro_s2299(desligamento_dict)
            if not valido:
                for erro in mensagens_erro:
                    self.logger.warning(f"Validação para CPF {cpf_trabalhador}, arquivo {caminho_arquivo}: {erro}")
                
                # Tentar corrigir dados problemáticos
                desligamento_dict = ValidadorDados.sanitizar_dados(desligamento_dict, 'S-2299')
                
                # Revalidar após correções
                valido, mensagens_erro = ValidadorDados.validar_registro_s2299(desligamento_dict)
                if not valido:
                    self.logger.warning(f"Dados ainda apresentam problemas após correções: {', '.join(mensagens_erro)}")
                else:
                    self.logger.info(f"Dados corrigidos com sucesso para CPF {cpf_trabalhador}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao processar S-2299 {caminho_arquivo}: {e}", exc_info=True)
            return False
    
    def _obter_descricao_motivo_desligamento(self, codigo_motivo):
        """Retorna a descrição do motivo de desligamento baseado no código"""
        descricoes = {
            '01': 'Rescisão com justa causa por iniciativa do empregador',
            '02': 'Rescisão sem justa causa por iniciativa do empregador',
            '03': 'Rescisão antecipada do contrato a termo por iniciativa do empregador',
            '04': 'Rescisão por culpa recíproca',
            '05': 'Rescisão por força maior',
            '06': 'Rescisão por término de contrato a termo',
            '07': 'Rescisão do contrato de trabalho por iniciativa do empregado',
            '08': 'Rescisão do contrato de trabalho por interesse do empregado',
            '09': 'Rescisão por falecimento do empregado',
            '10': 'Rescisão por falecimento do empregador individual',
            '11': 'Transferência de empregado para empresa do mesmo grupo',
            '12': 'Transferência de empregado para outra empresa',
            '13': 'Rescisão contratual a pedido do empregado, durante o período de experiência',
            '14': 'Rescisão contratual por encerramento da empresa',
        }
        return descricoes.get(codigo_motivo, 'Motivo não especificado')
    
    def _elemento_para_dict(self, elem):
        """Converte um elemento XML para dicionário"""
        if elem is None:
            return None
            
        result = {}
        
        # Atributos do elemento
        result.update(elem.attrib)
        
        # Texto do elemento
        if elem.text and elem.text.strip():
            result['_text'] = elem.text.strip()
            
        # Elementos filhos
        for child in elem:
            child_dict = self._elemento_para_dict(child)
            
            # Nome do elemento filho
            tag = child.tag
            if '}' in tag:
                tag = tag.split('}')[1]
                
            # Adicionar ao resultado
            if tag in result:
                # Se já existe uma chave com este nome, transformar em lista
                if not isinstance(result[tag], list):
                    result[tag] = [result[tag]]
                result[tag].append(child_dict)
            else:
                result[tag] = child_dict
                
        return result
    
    def detectar_layout_xml(self, caminho_arquivo: str) -> str:
        """
        Detecta o layout do XML a partir do caminho do arquivo.
        """
        try:
            tree = ET.parse(caminho_arquivo)
            root = tree.getroot()
            return identificar_layout(root)
        except Exception as e:
            self.logger.error(f"Erro ao detectar layout do XML: {e}")
            return None

    def extrair_dados_xml(self, caminho_arquivo: str) -> dict:
        """
        Extrai os dados do XML e retorna como dicionário.
        """
        try:
            tree = ET.parse(caminho_arquivo)
            root = tree.getroot()
            # Converte o XML para dict (simples)
            def elem_to_dict(elem):
                d = {elem.tag.split('}')[-1]: {}}
                children = list(elem)
                if children:
                    dd = {}
                    for dc in map(elem_to_dict, children):
                        for k, v in dc.items():
                            if k in dd:
                                if not isinstance(dd[k], list):
                                    dd[k] = [dd[k]]
                                dd[k].append(v)
                            else:
                                dd[k] = v
                    d = {elem.tag.split('}')[-1]: dd}
                if elem.text and elem.text.strip():
                    d[elem.tag.split('}')[-1]]['_text'] = elem.text.strip()
                d[elem.tag.split('}')[-1]].update(elem.attrib)
                return d
            return elem_to_dict(root)
        except Exception as e:
            self.logger.error(f"Erro ao extrair dados do XML: {e}")
            return {}
