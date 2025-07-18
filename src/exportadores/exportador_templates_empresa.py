"""
Exportador específico para templates da Empresa
Gera os 9 CSVs conforme especificado na proposta técnica
"""

import os
import re
import logging
import csv
import pandas as pd
import json
import types
import traceback
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Callable
from datetime import datetime

from utils.mapeador_campos_empresa import MapeadorCamposEmpresa
from configuracao.configuracoes import Configuracoes


class ExportadorTemplatesEmpresa:
    """
    Exportador específico para os templates da Empresa
    Gera exatamente os 9 CSVs conforme especificado na proposta
    """
    
    def __init__(self, gerenciador_bd=None, configuracoes=None):
        """
        Inicializa o exportador de templates Empresa
        
        Args:
            gerenciador_bd: Gerenciador de banco de dados
            configuracoes: Configurações da aplicação
        """
        self.gerenciador_bd = gerenciador_bd
        self.configuracoes = configuracoes or Configuracoes()
        self.logger = logging.getLogger(__name__)
        
        # Inicializar mapeador de campos
        self.mapeador = MapeadorCamposEmpresa()
        
        # Garantir que o diretório de saída existe
        self._caminho_saida = self.configuracoes.CAMINHO_SAIDA
        self.logger.info(f"[DEBUG] Inicializando exportador com CAMINHO_SAIDA: {self._caminho_saida}")
        self.logger.info(f"[DEBUG] Tipo de CAMINHO_SAIDA: {type(self._caminho_saida)}")
        
        if self._caminho_saida is None:
            raise ValueError("CAMINHO_SAIDA não pode ser None")
        
        self._caminho_saida.mkdir(parents=True, exist_ok=True)
        
        # A pasta de saída agora é diretamente o diretório de saída raiz
        self.pasta_csv = self._caminho_saida
        self.logger.info(f"[DEBUG] pasta_csv definida como: {self.pasta_csv}")
        
        # Inicializa o caminho dos templates
        self.caminho_templates = self.configuracoes.CAMINHO_TEMPLATES
        self.caminho_templates.mkdir(parents=True, exist_ok=True)
        
        # Inicializa templates obrigatórios
        self.templates_obrigatorios = [
            "01_CONVTRABALHADOR.csv",
            "02_CONVCONTRATO.csv",
            "03_CONVCONTRATOALT.csv",
            "04_CONVDEPENDENTE.csv",
            "05_FERIAS.csv",
            "06_CONVFICHA.csv",
            "07_CARGOS.csv",
            "08_CONVAFASTAMENTO.csv",
            "09_CONVATESTADO.csv"
        ]
    
    @property
    def caminho_saida(self):
        """Getter para o caminho de saída"""
        return self._caminho_saida
    
    @caminho_saida.setter
    def caminho_saida(self, novo_caminho):
        """Setter para o caminho de saída que também atualiza pasta_csv"""
        self._caminho_saida = Path(novo_caminho) if isinstance(novo_caminho, str) else novo_caminho
        self._caminho_saida.mkdir(parents=True, exist_ok=True)
        self.pasta_csv = self._caminho_saida
        
        # Verificar templates CSV disponíveis fisicamente (opcional)
        self._verificar_templates_disponiveis()
    
    def exportar_todos_templates(self) -> int:
        """
        Exporta todos os 9 templates obrigatórios
        
        Returns:
            Número de templates processados com sucesso
        """
        self.logger.info(f"Iniciando exportação de templates para: {self.caminho_saida}")
        
        templates_processados = 0
        
        for nome_template in self.templates_obrigatorios:
            try:
                self.logger.info(f"Processando template: {nome_template}")
                
                # Ler estrutura do template (do arquivo ou configuração)
                colunas_template = self._ler_colunas_template(nome_template)
                
                if not colunas_template:
                    self.logger.error(f"Template {nome_template}: Não foi possível ler as colunas (nem do arquivo nem da configuração)")
                    self._criar_arquivo_vazio(nome_template, [])
                    continue
                    
                self.logger.info(f"Template {nome_template}: Usando {len(colunas_template)} colunas para exportação")
                
                # Gerar dados baseado no tipo de template
                dados = self._gerar_dados_template(nome_template, colunas_template)
                
                # Salvar o arquivo CSV na pasta específica
                self._salvar_template_csv(nome_template, colunas_template, dados)
                
                self.logger.info(f"Template {nome_template}: Exportado {len(dados)} registros")
                templates_processados += 1
                
            except Exception as e:
                self.logger.error(f"Erro ao processar template {nome_template}: {e}", exc_info=True)
                # Criar arquivo vazio em caso de erro
                self._criar_arquivo_vazio(nome_template, [])
        
        # Finalizar exportação
        self._finalizar_exportacao()
        
        self.logger.info(f"Exportação concluída: {templates_processados} templates processados")
        return templates_processados
    
    def _ler_colunas_template(self, nome_template: str) -> List[str]:
        """
        Lê as colunas do arquivo template.
        Primeiro tenta ler do arquivo físico e, caso não exista, usa as definições de configuração.
        
        Args:
            nome_template: Nome do arquivo template
            
        Returns:
            Lista com os nomes das colunas
        """
        caminho_template = self.caminho_templates / nome_template
        
        # Tenta ler do arquivo físico primeiro
        if caminho_template.exists():
            try:
                with open(caminho_template, 'r', encoding='utf-8-sig') as arquivo:
                    leitor = csv.reader(arquivo, delimiter=';')
                    primeira_linha = next(leitor, [])
                    
                    if primeira_linha:
                        # Limpar e normalizar nomes das colunas
                        colunas = [col.strip() for col in primeira_linha if col.strip()]
                        self.logger.info(f"Template {nome_template}: {len(colunas)} colunas lidas do arquivo físico")
                        return colunas
                        
            except Exception as e:
                self.logger.error(f"Erro ao ler template {nome_template}: {e}")
        
        # Se não conseguiu ler do arquivo físico, tenta usar a configuração
        if nome_template in self.configuracoes.COLUNAS_TEMPLATES:
            colunas = self.configuracoes.COLUNAS_TEMPLATES[nome_template]
            self.logger.info(f"Template {nome_template}: {len(colunas)} colunas obtidas da configuração")
            return colunas
        
        # Se não encontrou no arquivo nem na configuração, retorna vazio
        self.logger.warning(f"Template não encontrado: {caminho_template} e não definido nas configurações")
        return []
    
    def _extrair_valor_prioritario(self, registro: dict, coluna: str, chave_template: str) -> Any:
        """
        Extrai o valor de um campo priorizando a coluna do banco, depois o JSON, depois valor padrão.
        """
        # 1. Tenta pegar direto da coluna do banco
        if coluna in registro and registro[coluna] not in (None, ""):
            return registro[coluna]
        # 2. Tenta via mapeador (JSON)
        valor = self.mapeador.obter_valor_campo(chave_template, coluna, registro)
        if valor not in (None, ""):
            return valor
        # 3. Valor padrão
        mapeamento = self.mapeador.mapeamentos.get(chave_template, {})
        campos = mapeamento.get("campos", {})
        return campos.get(coluna, {}).get("valor_padrao", "")

    def _extrair_array_para_template(self, dados, colunas, chave_template, metodo_extracao, array_nome_log):
        """
        Helper para extrair arrays do JSON e gerar linhas para o template.
        Garante que todos os campos das colunas sejam preenchidos.
        
        Args:
            dados: Lista de registros do banco
            colunas: Lista de colunas do template
            chave_template: Nome do template sem extensão
            metodo_extracao: Método ou função para extrair itens do array no JSON
            array_nome_log: Nome do tipo de array para logs
            
        Returns:
            Lista de registros para o template
        """
        dados_filtrados = []
        total_itens_extraidos = 0
        registros_processados = 0
        
        for registro in dados:
            registros_processados += 1
            json_str = registro.get('json_data')
            itens = []
            
            if json_str:
                try:
                    # Se metodo_extracao é uma string, tenta usar getattr
                    if isinstance(metodo_extracao, str):
                        func = getattr(self.mapeador, metodo_extracao, None)
                        if func and callable(func):
                            itens = func(json_str)
                        else:
                            self.logger.warning(f"Método '{metodo_extracao}' não encontrado no mapeador")
                            itens = []
                    else:
                        # Caso contrário, assume que é uma função direta
                        itens = metodo_extracao(json_str)
                    
                    if itens and isinstance(itens, list) and len(itens) > 0:
                        total_itens_extraidos += len(itens)
                        self.logger.debug(f"Extraídos {len(itens)} {array_nome_log} do registro {registros_processados}")
                except Exception as e:
                    self.logger.error(f"Erro ao extrair {array_nome_log} do JSON: {e}")
                    self.logger.debug(f"JSON problemático (primeiros 200 chars): {str(json_str)[:200]}...")
            
            if not itens or not isinstance(itens, list) or len(itens) == 0:
                # Se não extraiu itens, tenta usar os dados do próprio registro
                reg_map = {}
                for coluna in colunas:
                    reg_map[coluna] = self._extrair_valor_prioritario(registro, coluna, chave_template)
                dados_filtrados.append(reg_map)
                self.logger.debug(f"Registro {registros_processados}: Sem {array_nome_log}, usando dados do registro principal")
            else:
                # Para cada item extraído, gera uma linha completa
                for item in itens:
                    if item and isinstance(item, dict):
                        reg_map = {}
                        registro_completo = dict(registro)
                        registro_completo.update(item)
                        for coluna in colunas:
                            valor = self._extrair_valor_prioritario(registro_completo, coluna, chave_template)
                            reg_map[coluna] = valor
                        dados_filtrados.append(reg_map)
        
        self.logger.info(f"{array_nome_log.capitalize()} extraídos: {len(dados_filtrados)} registros de {total_itens_extraidos} itens em {registros_processados} registros base")
        
        # Verificar se há registros com todos os campos vazios
        registros_vazios = 0
        for reg in dados_filtrados:
            valores = [v for v in reg.values() if v not in (None, "")]
            if not valores:
                registros_vazios += 1
        
        if registros_vazios > 0:
            self.logger.warning(f" {registros_vazios} registros estão completamente vazios em {array_nome_log}")
        
        return dados_filtrados

    def _gerar_dados_template(self, nome_template: str, colunas: list) -> list:
        """
        Gera dados para qualquer template usando o mapeamento centralizado do MapeadorCamposEmpresa.
        Para cada coluna, tenta extrair o valor do registro do banco de dados e do json_data usando o mapeamento.
        Se não encontrar, deixa vazio. Adiciona comentários de código para clareza.
        """
        mapeador = MapeadorCamposEmpresa()
        # Remove .csv extension for mapping lookup
        nome_template_sem_ext = nome_template.replace('.csv', '')
        # Usar exportar_dados para buscar registros
        fonte = mapeador.mapeamentos.get(nome_template_sem_ext, {}).get('fonte_principal', '')
        if not fonte:
            self.logger.warning(f"Fonte de dados não definida para {nome_template}")
            return []
        dados = self.gerenciador_bd.exportar_dados(fonte)
        if not dados:
            self.logger.warning(f"Nenhum registro encontrado para {nome_template}")
            return []
        registros_processados = []
        for idx, registro in enumerate(dados):
            linha = {}
            json_str = registro.get("json_data", "{}")
            try:
                import json
                json_data = json.loads(json_str) if isinstance(json_str, str) else json_str
            except Exception:
                json_data = {}
            for coluna in colunas:
                valor = mapeador.obter_valor_campo(nome_template_sem_ext, coluna, registro)
                if valor is None or (isinstance(valor, str) and not valor.strip()):
                    valor = mapeador._extrair_valor_json_com_alternativos(json_data, mapeador.mapeamentos.get(nome_template_sem_ext, {}).get('campos', {}).get(coluna, {}))
                linha[coluna] = valor if valor is not None else ""
            registros_processados.append(linha)
        self.logger.info(f"[DEBUG] {nome_template}: {len(registros_processados)} registros processados/exportados.")
        # Log the first 5 rows for inspection
        for i, row in enumerate(registros_processados[:5]):
            self.logger.info(f"[DEBUG] {nome_template} row {i+1}: {row}")
        return registros_processados

    def _gerar_dados_dependente(self, colunas: List[str]) -> List[Dict[str, Any]]:
        """Gera dados para o template de dependentes usando a tabela esocial_dependentes - 100% Coverage"""
        dependentes_processados = []
        
        # Buscar dados diretamente da tabela esocial_dependentes
        self.logger.info("Buscando dados da tabela esocial_dependentes...")
        registros = self.gerenciador_bd.exportar_dados('esocial_dependentes')
        
        if not registros:
            self.logger.warning("Nenhum registro encontrado na tabela esocial_dependentes")
            return []
            
        self.logger.info(f"Processando {len(registros)} registros da tabela esocial_dependentes")
        self.logger.debug(f"Primeiro registro: {registros[0] if registros else 'N/A'}")
        
        for registro in registros:
            try:
                # Extrair dados básicos do registro
                cpf_trabalhador = registro.get("cpf_trabalhador", "")
                cnpj_empregador = registro.get("cnpj_empregador", "")
                matricula = registro.get("matricula", "")
                nome_dependente = registro.get("nome_dependente", "")
                cpf_dependente = registro.get("cpf_dependente", "")
                tipo_dependente = registro.get("tipo_dependente", "")
                sexo_dependente = registro.get("sexo_dependente", "")
                data_nascimento = registro.get("data_nascimento", "")
                dep_irrf = registro.get("dep_irrf", "")
                dep_sf = registro.get("dep_sf", "")
                inc_trab = registro.get("inc_trab", "")
                descr_dep = registro.get("descr_dep", "")
                
                self.logger.debug(f"Processando dependente: {nome_dependente} (CPF: {cpf_dependente})")
                
                # Criar registro de dependente para o template
                dependente = {}
                for coluna in colunas:
                    # Mapear cada coluna do template para o valor correspondente
                    if coluna == "1 A-ID do empregador":
                        dependente[coluna] = cnpj_empregador
                    elif coluna == "2 B  - Código do trabalhador":
                        dependente[coluna] = cpf_trabalhador
                    elif coluna == "3 C  - Código do tipo de dependente":
                        dependente[coluna] = tipo_dependente
                    elif coluna == "4 D  - Código do dependente":
                        dependente[coluna] = cpf_dependente
                    elif coluna == "5 E  - Nome do dependente":
                        dependente[coluna] = nome_dependente
                    elif coluna == "6 F  - Início da vigência":
                        dependente[coluna] = ""  # Não disponível no S-2200
                    elif coluna == "7 G  - Término da vigência":
                        dependente[coluna] = ""  # Não disponível no S-2200
                    elif coluna == "8 H  - Sexo do dependente":
                        dependente[coluna] = sexo_dependente
                    elif coluna == "9 I  - Data de nascimento do dependente":
                        dependente[coluna] = data_nascimento
                    elif coluna == "10 J  - Nome da mãe":
                        dependente[coluna] = ""  # Não disponível no S-2200
                    elif coluna == "11 K  - CPF do dependente":
                        dependente[coluna] = cpf_dependente
                    elif coluna == "12 L  - Paga salário família":
                        dependente[coluna] = dep_sf
                    elif coluna == "13 M  - Data de baixa do salário  família":
                        dependente[coluna] = ""  # Não disponível no S-2200
                    elif coluna == "14 N  - Dependente para IRRF":
                        dependente[coluna] = dep_irrf
                    elif coluna == "15 O  - Data de baixa de dependente para IRRF":
                        dependente[coluna] = ""  # Não disponível no S-2200
                    elif coluna == "16 P  - Filho deficiente recebe salário família":
                        dependente[coluna] = ""  # Não disponível no S-2200
                    elif coluna == "17 Q  - Código da cidade de nascimento":
                        dependente[coluna] = ""  # Não disponível no S-2200
                    elif coluna == "18 R  - Número da certidão de nascimento do dependente":
                        dependente[coluna] = ""  # Não disponível no S-2200
                    elif coluna == "19 S  - Nome do cartório de registro":
                        dependente[coluna] = ""  # Não disponível no S-2200
                    elif coluna == "20 T  - Número de registro":
                        dependente[coluna] = ""  # Não disponível no S-2200
                    elif coluna == "21 U  - Número no livro de registro":
                        dependente[coluna] = ""  # Não disponível no S-2200
                    elif coluna == "22 V  - Número na folha de registro":
                        dependente[coluna] = ""  # Não disponível no S-2200
                    elif coluna == "23 W  - Data de registro em cartório":
                        dependente[coluna] = ""  # Não disponível no S-2200
                    elif coluna == "24 X  - Data de entrega do documento":
                        dependente[coluna] = ""  # Não disponível no S-2200
                    elif coluna == "25 Y  - Endereço do dependente":
                        dependente[coluna] = ""  # Não disponível no S-2200
                    elif coluna == "26 Z  - Número de endereço":
                        dependente[coluna] = ""  # Não disponível no S-2200
                    elif coluna == "27 AA  - Bairro":
                        dependente[coluna] = ""  # Não disponível no S-2200
                    elif coluna == "28 AB  - Código da cidade":
                        dependente[coluna] = ""  # Não disponível no S-2200
                    elif coluna == "29 AC  - CEP do dependente":
                        dependente[coluna] = ""  # Não disponível no S-2200
                    elif coluna == "30 AD  - Telefone 1 do dependente":
                        dependente[coluna] = ""  # Não disponível no S-2200
                    elif coluna == "31 AE  - Telefone 2 do dependente":
                        dependente[coluna] = ""  # Não disponível no S-2200
                    elif coluna == "32 AF  - Observações":
                        dependente[coluna] = descr_dep
                    elif coluna == "33 AG  - Data de registro":
                        dependente[coluna] = ""  # Não disponível no S-2200
                    elif coluna == "34 AH  - Número do cartão nacional de saúde":
                        dependente[coluna] = ""  # Não disponível no S-2200
                    elif coluna == "35 AI  - Número da declaração de nascimento vivo":
                        dependente[coluna] = ""  # Não disponível no S-2200
                    elif coluna == "36 AJ  - Número do RG do dependente":
                        dependente[coluna] = ""  # Não disponível no S-2200
                    elif coluna == "37 AK  - Origem":
                        dependente[coluna] = ""  # Não disponível no S-2200
                    elif coluna == "38 AL  - Destino":
                        dependente[coluna] = ""  # Não disponível no S-2200
                    else:
                        dependente[coluna] = ""  # Preencher vazio para qualquer coluna extra
                
                dependentes_processados.append(dependente)
                self.logger.debug(f"Dependente processado: {nome_dependente}")
                
            except Exception as e:
                self.logger.warning(f"Erro ao processar dependente: {e}")
                continue
        
        # Garantir que todas as colunas estão presentes
        for dependente in dependentes_processados:
            for coluna in colunas:
                if coluna not in dependente:
                    dependente[coluna] = ""
        
        self.logger.info(f"Total de {len(dependentes_processados)} dependentes processados para o template")
        return dependentes_processados

    def _gerar_dados_ferias(self, colunas: List[str]) -> List[Dict[str, Any]]:
        """Gera dados para o template de férias (S-2230 com férias)"""
        ferias_processadas = []
        
        # Buscar registros de afastamento relacionados a férias
        registros = self.gerenciador_bd.exportar_dados('esocial_s2230')
        
        if not registros:
            self.logger.warning("Nenhum registro de afastamento (S-2230) encontrado para férias")
            return []
            
        self.logger.info(f"Encontrados {len(registros)} registros de afastamentos para processamento de férias")
        
        # Para cada registro de afastamento
        for registro in registros:
            json_str = registro.get("json_data", "{}")
            
            try:
                # Extrair informações básicas do registro
                cnpj_empregador = registro.get("cnpj_empregador", "")
                cpf_trabalhador = registro.get("cpf_trabalhador", "")
                data_inicio = registro.get("data_inicio", "")
                data_fim = registro.get("data_fim", "")
                
                # Verificar se temos pelo menos os dados básicos
                if not cnpj_empregador or not cpf_trabalhador or not data_inicio:
                    continue
                
                # Analisar o JSON para verificar se é afastamento de férias
                import json
                dados_json = json.loads(json_str) if isinstance(json_str, str) else json_str
                
                # Buscar o motivo do afastamento em diferentes caminhos
                motivo_afastamento = None
                caminhos_motivo = [
                    ["evtAfastTemp", "infoAfastamento", "iniAfastamento", "infoAfastamento", "codMotAfast", "_text"],
                    ["infoAfastamento", "iniAfastamento", "infoAfastamento", "codMotAfast", "_text"],
                    ["iniAfastamento", "infoAfastamento", "codMotAfast", "_text"]
                ]
                
                for caminho in caminhos_motivo:
                    temp = dados_json
                    for parte in caminho:
                        if isinstance(temp, dict) and parte in temp:
                            temp = temp[parte]
                        else:
                            temp = None
                            break
                    if temp:
                        motivo_afastamento = temp
                        break
                
                # Verificar se é férias (código 30)
                if motivo_afastamento == '30' or motivo_afastamento == '31':
                    # Criar registro de férias
                    ferias = {
                        "1 A-ID do empregador": cnpj_empregador,
                        "2 B-CPF trabalhador": cpf_trabalhador,
                        "3 C-Data início": data_inicio,
                        "4 D-Data fim": data_fim,
                        "5 E-Dias de férias": "",
                        "6 F-Abono pecuniário": "N",
                        "7 G-Dias de abono": "0",
                        "8 H-Férias coletivas": "N"
                    }
                    
                    # Calcular dias de férias
                    if data_inicio and data_fim:
                        try:
                            from datetime import datetime
                            d1 = datetime.strptime(data_inicio, "%Y-%m-%d")
                            d2 = datetime.strptime(data_fim, "%Y-%m-%d")
                            dias = (d2 - d1).days + 1
                            ferias["5 E-Dias de férias"] = str(dias)
                        except Exception as e:
                            self.logger.warning(f"Erro ao calcular dias de férias: {e}")
                    
                    # Verificar se há informações adicionais no JSON sobre abono
                    # Esta parte pode ser expandida conforme as especificidades dos dados
                    
                    # Adicionar o registro
                    ferias_processadas.append(ferias)
                    
            except Exception as e:
                self.logger.error(f"Erro ao processar registro de férias: {e}")
        
        # Completar campos com valores padrão
        for ferias in ferias_processadas:
            for coluna in colunas:
                if coluna not in ferias:
                    ferias[coluna] = ""
        
        self.logger.info(f"Total de {len(ferias_processadas)} períodos de férias processados")
        return ferias_processadas

    def _gerar_dados_ficha_financeira(self, colunas: List[str]) -> List[Dict[str, Any]]:
        """Gera dados para o template de ficha financeira (S-1200) - 100% Coverage"""
        fichas_processadas = []
        registros = self.gerenciador_bd.exportar_dados('esocial_s1200')
        if not registros:
            self.logger.warning("Nenhum registro de pagamento (S-1200) encontrado")
            return []
        self.logger.info(f"Encontrados {len(registros)} registros de pagamento para processamento de ficha financeira")
        for registro in registros:
            json_str = registro.get("json_data", "{}")
            try:
                import json
                dados_json = json.loads(json_str) if isinstance(json_str, str) else json_str
                cnpj_empregador = registro.get("cnpj_empregador", "")
                cpf_trabalhador = registro.get("cpf_trabalhador", "")
                periodo_apuracao = registro.get("periodo_apuracao", "")
                estabelecimento = registro.get("estabelecimento", "")
                matricula = registro.get("matricula", "")
                categoria = registro.get("categoria", "")
                codigo_rubrica = registro.get("codigo_rubrica", "")
                descricao_rubrica = registro.get("descricao_rubrica", "")
                valor_rubrica = registro.get("valor_rubrica", "")
                tipo_rubrica = registro.get("tipo_rubrica", "")
                # Mapear todos os campos do template 06_CONVFICHA.csv
                ficha = {}
                for coluna in colunas:
                    # Mapear cada coluna do template para o valor correspondente
                    if coluna == '1 A-ID do empregador':
                        ficha[coluna] = cnpj_empregador
                    elif coluna == '2 B-Código do estabelecimento':
                        ficha[coluna] = estabelecimento
                    elif coluna == '3 C - Código do tipo de cálculo':
                        ficha[coluna] = ''  # Não disponível
                    elif coluna == '4 D  - Data do pagamento':
                        ficha[coluna] = ''  # Não disponível
                    elif coluna == '5 E  - Data inicial do cálculo':
                        ficha[coluna] = ''  # Não disponível
                    elif coluna == '6 F  - Data final do cálculo':
                        ficha[coluna] = ''  # Não disponível
                    elif coluna == '7 G  - Data de cálculo da folha':
                        ficha[coluna] = ''  # Não disponível
                    elif coluna == '8 H  - Data recolhimento da GRRF':
                        ficha[coluna] = ''  # Não disponível
                    elif coluna == '9 I  - Observações sobre o cálculo':
                        ficha[coluna] = ''  # Não disponível
                    elif coluna == '10 J-Código do contrato':
                        ficha[coluna] = matricula
                    elif coluna == '11 K  - Código do cargo':
                        ficha[coluna] = ''  # Não disponível
                    elif coluna == '12 L  - Código da função':
                        ficha[coluna] = ''  # Não disponível
                    elif coluna == '13 M  - Código do departamento':
                        ficha[coluna] = ''  # Não disponível
                    elif coluna == '14 N  - Código da jornada de trabalho':
                        ficha[coluna] = ''  # Não disponível
                    elif coluna == '15 O  - Código do sindicato':
                        ficha[coluna] = ''  # Não disponível
                    elif coluna == '16 P  - Valor do salário':
                        ficha[coluna] = ''  # Não disponível
                    elif coluna == '17 Q  - Tipo de salário':
                        ficha[coluna] = ''  # Não disponível
                    elif coluna == '18 R  - Qtde de horas contratuais mensais':
                        ficha[coluna] = ''  # Não disponível
                    elif coluna == '19 S  - Qtde dependentes para IR':
                        ficha[coluna] = ''  # Não disponível
                    elif coluna == '20 T  - Qtde dependentes para SF':
                        ficha[coluna] = ''  # Não disponível
                    elif coluna == '21 U  - Código de exposição à agentes nocivos':
                        ficha[coluna] = ''  # Não disponível
                    elif coluna == '22 V  - Grau de insalubridade':
                        ficha[coluna] = ''  # Não disponível
                    elif coluna == '23 W  - Tem periculosidade':
                        ficha[coluna] = ''  # Não disponível
                    elif coluna == '24 X  - Ensejo de aposentadoria especial':
                        ficha[coluna] = ''  # Não disponível
                    elif coluna == '25 Y  - Sigla da rubrica':
                        ficha[coluna] = codigo_rubrica
                    elif coluna == '26 Z  - Sigla da rubrica para o recibo':
                        ficha[coluna] = codigo_rubrica
                    elif coluna == '27 AA  - Descrição da rubrica para o recibo':
                        ficha[coluna] = descricao_rubrica
                    elif coluna == '28 AB  - Razão ou qtde':
                        ficha[coluna] = ''  # Não disponível
                    elif coluna == '29 AC  - Valor da rubrica':
                        ficha[coluna] = valor_rubrica
                    elif coluna == '30 AD  - Classe da rubrica':
                        ficha[coluna] = tipo_rubrica
                    elif coluna == '31 AE  - Período de referência':
                        ficha[coluna] = periodo_apuracao
                    else:
                        ficha[coluna] = ''  # Preencher vazio para qualquer coluna extra
                fichas_processadas.append(ficha)
            except Exception as e:
                self.logger.error(f"Erro ao processar registro de ficha financeira: {e}")
        self.logger.info(f"Total de {len(fichas_processadas)} rubricas processadas para ficha financeira")
        return fichas_processadas

    def _gerar_dados_cargos(self, colunas: List[str]) -> List[Dict[str, Any]]:
        """Gera dados para o template de cargos (S-1030) - 100% Coverage"""
        cargos_processados = []
        
        # Buscar registros de cargos
        registros = self.gerenciador_bd.exportar_dados('esocial_s1030')
        
        if not registros:
            self.logger.warning("Nenhum registro de cargo (S-1030) encontrado")
            return []
            
        self.logger.info(f"Encontrados {len(registros)} registros de cargo para processamento")
        
        # Para cada registro de cargo
        for registro in registros:
            try:
                # Extrair informações básicas do registro
                cnpj_empregador = registro.get("cnpj_empregador", "")
                codigo = registro.get("codigo", "")
                descricao = registro.get("descricao", "")
                inicio_validade = registro.get("inicio_validade", "")
                fim_validade = registro.get("fim_validade", "")
                cbo = registro.get("cbo", "")
                
                # Extrair informações complementares do registro
                cargo_publico = registro.get("cargo_publico", "")
                nivel_cargo = registro.get("nivel_cargo", "")
                desc_sumaria = registro.get("desc_sumaria", "")
                situacao = registro.get("situacao", "")
                permite_acumulo = registro.get("permite_acumulo", "")
                permite_contagem_esp = registro.get("permite_contagem_esp", "")
                dedicacao_exclusiva = registro.get("dedicacao_exclusiva", "")
                num_lei = registro.get("num_lei", "")
                dt_lei = registro.get("dt_lei", "")
                situacao_lei = registro.get("situacao_lei", "")
                tem_funcao = registro.get("tem_funcao", "")
                
                # Criar registro do cargo com todos os campos disponíveis
                cargo = {
                    "1 A-ID do empregador": cnpj_empregador,
                    "2 B-Código do cargo": codigo,
                    "3 C-Nome do cargo": descricao,
                    "4 D-ID do tipo de código": "",  # Campo não disponível no S-1030
                    "5 E-ID do nível organizacional": nivel_cargo,
                    "6 F-Código do CBO": cbo,
                    "7 G-Início da validade": inicio_validade,
                    "8 H-Término da validade": fim_validade or "",
                    "9 I-Descrição sumária": desc_sumaria,
                    "10 J-Permite acúmulo de cargo": permite_acumulo,
                    "11 L-Permite contagem especial do acúmulo de cargo": permite_contagem_esp,
                    "12 M-Cargo de dedicação exclusiva": dedicacao_exclusiva,
                    "13 N-Número da Lei que criou e/ou extinguiu e/ou restruturou o": num_lei,
                    "14 O-Data da Lei que criou e/ou extinguiu e/ou restruturou o ca": dt_lei,
                    "15 P-Situação gerada pela Lei": situacao_lei,
                    "16 Q-O cargo tem função": tem_funcao
                }
                
                # Verificar dados mínimos
                if cnpj_empregador and codigo and descricao:
                    cargos_processados.append(cargo)
                
            except Exception as e:
                self.logger.error(f"Erro ao processar registro de cargo: {e}")
        
        # Completar campos com valores padrão
        for cargo in cargos_processados:
            for coluna in colunas:
                if coluna not in cargo:
                    cargo[coluna] = ""
        
        self.logger.info(f"Total de {len(cargos_processados)} cargos processados")
        return cargos_processados

    def _gerar_dados_afastamentos(self, colunas: List[str]) -> List[Dict[str, Any]]:
        """Gera dados para o template de afastamentos (S-2230)"""
        afastamentos_processados = []
        
        # Buscar registros de afastamento
        registros = self.gerenciador_bd.exportar_dados('esocial_s2230')
        
        if not registros:
            self.logger.warning("Nenhum registro de afastamento (S-2230) encontrado")
            return []
            
        self.logger.info(f"Encontrados {len(registros)} registros de afastamentos para processamento")
        
        # Mapeamento de códigos de afastamento para descrições
        mapeamento_motivos = {
            "01": "Acidente/Doença do trabalho",
            "03": "Acidente/Doença não relacionada ao trabalho",
            "05": "Afastamento por motivo de cessão",
            "06": "Aposentadoria por invalidez",
            "07": "Acompanhamento - Licença para acompanhamento de membro da família enfermo",
            "08": "Afastamento do empregado para participar de atividade sindical",
            "10": "Afastamento judicial",
            "11": "Licença maternidade",
            "12": "Licença paternidade",
            "13": "Licença remunerada (prevista em Legislação, CCT, ACT, etc.)",
            "14": "Licença não remunerada",
            "15": "Serviço militar obrigatório",
            "18": "Suspensão disciplinar",
            "19": "Licença sem vencimentos",
            "20": "Doação de sangue",
            "21": "Aborto não criminoso",
            "22": "Afastamento para exercer mandato eleitoral",
            "23": "Judicial - Outros",
            "24": "Representante sindical",
            "25": "Mandato sindical",
            "30": "Férias",
            "31": "Férias coletivas",
            "33": "Outro motivo de afastamento temporário",
            "34": "Alistamento militar",
            "35": "Inatividade do trabalhador avulso",
            "36": "Licença recebimento auxílio-doença"
        }
        
        # Para cada registro de afastamento
        for registro in registros:
            json_str = registro.get("json_data", "{}")
            
            try:
                # Extrair informações básicas do registro
                cnpj_empregador = registro.get("cnpj_empregador", "")
                cpf_trabalhador = registro.get("cpf_trabalhador", "")
                data_inicio = registro.get("data_inicio", "")
                data_fim = registro.get("data_fim", "")
                
                # Verificar se temos pelo menos os dados básicos
                if not cnpj_empregador or not cpf_trabalhador or not data_inicio:
                    continue
                
                # Analisar o JSON para extrair o motivo do afastamento
                import json
                dados_json = json.loads(json_str) if isinstance(json_str, str) else json_str
                
                # Buscar o motivo do afastamento em diferentes caminhos
                motivo_afastamento = None
                caminhos_motivo = [
                    ["evtAfastTemp", "infoAfastamento", "iniAfastamento", "infoAfastamento", "codMotAfast", "_text"],
                    ["infoAfastamento", "iniAfastamento", "infoAfastamento", "codMotAfast", "_text"],
                    ["iniAfastamento", "infoAfastamento", "codMotAfast", "_text"]
                ]
                
                for caminho in caminhos_motivo:
                    temp = dados_json
                    for parte in caminho:
                        if isinstance(temp, dict) and parte in temp:
                            temp = temp[parte]
                        else:
                            temp = None
                            break
                    if temp:
                        motivo_afastamento = temp
                        break
                
                # Ignorar férias, pois elas já são tratadas em _gerar_dados_ferias
                if motivo_afastamento == '30' or motivo_afastamento == '31':
                    continue
                
                # Criar registro de afastamento
                afastamento = {
                    "1 A-ID do empregador": cnpj_empregador,
                    "2 B-CPF trabalhador": cpf_trabalhador,
                    "3 C-Data de início": data_inicio,
                    "4 D-Data fim": data_fim or "",
                    "5 E-Tipo de afastamento": motivo_afastamento or "",
                    "6 F-Descrição motivo": mapeamento_motivos.get(str(motivo_afastamento), "Outro") if motivo_afastamento else "Outro"
                }
                
                # Adicionar o registro
                afastamentos_processados.append(afastamento)
                
            except Exception as e:
                self.logger.error(f"Erro ao processar registro de afastamento: {e}")
        
        # Completar campos com valores padrão
        for afastamento in afastamentos_processados:
            for coluna in colunas:
                if coluna not in afastamento:
                    afastamento[coluna] = ""
        
        self.logger.info(f"Total de {len(afastamentos_processados)} afastamentos processados")
        return afastamentos_processados

    def _gerar_dados_atestados(self, colunas: List[str]) -> List[Dict[str, Any]]:
        """Gera dados para o template de atestados médicos (S-2230 < 15 dias)"""
        # Buscar registros de afastamento com atestados
        registros = self.gerenciador_bd.exportar_dados('esocial_s2230')
        
        if not registros:
            self.logger.warning("Nenhum registro de afastamento (S-2230) encontrado para atestados")
            return []
            
        self.logger.info(f"Encontrados {len(registros)} registros de afastamentos para processamento de atestados")
        
        # Lista para armazenar os atestados processados
        atestados_processados = []
        
        # Para cada registro de afastamento
        for registro in registros:
            json_str = registro.get("json_data", "{}")
            
            try:
                # Extrair informações básicas do registro
                cnpj_empregador = registro.get("cnpj_empregador", "")
                cpf_trabalhador = registro.get("cpf_trabalhador", "")
                data_inicio = registro.get("data_inicio", "")
                data_fim = registro.get("data_fim", "")
                
                # Verificar se temos pelo menos os dados básicos
                if not cnpj_empregador or not cpf_trabalhador or not data_inicio:
                    continue
                
                # Calcular duração do afastamento
                qtd_dias = ""
                if data_inicio and data_fim:
                    try:
                        from datetime import datetime
                        d1 = datetime.strptime(data_inicio, "%Y-%m-%d")
                        d2 = datetime.strptime(data_fim, "%Y-%m-%d")
                        dias = (d2 - d1).days + 1
                        qtd_dias = str(dias)
                    except Exception as e:
                        self.logger.warning(f"Erro ao calcular duração do afastamento: {e}")
                
                # Atestados são afastamentos por doença com menos de 15 dias
                # Verificar se a duração é menor que 15 dias
                if qtd_dias and int(qtd_dias) < 15:
                    # Analisar o JSON para extrair informações do atestado
                    try:
                        import json
                        dados_json = json.loads(json_str) if isinstance(json_str, str) else json_str
                        
                        # Buscar informações do atestado em diferentes caminhos
                        info_atestado = None
                        caminhos_atestado = [
                            ["evtAfastTemp", "infoAfastamento", "iniAfastamento", "infoAtestado"],
                            ["infoAfastamento", "iniAfastamento", "infoAtestado"],
                            ["iniAfastamento", "infoAtestado"]
                        ]
                        
                        for caminho in caminhos_atestado:
                            temp = dados_json
                            for parte in caminho:
                                if isinstance(temp, dict) and parte in temp:
                                    temp = temp[parte]
                                else:
                                    temp = None
                                    break
                            if temp:
                                info_atestado = temp
                                break
                        
                        # Extrair informações do atestado
                        cid = ""
                        nome_medico = ""
                        
                        if info_atestado and isinstance(info_atestado, dict):
                            # CID
                            if "codCID" in info_atestado:
                                if isinstance(info_atestado["codCID"], dict) and "_text" in info_atestado["codCID"]:
                                    cid = info_atestado["codCID"]["_text"]
                                else:
                                    cid = str(info_atestado.get("codCID", ""))
                            
                            # Médico emitente
                            if "emitente" in info_atestado:
                                emitente = info_atestado["emitente"]
                                if isinstance(emitente, dict):
                                    if "nmEmit" in emitente:
                                        if isinstance(emitente["nmEmit"], dict) and "_text" in emitente["nmEmit"]:
                                            nome_medico = emitente["nmEmit"]["_text"]
                                        else:
                                            nome_medico = str(emitente.get("nmEmit", ""))
                        
                        # Criar registro de atestado
                        atestado = {
                            "1 A-ID do empregador": cnpj_empregador,
                            "2 B-CPF trabalhador": cpf_trabalhador,
                            "3 C-Data do atestado": data_inicio,
                            "4 D-Quantidade de dias": qtd_dias,
                            "5 E-CID": cid,
                            "6 F-Médico": nome_medico
                        }
                        
                        # Adicionar o registro
                        atestados_processados.append(atestado)
                        
                    except Exception as e:
                        self.logger.error(f"Erro ao processar JSON do atestado: {e}")
                
            except Exception as e:
                self.logger.error(f"Erro ao processar registro de atestado: {e}")
        
        # Completar campos com valores padrão
        for atestado in atestados_processados:
            for coluna in colunas:
                if coluna not in atestado:
                    atestado[coluna] = ""
        
        self.logger.info(f"Total de {len(atestados_processados)} atestados processados")
        return atestados_processados
        
    def _processar_atestado_direto(
        self, atestado_item, cnpj_empregador, cpf_trabalhador, 
        colunas, atestados_processados
    ):
        """Processa um item de atestado diretamente do JSON"""
        if isinstance(atestado_item, dict):
            dados_atestado = {}
            
            # Extrair emitente
            emitente = atestado_item.get("emitente", {})
            nome_medico = ""
            if isinstance(emitente, dict):
                nm_emit = emitente.get("nmEmit", {})
                if isinstance(nm_emit, dict):
                    nome_medico = nm_emit.get("_text", "")
                else:
                    nome_medico = nm_emit
            
            # Extrair código CID
            cod_cid = ""
            cid_obj = atestado_item.get("codCID", {})
            if isinstance(cid_obj, dict):
                cod_cid = cid_obj.get("_text", "")
            else:
                cod_cid = cid_obj
            
            # Extrair dias de afastamento
            qtd_dias = ""
            dias_obj = atestado_item.get("qtdDiasAfast", {})
            if isinstance(dias_obj, dict):
                qtd_dias = dias_obj.get("_text", "")
            else:
                qtd_dias = dias_obj
            
            # Extrair data de diagnóstico (equivalente à data do atestado)
            dt_diagnostico = ""
            dt_obj = atestado_item.get("dtDiagnostico", {})
            if isinstance(dt_obj, dict):
                dt_diagnostico = dt_obj.get("_text", "")
            else:
                dt_diagnostico = dt_obj
            
            # Mapear campos para o template
            for coluna in colunas:
                if coluna == "1 A-ID do empregador":
                    dados_atestado[coluna] = cnpj_empregador
                elif coluna == "2 B-CPF trabalhador":
                    dados_atestado[coluna] = cpf_trabalhador
                elif coluna == "3 C-Data do atestado":
                    dados_atestado[coluna] = dt_diagnostico
                elif coluna == "4 D-Quantidade de dias":
                    dados_atestado[coluna] = qtd_dias
                elif coluna == "5 E-CID":
                    dados_atestado[coluna] = cod_cid
                    # Log para diagnóstico
                    self.logger.info(f"CID extraído diretamente: {cod_cid}")
                elif coluna == "6 F-Médico":
                    dados_atestado[coluna] = nome_medico
                    # Log para diagnóstico
                    self.logger.info(f"Médico extraído diretamente: {nome_medico}")
                else:
                    dados_atestado[coluna] = ""
            
            atestados_processados.append(dados_atestado)
    
    def _mapear_campos_trabalhador(self, registro: Dict, json_data: Dict, resultado: Dict) -> Dict:
        """Mapeia campos específicos do trabalhador"""
        # Implementar mapeamento específico conforme estrutura do JSON
        # Por enquanto, mapear campos básicos
        registro['2 B-Código referência'] = resultado.get('cnpj_empregador', '')
        return registro
    
    def _mapear_campos_contrato(self, registro: Dict, json_data: Dict, resultado: Dict) -> Dict:
        """Mapeia campos específicos do contrato"""
        registro['1 A-ID do empregador'] = resultado.get('cnpj_empregador', '')
        return registro
    
    def _mapear_campos_contrato_alteracoes(self, registro: Dict, json_data: Dict, resultado: Dict) -> Dict:
        """Mapeia campos específicos das alterações de contrato"""
        return registro
    
    def _mapear_campos_ferias(self, registro: Dict, json_data: Dict, resultado: Dict) -> Dict:
        """Mapeia campos específicos das férias"""
        # Mapear explicitamente os campos da tabela esocial_s2230 para o template 05_FERIAS.csv
        resultado = {}
        
        # Campos básicos que vêm diretamente das colunas da tabela
        resultado["1 A-ID do empregador"] = registro.get("cnpj_empregador", "")
        resultado["2 B-CPF trabalhador"] = registro.get("cpf_trabalhador", "")
        resultado["3 C-Matrícula"] = registro.get("matricula", "")
        resultado["4 D-Data início"] = registro.get("data_inicio", "")
        resultado["5 E-Data fim"] = registro.get("data_fim", "")
        
        # Calcular duração da férias
        try:
            from datetime import datetime
            data_inicio = datetime.strptime(registro.get("data_inicio", ""), "%Y-%m-%d")
            data_fim = datetime.strptime(registro.get("data_fim", ""), "%Y-%m-%d")
            dias_ferias = (data_fim - data_inicio).days + 1
            resultado["10 J-Número de dias de férias"] = str(dias_ferias)
        except Exception:
            resultado["10 J-Número de dias de férias"] = ""
        
        # Valores padrão para os demais campos
        resultado["6 F-Data início do abono"] = ""
        resultado["7 G-Data fim do abono"] = ""
        resultado["8 H-Período aquisitivo início"] = ""
        resultado["9 I-Período aquisitivo fim"] = ""
        resultado["11 K-Indicativo de férias coletivas"] = ""
        
        # Processar o JSON, se disponível
        json_string = registro.get("json_data", "")
        if json_string and isinstance(json_string, str):
            try:
                import json
                json_obj = json.loads(json_string)
                
                # Extrair do JSON estruturado
                if "iniAfastamento" in json_obj:
                    if "dtIniAbono" in json_obj["iniAfastamento"]:
                        resultado["6 F-Data início do abono"] = json_obj["iniAfastamento"]["dtIniAbono"].get("_text", "")
                    
                    # Período aquisitivo
                    if "perAquisitivo" in json_obj["iniAfastamento"]:
                        periodo = json_obj["iniAfastamento"]["perAquisitivo"]
                        resultado["8 H-Período aquisitivo início"] = periodo.get("dtInicio", {}).get("_text", "")
                        resultado["9 I-Período aquisitivo fim"] = periodo.get("dtFim", {}).get("_text", "")
                    
                    # Dias de férias e indicativo de férias coletivas
                    resultado["10 J-Número de dias de férias"] = json_obj["iniAfastamento"].get("qtdDiasFerias", {}).get("_text", resultado["10 J-Número de dias de férias"])
                    resultado["11 K-Indicativo de férias coletivas"] = json_obj["iniAfastamento"].get("indFeriasColetivas", {}).get("_text", "")
                
                if "fimAfastamento" in json_obj:
                    if "dtFimAbono" in json_obj["fimAfastamento"]:
                        resultado["7 G-Data fim do abono"] = json_obj["fimAfastamento"]["dtFimAbono"].get("_text", "")
            except Exception as e:
                self.logger.error(f"Erro ao processar JSON de férias: {e}")
        
        self.logger.info(f"Mapeamento de férias concluído: {len(resultado)} campos mapeados")
        return resultado

    def _mapear_campos_ficha_financeira(self, registro: Dict, resultado: Dict) -> Dict:
        """Mapeia campos específicos da ficha financeira"""
        # Exemplo de mapeamento para os campos do layout 06_CONVFICHA.csv
        resultado = {}
        resultado["1 A-ID do empregador"] = registro.get("nrInscEstab", "")
        resultado["2 B-ID de pessoa"] = registro.get("ideDmDev", "")
        resultado["3 C-CPF trabalhador"] = registro.get("cpfTrab", "")
        resultado["4 D-Matrícula"] = registro.get("matricula", "")
        resultado["5 E-Competência"] = registro.get("perApur", "")
        resultado["6 F-ID da verba"] = registro.get("codRubr", "")
        resultado["7 G-Data"] = registro.get("dtIni", "")
        resultado["8 H-Tipo"] = registro.get("tpRubr", "")
        resultado["9 I-Valor"] = registro.get("vrRubr", "")
        return resultado

    def _mapear_campos_cargos(self, registro: Dict, resultado: Dict) -> Dict:
        """Mapeia campos específicos dos cargos"""
        resultado = {}
        resultado["1 A-ID do empregador"] = registro.get("nrInsc", "")
        resultado["2 B-ID do cargo"] = registro.get("codCargo", "")
        resultado["3 C-Nome do cargo"] = registro.get("nmCargo", "")
        resultado["4 D-Data de início"] = registro.get("iniValid", "")
        resultado["5 E-Data fim de validade"] = registro.get("fimValid", "")
        resultado["6 F-CBO"] = registro.get("codCBO", "")
        resultado["7 G-Observações"] = registro.get("observacoes", "")
        return resultado

    def _mapear_campos_afastamentos(self, registro: Dict, json_data: Dict, resultado: Dict) -> Dict:
        """Mapeia campos específicos dos afastamentos"""
        resultado = {}
        resultado["1 A-ID do empregador"] = json_data.get("evtAfastTemp", {}).get("ideEmpregador", {}).get("nrInsc", "")
        resultado["2 B-CPF trabalhador"] = json_data.get("evtAfastTemp", {}).get("ideTrabalhador", {}).get("cpfTrab", "")
        resultado["3 C-Data de início"] = registro.get("dtIniAfast", "")
        resultado["4 D-Data fim"] = registro.get("dtFimAfast", "")
        resultado["5 E-Tipo de afastamento"] = registro.get("codMotAfast", "")
        return resultado

    def _mapear_campos_atestados(self, registro: Dict, json_data: Dict, resultado: Dict) -> Dict:
        """Mapeia campos específicos dos atestados médicos"""
        resultado = {}
        resultado["1 A-ID do empregador"] = json_data.get("evtAfastTemp", {}).get("ideEmpregador", {}).get("nrInsc", "")
        resultado["2 B-CPF trabalhador"] = json_data.get("evtAfastTemp", {}).get("ideTrabalhador", {}).get("cpfTrab", "")
        resultado["3 C-Data do atestado"] = registro.get("dtDiagnostico", "")
        resultado["4 D-Quantidade de dias"] = registro.get("qtdDiasAfast", "")
        resultado["5 E-CID"] = registro.get("codCID", "")
        resultado["6 F-Médico"] = registro.get("emitente", {}).get("nmEmit", "")
        return resultado
    
    def _salvar_template_csv(self, nome_template: str, colunas: List[str], dados: List[Dict[str, Any]]) -> None:
        """
        Salva dados em um arquivo CSV usando o formato do template sem adicionar timestamp
        
        Args:
            nome_template: Nome do arquivo template
            colunas: Lista de colunas do template
            dados: Dados a serem salvos
        """
        import os
        import re
        
        # Verificar se há dados para salvar
        if not dados:
            self.logger.warning(f" Nenhum dado para salvar no template {nome_template}. Criando arquivo vazio.")
            self._criar_arquivo_vazio(nome_template, colunas)
            return
        
        # Validar dados extraídos e gerar diagnósticos detalhados
        self._validar_dados_extraidos(nome_template, dados, colunas)
        
        self.logger.info(f"[DEBUG] Criando caminho para arquivo {nome_template}")
        self.logger.info(f"[DEBUG] self.pasta_csv = {self.pasta_csv}")
        self.logger.info(f"[DEBUG] type(self.pasta_csv) = {type(self.pasta_csv)}")
        
        if self.pasta_csv is None:
            raise ValueError(f"pasta_csv é None ao tentar criar {nome_template}")
        
        caminho_arquivo = self.pasta_csv / nome_template
        self.logger.info(f"[DEBUG] caminho_arquivo = {caminho_arquivo}")
        self.logger.info(f"[DEBUG] type(caminho_arquivo) = {type(caminho_arquivo)}")
        
        try:
            self.pasta_csv.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Salvando {len(dados)} registros no arquivo {nome_template}")
            
            # DEBUG: Log the first few data rows before writing
            self.logger.info(f"[DEBUG] {nome_template}: Primeiros 3 registros antes da escrita:")
            for i, registro in enumerate(dados[:3]):
                self.logger.info(f"[DEBUG] {nome_template} registro {i+1}: {registro}")
            
            with caminho_arquivo.open('w', newline='', encoding='utf-8-sig') as arquivo:
                if colunas:
                    # Importar o formatador de dados brasileiro
                    # from src.utils.formatador_dados_br import formatar_data_br, formatar_numero_br
                    
                    escritor = csv.DictWriter(arquivo, fieldnames=colunas, delimiter=';')
                    escritor.writeheader()
                    contador = 0
                    self.logger.info(f"[DEBUG] {nome_template}: Iniciando escrita de {len(dados)} registros")
                    
                    for registro in dados:
                        registro_completo = {}
                        for coluna in colunas:
                            valor = registro.get(coluna, '')
                            
                            # Detectar e formatar datas
                            if isinstance(valor, str) and re.match(r'^\d{4}-\d{2}-\d{2}', valor):
                                valor = formatar_data_br(valor)
                            # Detectar e formatar números fracionários
                            elif isinstance(valor, (float, int)) or (isinstance(valor, str) and 
                                    re.match(r'^-?\d+\.\d+$', valor)):
                                valor = formatar_numero_br(valor)
                                
                            registro_completo[coluna] = valor
                        
                        # DEBUG: Log each row being written
                        self.logger.info(f"[DEBUG] {nome_template}: Escrevendo linha {contador+1}: {list(registro_completo.values())[:3]}...")
                        escritor.writerow(registro_completo)
                        contador += 1
                        
                        # Force flush after each row
                        arquivo.flush()
                    
                    # Force flush to ensure data is written
                    arquivo.flush()
                    os.fsync(arquivo.fileno())
                    
                    self.logger.info(f" {contador} registros salvos com sucesso em {nome_template}")
                    if caminho_arquivo.exists():
                        tamanho = caminho_arquivo.stat().st_size
                        self.logger.info(f"Arquivo criado em {self.caminho_saida} com {tamanho} bytes")
                        if tamanho < 100 and contador > 0:
                            self.logger.warning(f" Arquivo parece pequeno demais para {contador} registros")
        except Exception as e:
            self.logger.error(f" Erro ao salvar template {nome_template}: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
    
    def _criar_arquivo_vazio(self, nome_template: str, colunas: List[str]) -> None:
        """
        Cria um arquivo CSV vazio com as colunas especificadas
        
        Args:
            nome_template: Nome do arquivo template
            colunas: Lista de colunas do template
        """
        caminho_arquivo = self.pasta_csv / nome_template
        
        try:
            with caminho_arquivo.open('w', newline='', encoding='utf-8-sig') as arquivo:
                if colunas:
                    escritor = csv.writer(arquivo, delimiter=';')
                    escritor.writerow(colunas)
                    
            self.logger.info(f"Arquivo vazio criado: {nome_template} no diretório {self.caminho_saida}")
            
        except Exception as e:
            self.logger.error(f"Erro ao criar arquivo vazio {nome_template}: {e}")
    
    def _verificar_templates_disponiveis(self) -> None:
        """
        Verifica quais templates CSV físicos estão disponíveis na pasta de templates
        Não é mais necessário ter os arquivos, mas verifica por compatibilidade
        """
        try:
            # Verificar se existem arquivos CSV na pasta de templates
            arquivos_csv = list(self.caminho_templates.glob('*.csv'))
            
            if arquivos_csv:
                self.logger.info(f"Encontrados {len(arquivos_csv)} templates CSV físicos")
                
                # Verificar quais dos templates obrigatórios existem fisicamente
                templates_encontrados = [f.name for f in arquivos_csv if f.name in self.templates_obrigatorios]
                templates_faltantes = [t for t in self.templates_obrigatorios if t not in [f.name for f in arquivos_csv]]
                
                if templates_encontrados:
                    self.logger.info(f"Templates obrigatórios encontrados fisicamente: {', '.join(templates_encontrados)}")
                
                if templates_faltantes:
                    self.logger.info(f"Templates obrigatórios não encontrados fisicamente (serão usadas as definições de configuração): {', '.join(templates_faltantes)}")
            else:
                self.logger.info("Nenhum template CSV físico encontrado na pasta de templates. Serão usadas as definições de configuração.")
                
        except Exception as e:
            self.logger.error(f"Erro ao verificar templates CSV: {e}")
            self.logger.info("Continuando com as definições de configuração para os templates.")
    
    def _finalizar_exportacao(self) -> None:
        """
        Finaliza a exportação organizando arquivos
        """
        try:
            # Arquivo CSV já gerado, apenas finaliza a exportação
            self.logger.info("Exportação de arquivos CSV finalizada")
            
        except Exception as e:
            self.logger.error(f" Erro ao finalizar exportação: {e}")
    
    def _buscar_dados_fonte(self, fonte: str) -> List[Dict[str, Any]]:
        """
        Busca dados de uma fonte específica
        
        Args:
            fonte: Nome da tabela fonte
            
        Returns:
            Lista de registros da fonte
        """
        try:
            if fonte.strip().upper().startswith("SELECT"):
                # É uma consulta SQL completa
                self.logger.info(f"Executando consulta SQL personalizada")
                return self.gerenciador_bd.executar_query(fonte)
            else:
                # É um nome de tabela
                self.logger.info(f"Buscando dados da tabela: {fonte}")
                query = f"SELECT * FROM {fonte}"
                resultados = self.gerenciador_bd.executar_query(query)
                
                # Verificar se retornou algum dado
                if not resultados:
                    self.logger.warning(f" Nenhum dado encontrado na tabela: {fonte}")
                else:
                    self.logger.info(f" Encontrados {len(resultados)} registros na tabela: {fonte}")
                    # Verificar primeira linha para diagnóstico
                    if len(resultados) > 0:
                        primeira_linha = resultados[0]
                        self.logger.debug(f"Exemplo de registro: {json.dumps(dict(primeira_linha), default=str)[:200]}...")
                        
                return resultados
        except Exception as e:
            self.logger.error(f" Erro ao buscar dados da fonte {fonte}: {e}")
            # Mostrar stacktrace para diagnóstico
            import traceback
            self.logger.error(traceback.format_exc())
            return []
    
    def _formatar_valor(self, valor: Any) -> str:
        """
        Formata um valor para string conforme necessário
        
        Args:
            valor: Valor a ser formatado
        Returns:
            Valor formatado como string
        """
        from datetime import datetime
        if valor is None:
            return ''
        # Formatação de datas: YYYY-MM-DD ou YYYY-MM-DDTHH:MM:SS -> DD/MM/YYYY
        if isinstance(valor, str):
            v = valor.strip()
            # Data completa
            if v and (v.count('-') == 2 or 'T' in v):
                try:

                    if 'T' in v:
                        v = v.split('T')[0]
                    dt = datetime.strptime(v, '%Y-%m-%d')
                    return dt.strftime('%d/%m/%Y')
                except Exception:
                    pass
            # Número já formatado com vírgula
            if v.replace('.', '', 1).replace(',', '', 1).isdigit():
                try:
                    f = float(v.replace(',', '.'))
                    # Se for inteiro, retorna sem casas decimais
                    if f.is_integer():
                        return str(int(f))
                    return f'{f:.2f}'.replace('.', ',')
                except Exception:
                    pass
            return v
        elif isinstance(valor, int):
            return str(valor)
        elif isinstance(valor, float):
            if valor.is_integer():
                return str(int(valor))
            return f'{valor:.2f}'.replace('.', ',')
        return str(valor)
    
    def _gerar_dados_template_legado(self, nome_template: str, colunas: List[str]) -> List[Dict[str, Any]]:
        """
        Método legado para templates sem mapeamento definido
        
        Args:
            nome_template: Nome do template
            colunas: Lista de colunas do template
            
        Returns:
            Lista de dicionários com os dados
        """
        self.logger.info(f"Usando método legado para template: {nome_template}")
        
        # Templates específicos com implementações próprias
        if nome_template == '04_CONVDEPENDENTE.csv':
            return self._gerar_dados_dependente(colunas)
        elif nome_template == '05_FERIAS.csv':
            return self._gerar_dados_ferias(colunas)
        elif nome_template == '06_CONVFICHA.csv':
            return self._gerar_dados_ficha_financeira(colunas)
        elif nome_template == '07_CARGOS.csv':
            return self._gerar_dados_cargos(colunas)
        elif nome_template == '08_CONVAFASTAMENTO.csv':
            return self._gerar_dados_afastamentos(colunas)
        elif nome_template == '09_CONVATESTADO.csv':
            return self._gerar_dados_atestados(colunas)
        # Templates sem implementação específica
        else:
            self.logger.warning(f"Template {nome_template} sem implementação específica no modo legado")
            return []
    
    def verificar_mapeamentos_completos(self) -> bool:
        """
        Verifica se todos os mapeamentos necessários estão definidos para os templates.
        Usa colunas dos arquivos ou das configurações.
        
        Returns:
            bool: True se todos os mapeamentos estão completos, False caso contrário
        """
        self.logger.info("Verificando completude dos mapeamentos para os templates...")
        mapeamentos_completos = True
        
        # Para cada template obrigatório
        for nome_template in self.templates_obrigatorios:
            # Verificar se temos o mapeamento para este template
            nome_base = nome_template.replace('.csv', '')
            if nome_base not in self.mapeador.mapeamentos:
                self.logger.warning(f"Template {nome_template}: Não possui mapeamento definido!")
                mapeamentos_completos = False
                continue
                
            # Obter colunas do template (do arquivo ou configuração)
            colunas_template = self._ler_colunas_template(nome_template)
            if not colunas_template:
                self.logger.warning(f"Template {nome_template}: Não foi possível ler as colunas (nem do arquivo nem das configurações)")
                mapeamentos_completos = False
                continue
                
            # Verificar se cada coluna do template tem mapeamento
            colunas_sem_mapeamento = []
            for coluna in colunas_template:
                if coluna not in self.mapeador.mapeamentos[nome_base]['campos']:
                    colunas_sem_mapeamento.append(coluna)
                    
            if colunas_sem_mapeamento:
                self.logger.warning(f"Template {nome_template}: {len(colunas_sem_mapeamento)} colunas não possuem mapeamento")
                for coluna in colunas_sem_mapeamento[:5]:  # Mostrar até 5 exemplos
                    self.logger.warning(f"- Coluna '{coluna}' não possui mapeamento")
                if len(colunas_sem_mapeamento) > 5:
                    self.logger.warning(f"- E mais {len(colunas_sem_mapeamento) - 5} colunas...")
                mapeamentos_completos = False
        
        if mapeamentos_completos:
            self.logger.info(" Todos os mapeamentos estão completos!")
        else:
            self.logger.warning(" Existem mapeamentos incompletos nos templates!")
        
        return mapeamentos_completos
    
    def verificar_completude_dados(self) -> Dict[str, Dict[str, Any]]:
        """
        Verifica a completude dos dados nos CSVs gerados.
        Analisa cada arquivo e reporta estatísticas sobre campos preenchidos e ausentes.
        
        Returns:
            Dict com estatísticas por template
        """
        self.logger.info("Verificando completude dos dados nos CSVs gerados...")
        resultado = {}
        
        for nome_template in self.templates_obrigatorios:
            caminho_csv = self.caminho_saida / nome_template
            
            if not caminho_csv.exists():
                self.logger.warning(f"Arquivo {nome_template} não foi gerado")
                resultado[nome_template] = {
                    "existe": False,
                    "registros": 0,
                    "campos_completos": 0,
                    "campos_vazios": 0,
                    "porcentagem_preenchimento": 0,
                    "campos_mais_ausentes": []
                }
                continue
                
            try:
                # Verificar se o arquivo tem conteúdo
                tamanho = caminho_csv.stat().st_size
                if tamanho < 10:
                    self.logger.warning(f" Arquivo {nome_template} está praticamente vazio ({tamanho} bytes)")
                    resultado[nome_template] = {
                        "existe": True,
                        "registros": 0,
                        "campos_completos": 0,
                        "campos_vazios": 0,
                        "porcentagem_preenchimento": 0,
                        "campos_mais_ausentes": []
                    }
                    continue
                
                # Ler o arquivo CSV
                self.logger.info(f"Analisando arquivo {nome_template}...")
                df = pd.read_csv(caminho_csv, sep=';', encoding='utf-8-sig', na_values=['', 'null', 'NULL', 'None'])
                
                # Estatísticas gerais
                registros = len(df)
                
                if registros == 0:
                    self.logger.warning(f" Arquivo {nome_template} não contém registros (apenas cabeçalho)")
                    resultado[nome_template] = {
                        "existe": True,
                        "registros": 0,
                        "campos_completos": 0,
                        "campos_vazios": 0,
                        "porcentagem_preenchimento": 0,
                        "campos_mais_ausentes": []
                    }
                    continue
                
                # Tratar valores vazios e espaços como NaN para contar corretamente
                df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
                df = df.replace(r'^\s*$', pd.NA, regex=True)
                
                # Contar campos vazios e preenchidos
                campos_vazios = (df.isna() | (df == '')).sum().to_dict()
                
                # Calcular estatísticas
                total_campos = registros * len(df.columns)
                total_vazios = sum(campos_vazios.values())
                total_preenchidos = total_campos - total_vazios
                porcentagem = (total_preenchidos / total_campos) * 100 if total_campos > 0 else 0
                
                # Identificar campos mais ausentes
                campos_mais_ausentes = [(campo, contagem) for campo, contagem in campos_vazios.items() if contagem > 0]
                campos_mais_ausentes.sort(key=lambda x: x[1], reverse=True)
                campos_mais_ausentes = campos_mais_ausentes[:10]  # Top 10
                
                # Verificar registros completamente vazios
                linhas_vazias = df.isna().all(axis=1).sum()
                if linhas_vazias > 0:
                    self.logger.warning(f" {nome_template}: {linhas_vazias} registros estão completamente vazios")
                
                # Verificar campos que nunca foram preenchidos
                campos_nunca_preenchidos = [campo for campo, count in campos_vazios.items() if count == registros]
                if campos_nunca_preenchidos:
                    self.logger.warning(f" {nome_template}: {len(campos_nunca_preenchidos)} campos nunca foram preenchidos")
                    for campo in campos_nunca_preenchidos[:5]:
                        self.logger.warning(f"  - Campo '{campo}' sempre ausente")
                    if len(campos_nunca_preenchidos) > 5:
                        self.logger.warning(f"  - E mais {len(campos_nunca_preenchidos) - 5} campos...")
                
                # Registrar resultados
                resultado[nome_template] = {
                    "existe": True,
                    "registros": registros,
                    "registros_vazios": int(linhas_vazias),
                    "campos_completos": int(total_preenchidos),
                    "campos_vazios": int(total_vazios),
                    "porcentagem_preenchimento": float(porcentagem),
                    "campos_mais_ausentes": campos_mais_ausentes,
                    "campos_nunca_preenchidos": campos_nunca_preenchidos
                }
                
                # Logar resultados
                self.logger.info(f"Template {nome_template}: {registros} registros, {porcentagem:.2f}% de preenchimento")
                for campo, count in campos_mais_ausentes[:3]:
                    if registros > 0:
                        self.logger.info(f"  - Campo '{campo}' ausente em {count} registros ({(count/registros)*100:.1f}%)")
            except Exception as e:
                self.logger.error(f"Erro ao analisar arquivo {nome_template}: {e}")
                self.logger.error(traceback.format_exc())
                resultado[nome_template] = {
                    "existe": True,
                    "erro": str(e)
                }
                
        return resultado
    
    def _processar_json_ferias(self, registro: Dict) -> Dict:
        """
        Processa o JSON de férias para extrair dados mais facilmente.
        Extrai dados de férias de acordo com o layout S-2230 do eSocial.
        
        Args:
            registro: Registro da tabela esocial_s2230
            
        Returns:
            Dicionário com o JSON processado, simplificando acesso aos campos
        """
        try:
            if "json_data" not in registro or not registro["json_data"]:
                self.logger.debug("JSON de férias não encontrado no registro")
                return {}
                
            if isinstance(registro["json_data"], str):
                try:
                    json_data = json.loads(registro["json_data"])
                except json.JSONDecodeError as e:
                    self.logger.error(f"Erro ao decodificar JSON de férias: {e}")
                    return {}
            else:
                json_data = registro["json_data"]
                
            # Extrair informações mais relevantes para simplificar o acesso
            processado: Dict[str, Any] = {}
            
            # Função auxiliar para extrair texto do campo, considerando estrutura _text ou valor direto
            def extrair_texto(obj: Any, campo: str) -> Any:
                if not obj or not isinstance(obj, dict) or campo not in obj:
                    return None
                valor = obj.get(campo)
                if isinstance(valor, dict) and "_text" in valor:
                    return valor.get("_text")
                return valor
            
            # Processar a estrutura do JSON para extrair dados de férias
            if "evtAfastTemp" in json_data:
                # Estrutura completa do eSocial 2.5
                evt = json_data["evtAfastTemp"]
                
                # Dados do empregador e trabalhador
                if "ideEmpregador" in evt and isinstance(evt["ideEmpregador"], dict):
                    ide_empregador = evt["ideEmpregador"]
                    if "nrInsc" in ide_empregador:
                        processado["nrInsc"] = extrair_texto(ide_empregador, "nrInsc")
                    if "tpInsc" in ide_empregador:
                        processado["tpInsc"] = extrair_texto(ide_empregador, "tpInsc")
                
                if "ideTrabalhador" in evt and isinstance(evt["ideTrabalhador"], dict):
                    ide_trabalhador = evt["ideTrabalhador"]
                    if "cpfTrab" in ide_trabalhador:
                        processado["cpfTrab"] = extrair_texto(ide_trabalhador, "cpfTrab")
                
                # Informações de afastamento (férias)
                if "infoAfastamento" in evt and isinstance(evt["infoAfastamento"], dict):
                    info_afast = evt["infoAfastamento"]
                    
                    # Dados do início de afastamento
                    if "iniAfastamento" in info_afast and isinstance(info_afast["iniAfastamento"], dict):
                        ini = info_afast["iniAfastamento"]
                        if "dtIniAfast" in ini:
                            processado["dtIniAfast"] = extrair_texto(ini, "dtIniAfast")
                        if "codMotAfast" in ini:
                            processado["codMotAfast"] = extrair_texto(ini, "codMotAfast")
                        if "dtIniAbono" in ini:
                            processado["dtIniAbono"] = extrair_texto(ini, "dtIniAbono")
                        if "qtdDiasFerias" in ini:
                            processado["qtdDiasFerias"] = extrair_texto(ini, "qtdDiasFerias")
                        if "indFeriasColetivas" in ini:
                            processado["indFeriasColetivas"] = extrair_texto(ini, "indFeriasColetivas")
                        
                        # Período aquisitivo
                        if "perAquisitivo" in ini and isinstance(ini["perAquisitivo"], dict):
                            per = ini["perAquisitivo"]
                            if "dtInicio" in per:
                                processado["perAquisitivoInicio"] = extrair_texto(per, "dtInicio")
                            if "dtFim" in per:
                                processado["perAquisitivoFim"] = extrair_texto(per, "dtFim")
                    
                    # Dados do fim de afastamento
                    if "fimAfastamento" in info_afast and isinstance(info_afast["fimAfastamento"], dict):
                        fim = info_afast["fimAfastamento"]
                        if "dtTermAfast" in fim:
                            processado["dtFimAfast"] = extrair_texto(fim, "dtTermAfast")
                        if "dtFimAbono" in fim:
                            processado["dtFimAbono"] = extrair_texto(fim, "dtFimAbono")
            
            # Compatibilidade com outros formatos de JSON
            elif "iniAfastamento" in json_data:
                # JSON já está parcialmente processado
                if isinstance(json_data["iniAfastamento"], dict):
                    ini = json_data["iniAfastamento"]
                    if "dtIniAfast" in ini:
                        processado["dtIniAfast"] = extrair_texto(ini, "dtIniAfast")
                    if "codMotAfast" in ini:
                        processado["codMotAfast"] = extrair_texto(ini, "codMotAfast")
                    if "dtIniAbono" in ini:
                        processado["dtIniAbono"] = extrair_texto(ini, "dtIniAbono")
                    if "qtdDiasFerias" in ini:
                        processado["qtdDiasFerias"] = extrair_texto(ini, "qtdDiasFerias")
                   
                    if "indFeriasColetivas" in ini:
                        processado["indFeriasColetivas"] = extrair_texto(ini, "indFeriasColetivas")
                    
                    if "perAquisitivo" in ini and isinstance(ini["perAquisitivo"], dict):
                        per = ini["perAquisitivo"]
                        if "dtInicio" in per:
                            processado["perAquisitivoInicio"] = extrair_texto(per, "dtInicio")
                        if "dtFim" in per:
                            processado["perAquisitivoFim"] = extrair_texto(per, "dtFim")
                
                if "fimAfastamento" in json_data and isinstance(json_data["fimAfastamento"], dict):
                    fim = json_data["fimAfastamento"]
                    if "dtTermAfast" in fim:
                        processado["dtFimAfast"] = extrair_texto(fim, "dtTermAfast")
                    if "dtFimAbono" in fim:
                        processado["dtFimAbono"] = extrair_texto(fim, "dtFimAbono")
            
            # Remover valores None para economizar espaço
            processado = {k: v for k, v in processado.items() if v is not None}
            
            self.logger.debug(f"JSON de férias processado: {len(processado)} campos extraídos")
            return processado
            
        except Exception as e:
            self.logger.error(f"Erro ao processar JSON de férias: {e}")
            self.logger.error(traceback.format_exc())
            return {}
    
    def _processar_json_dependente(self, registro: Dict) -> Dict:
        """
        Processa o JSON de dependentes para extrair dados mais facilmente.
        
        Args:
            registro: Registro da tabela esocial_dependentes ou esocial_s2200
            
        Returns:
            Dicionário com o JSON processado para fácil acesso aos campos de dependentes
        """
        try:
            if "json_data" not in registro or not registro["json_data"]:
                self.logger.debug("JSON de dependente não encontrado no registro")
                return {}
                
            if isinstance(registro["json_data"], str):
                try:
                    json_data = json.loads(registro["json_data"])
                except json.JSONDecodeError as e:
                    self.logger.error(f"Erro ao decodificar JSON de dependente: {e}")
                    return {}
            else:
                json_data = registro["json_data"]
                
            # Extrair informações relevantes para facilitar o acesso
            processado: Dict[str, Any] = {}
            
            # Função auxiliar para extrair texto de campos aninhados
            def extrair_texto(obj: Any, campo: str) -> Any:
                if not obj or not isinstance(obj, dict) or campo not in obj:
                    return None
                valor = obj.get(campo)
                if isinstance(valor, dict) and "_text" in valor:
                    return valor.get("_text")
                return valor
                
            # Extrair dados do dependente baseado na estrutura do XML/JSON do eSocial
            if "evtCadInicial" in json_data or "evtAltCadastral" in json_data or "evtAdmissao" in json_data:
                # Identificar o evento correto
                evento = None
                if "evtCadInicial" in json_data:
                    evento = json_data["evtCadInicial"]
                elif "evtAltCadastral" in json_data:
                    evento = json_data["evtAltCadastral"]
                elif "evtAdmissao" in json_data:
                    evento = json_data["evtAdmissao"]
                
                if evento and "trabalhador" in evento:
                    trabalhador = evento["trabalhador"]
                    
                    # Dados básicos do trabalhador para referência
                    if "cpfTrab" in trabalhador:
                        processado["cpfTrab"] = extrair_texto(trabalhador, "cpfTrab")
                    
                    if "dependente" in trabalhador:
                        dependentes = trabalhador["dependente"]
                        
                        # Pode ser um único dependente ou lista de dependentes
                        if isinstance(dependentes, dict):
                            dep = dependentes
                            # Mapear campos básicos
                            processado["tpDep"] = extrair_texto(dep, "tpDep")
                            processado["nmDep"] = extrair_texto(dep, "nmDep")
                            processado["dtNascto"] = extrair_texto(dep, "dtNascto")
                            processado["cpfDep"] = extrair_texto(dep, "cpfDep")
                            processado["depIRRF"] = extrair_texto(dep, "depIRRF")
                            processado["depSF"] = extrair_texto(dep, "depSF")
                            processado["incTrab"] = extrair_texto(dep, "incTrab")
                        elif isinstance(dependentes, list):
                            # Se for lista, retorna o primeiro para manter compatibilidade
                            # Os outros serão tratados pela função extrair_dependentes no mapeador
                            if dependentes:
                                dep = dependentes[0]
                                processado["tpDep"] = extrair_texto(dep, "tpDep")
                                processado["nmDep"] = extrair_texto(dep, "nmDep")
                                processado["dtNascto"] = extrair_texto(dep, "dtNascto")
                                processado["cpfDep"] = extrair_texto(dep, "cpfDep")
                                processado["depIRRF"] = extrair_texto(dep, "depIRRF")
                                processado["depSF"] = extrair_texto(dep, "depSF")
                                processado["incTrab"] = extrair_texto(dep, "incTrab")
            
            # Remover valores None para economizar espaço
            processado = {k: v for k, v in processado.items() if v is not None}
            
            self.logger.debug(f"JSON de dependente processado: {len(processado)} campos extraídos")
            return processado
            
        except Exception as e:
            self.logger.error(f"Erro ao processar JSON de dependente: {e}")
            self.logger.error(traceback.format_exc())
            return {}
    
    def _adicionar_metodo_dinamico(self, nome_metodo: str, metodo_func: Callable) -> bool:
        """
        Adiciona um método dinamicamente ao mapeador.
        
        Args:
            nome_metodo: Nome do método a ser adicionado
            metodo_func: Função a ser vinculada como método
            
        Returns:
            True se o método foi adicionado com sucesso
        """
        try:
            # Adicionar o método diretamente à instância, sem usar MethodType
            setattr(self.mapeador, nome_metodo, types.MethodType(metodo_func, self.mapeador))
            
            self.logger.info(f"Método '{nome_metodo}' adicionado dinamicamente ao mapeador")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao adicionar método '{nome_metodo}' dinamicamente: {e}")
            return False
    
    def _validar_dados_extraidos(self, template_nome: str, dados: List[Dict], colunas: List[str]) -> None:
        """
        Valida os dados extraídos para um template específico e gera logs detalhados.
        
        Args:
            template_nome: Nome do template
            dados: Lista de dados extraídos
            colunas: Colunas do template
        """
        registros_totais = len(dados)
        self.logger.info(f"Validando dados para {template_nome}: {registros_totais} registros extraídos")
        
        # Se não tem registros, não precisa validar mais nada
        if not registros_totais:
            self.logger.warning(f" Nenhum registro extraído para {template_nome}!")
            return
            
        # Verifica registros com todos os campos vazios
        registros_vazios = 0
        for registro in dados:
            valores = [v for k, v in registro.items() if v not in (None, "")]
            if not valores:
                registros_vazios += 1
        
        if registros_vazios > 0:
            self.logger.warning(f" {registros_vazios} registros estão completamente vazios em {template_nome}")
            if registros_vazios == registros_totais:
                self.logger.error(f" ERRO CRÍTICO: Todos os registros de {template_nome} estão vazios!")
        
        # Validar colunas obrigatórias
        colunas_obrigatorias = []
        chave_template = template_nome.replace('.csv', '')
        mapeamento = self.mapeador.obter_mapeamento_template(chave_template)
        
        if mapeamento and 'campos' in mapeamento:
            for campo, definicao in mapeamento['campos'].items():
                if definicao.get('obrigatorio'):
                    colunas_obrigatorias.append(campo)
        
        if colunas_obrigatorias:
            self.logger.info(f"Verificando {len(colunas_obrigatorias)} campos obrigatórios para {template_nome}")
            
            # Contar quantos registros têm cada campo obrigatório preenchido
            contagem_preenchidos = {}
            for col in colunas_obrigatorias:
                contagem_preenchidos[col] = 0
            
            for registro in dados:
                for col in colunas_obrigatorias:
                    valor = registro.get(col, '')
                    if valor not in (None, ''):
                        contagem_preenchidos[col] += 1
            
            # Mostrar estatística de preenchimento de cada coluna obrigatória
            for col, contagem in contagem_preenchidos.items():
                porcentagem = (contagem / registros_totais) * 100 if registros_totais > 0 else 0
                if porcentagem < 100:
                    self.logger.warning(f" Campo {col}: Preenchido em {contagem}/{registros_totais} registros ({porcentagem:.1f}%)")
                else:
                    self.logger.info(f"Campo {col}: Preenchido em {contagem}/{registros_totais} registros (100%)")
        
        # Mostrar amostra dos dados
        if registros_totais > 0:
            amostra_size = min(3, registros_totais)
            self.logger.info(f"Amostra de {amostra_size} registros para {template_nome}:")
            
            for i in range(amostra_size):
                registro = dados[i]
                log_amostra = {}
                
                # Limitar o número de campos no log para não ficar muito grande
                campos_importantes = colunas_obrigatorias[:5] if colunas_obrigatorias else colunas[:5]
                for campo in campos_importantes:
                    if campo in registro:
                        log_amostra[campo] = registro[campo]
                
                self.logger.info(f"Registro {i+1}: {log_amostra}")
    
    def _diagnosticar_dados(self, tabela: str) -> None:
        """
        Realiza diagnóstico detalhado dos dados de uma tabela específica
        
        Args:
            tabela: Nome da tabela a ser diagnosticada
        """
        self.logger.info(f"Iniciando diagnóstico detalhado da tabela: {tabela}")
        
        # Verificar se a tabela existe
        tabela_existe_query = f"""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='{tabela}'
        """
        tabela_existe = self.gerenciador_bd.executar_query(tabela_existe_query)
        
        if not tabela_existe:
            self.logger.error(f" Tabela não encontrada: {tabela}")
            return
        
        # Contar registros
        count_query = f"SELECT COUNT(*) as total FROM {tabela}"
        count_result = self.gerenciador_bd.executar_query(count_query)
        total_registros = count_result[0]['total'] if count_result else 0
        
        self.logger.info(f"Tabela {tabela}: {total_registros} registros encontrados")
        
        if total_registros == 0:
            self.logger.warning(f" Tabela {tabela} está vazia!")
            return
        
        # Verificar estrutura (schema)
        pragma_query = f"PRAGMA table_info({tabela})"
        colunas_info = self.gerenciador_bd.executar_query(pragma_query)
        
        self.logger.info(f"Estrutura da tabela {tabela}: {len(colunas_info)} colunas")
        for col in colunas_info:
            self.logger.info(f"  - {col['name']} ({col['type']})")
        
        # Buscar amostra de dados para diagnóstico
        sample_query = f"SELECT * FROM {tabela} LIMIT 1"
        amostra = self.gerenciador_bd.executar_query(sample_query)
        
        if amostra:
            self.logger.info(f"Amostra de dados da tabela {tabela}:")
            for chave, valor in amostra[0].items():
                if chave == 'json_data':
                    try:
                        dados_json = json.loads(valor) if valor else {}
                        # Mostrar estrutura principal do JSON
                        self.logger.info(f"  - json_data: Estrutura principal: {list(dados_json.keys())}")
                        
                        # Se for um evento do eSocial, verificar tipo
                        for key in dados_json.keys():
                            if key.startswith('evt'):
                                self.logger.info(f"  - Tipo de evento eSocial: {key}")
                    except Exception as e:
                        self.logger.error(f"  - json_data: Erro ao parsear JSON: {e}")
                        if valor:
                            self.logger.info(f"  - json_data (primeiros 200 caracteres): {valor[:200]}...")
                else:
                    self.logger.info(f"  - {chave}: {valor}")
            
            # Se for uma tabela relacionada aos templates problemáticos, analisar mais a fundo
            if tabela in ['esocial_s2230', 'esocial_s1030']:
                try:
                    registro = amostra[0]
                    json_str = registro.get('json_data', '{}')
                    dados_json = json.loads(json_str) if isinstance(json_str, str) and json_str else {}
                    
                    # Diagnóstico específico para cada tipo de tabela
                    if tabela == 'esocial_s2230':  # Afastamentos e atestados
                        self.logger.info("Diagnóstico específico para S-2230 (Afastamentos/Atestados):")
                        
                        # Verificar caminho para infoAfastamento
                        if 'evtAfastTemp' in dados_json and 'infoAfastamento' in dados_json['evtAfastTemp']:
                            info_afast = dados_json['evtAfastTemp']['infoAfastamento']
                            self.logger.info(f"  - infoAfastamento encontrado: {list(info_afast.keys())}")
                            
                            # Verificar início do afastamento
                            if 'iniAfastamento' in info_afast:
                                ini_afast = info_afast['iniAfastamento']
                                self.logger.info(f"  - iniAfastamento encontrado: {list(ini_afast.keys())}")
                                
                                # Verificar informações de atestado
                                if 'infoAtestado' in ini_afast:
                                    info_atestado = ini_afast['infoAtestado']
                                    self.logger.info(f"  - infoAtestado encontrado: {list(info_atestado.keys() if isinstance(info_atestado, dict) else ['<lista>'])}")
                                else:
                                    self.logger.warning("  - infoAtestado não encontrado no registro")
                            else:
                                self.logger.warning("  - iniAfastamento não encontrado no registro")
                        else:
                            self.logger.warning("  - Caminho evtAfastTemp/infoAfastamento não encontrado")
                    
                    elif tabela == 'esocial_s1030':  # Cargos
                        self.logger.info("Diagnóstico específico para S-1030 (Cargos):")
                        
                        # Verificar caminho para infoCargo
                        if 'evtTabCargo' in dados_json and 'infoCargo' in dados_json['evtTabCargo']:
                            info_cargo = dados_json['evtTabCargo']['infoCargo']
                            self.logger.info(f"  - infoCargo encontrado: {list(info_cargo.keys())}")
                            
                            # Verificar dados do cargo
                            if 'dadosCargo' in info_cargo:
                                dados_cargo = info_cargo['dadosCargo']
                                tipo = type(dados_cargo).__name__
                                self.logger.info(f"  - dadosCargo encontrado (tipo: {tipo})")
                                if isinstance(dados_cargo, dict):
                                    self.logger.info(f"  - Campos do cargo: {list(dados_cargo.keys())}")
                            else:
                                self.logger.warning("  - dadosCargo não encontrado no registro")
                        else:
                            self.logger.warning("  - Caminho evtTabCargo/infoCargo não encontrado")
                
                except Exception as e:
                    self.logger.error(f"Erro no diagnóstico específico para {tabela}: {e}")
        
        self.logger.info(f"Diagnóstico concluído para tabela: {tabela}")
    
    def _extrair_valor_json_recursivo(self, dados_json, caminho):
        """
        Extrai um valor de um caminho JSON recursivamente, lidando com diferentes formatos de dados
        
        Args:
            dados_json: Dicionário JSON ou objeto aninhado
            caminho: Lista com o caminho para o valor desejado
            
        Returns:
            O valor encontrado ou None se não encontrado
        """
        if not dados_json or not caminho:
            return None
            
        temp = dados_json
        for parte in caminho:
            if isinstance(temp, dict) and parte in temp:
                temp = temp[parte]
            else:
                return None
        
        # Se o resultado é um dicionário com _text, retorna o valor de _text
        if isinstance(temp, dict) and "_text" in temp:
            return temp["_text"]
        
        return temp

# --- Local formatting utilities (replacing src.utils.formatador_dados_br) ---
def formatar_data_br(data_str):
    """Formata data de YYYY-MM-DD para DD/MM/YYYY"""
    if not data_str or not isinstance(data_str, str):
        return data_str
    try:
        if 'T' in data_str:
            data_str = data_str.split('T')[0]
        if len(data_str) == 10 and data_str.count('-') == 2:
            from datetime import datetime
            dt = datetime.strptime(data_str, '%Y-%m-%d')
            return dt.strftime('%d/%m/%Y')
    except:
        pass
    return data_str

def formatar_numero_br(valor, casas_decimais=2):
    """Formata número para formato brasileiro com vírgula como separador decimal"""
    if valor is None:
        return ''
    try:
        if isinstance(valor, str):
            valor = float(valor.replace(',', '.'))
        elif isinstance(valor, (int, float)):
            valor = float(valor)
        else:
            return str(valor)
        
        if valor.is_integer():
            return str(int(valor))
        return f'{valor:.{casas_decimais}f}'.replace('.', ',')
    except:
        return str(valor)
