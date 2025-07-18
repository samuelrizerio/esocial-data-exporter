"""
Esquemas de tabelas para o banco de dados SQLite
"""

import sqlite3
from typing import Dict, List, Any

# Esquemas de tabelas para cada layout do eSocial
TABLE_SCHEMAS = {

    
    # S-1020: Tabela de Lotacoes Tributarias (Tomador) - 100% Coverage
    "S-1020": """
        CREATE TABLE IF NOT EXISTS esocial_s1020 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            -- Identificacao
            codigo TEXT,
            cod_lotacao TEXT,
            descricao TEXT,
            desc_lotacao TEXT,
            tipo_lotacao TEXT,
            tipo_inscricao TEXT,
            nr_inscricao TEXT,
            
            -- Validade
            inicio_validade TEXT,
            fim_validade TEXT,
            nova_ini_valid TEXT,
            nova_fim_valid TEXT,
            
            -- FPAS
            fpas TEXT,
            cod_tercs TEXT,
            cod_tercs_susp TEXT,
            
            -- Processo Judicial Terceiros
            proc_jud_terceiros_cod_susp TEXT,
            proc_jud_terceiros_cod_terc TEXT,
            proc_jud_terceiros_nr_proc_jud TEXT,
            proc_jud_terceiro_cod_susp TEXT,
            proc_jud_terceiro_cod_terc TEXT,
            proc_jud_terceiro_nr_proc_jud TEXT,
            
            -- infoEmprParcial
            tp_insc_contrat TEXT,
            nr_insc_contrat TEXT,
            tp_insc_prop TEXT,
            nr_insc_prop TEXT,
            
            -- dadosOpPort
            aliq_rat TEXT,
            fap TEXT,
            
            -- Dados do empregador
            cnpj_empregador TEXT,
            
            -- JSON completo para analise
            json_data TEXT,
            data_importacao TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """,
    
    # S-1030: Tabela de Cargos/Funções - 100% Coverage
    "S-1030": """
        CREATE TABLE IF NOT EXISTS esocial_s1030 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            -- Dados do evento
            tipo_ambiente TEXT,
            processo_emissor TEXT,
            versao_processo TEXT,
            tipo_inscricao TEXT,
            
            -- Dados de identificação do cargo
            codigo TEXT,
            inicio_validade TEXT,
            fim_validade TEXT,
            
            -- Dados básicos do cargo
            descricao TEXT,
            cbo TEXT,
            cargo_publico TEXT,
            
            -- Dados complementares do cargo
            nivel_cargo TEXT,
            desc_sumaria TEXT,
            dt_criacao TEXT,
            dt_extincao TEXT,
            situacao TEXT,
            permite_acumulo TEXT,
            permite_contagem_esp TEXT,
            dedicacao_exclusiva TEXT,
            num_lei TEXT,
            dt_lei TEXT,
            situacao_lei TEXT,
            tem_funcao TEXT,
            
            -- Dados do empregador
            cnpj_empregador TEXT,
            
            -- JSON completo para análise
            json_data TEXT,
            data_importacao TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """,
    
    # S-1200: Remuneração do Trabalhador
    "S-1200": """
        CREATE TABLE IF NOT EXISTS esocial_s1200 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            periodo_apuracao TEXT,
            cpf_trabalhador TEXT,
            matricula TEXT,
            categoria TEXT,
            estabelecimento TEXT,
            codigo_rubrica TEXT,
            descricao_rubrica TEXT,
            valor_rubrica REAL,
            tipo_rubrica TEXT,
            cnpj_empregador TEXT,
            json_data TEXT,
            data_importacao TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """,
    
    # S-2200: Cadastramento Inicial do Vínculo - 100% Coverage
    "S-2200": """
        CREATE TABLE IF NOT EXISTS esocial_s2200 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            -- Dados básicos do trabalhador
            cpf_trabalhador TEXT,
            nome_trabalhador TEXT,
            sexo TEXT,
            raca_cor TEXT,
            estado_civil TEXT,
            grau_instrucao TEXT,
            nome_social TEXT,
            
            -- Nascimento
            data_nascimento TEXT,
            nm_mae TEXT,
            nm_pai TEXT,
            uf_nasc TEXT,
            pais_nasc TEXT,
            pais_nac TEXT,
            
            -- Endereço Brasil
            tp_lograd TEXT,
            dsc_lograd TEXT,
            nr_lograd TEXT,
            complemento TEXT,
            cep TEXT,
            bairro TEXT,
            cod_munic TEXT,
            nm_cidade TEXT,
            uf_resid TEXT,
            
            -- Endereço Exterior
            pais_resid TEXT,
            bairro_ext TEXT,
            dsc_lograd_ext TEXT,
            nr_lograd_ext TEXT,
            complemento_ext TEXT,
            nm_cidade_ext TEXT,
            cod_postal_ext TEXT,
            
            -- Trabalhador Imigrante
            tmp_resid TEXT,
            cond_ing TEXT,
            
            -- InfoDeficiencia
            def_fisica TEXT,
            def_visual TEXT,
            def_auditiva TEXT,
            def_mental TEXT,
            def_intelectual TEXT,
            reab_readap TEXT,
            info_cota TEXT,
            observacao_def TEXT,
            
            -- Contato
            fone_princ TEXT,
            fone_alt TEXT,
            email_princ TEXT,
            email_alt TEXT,
            contato_emerg TEXT,
            fone_emerg TEXT,
            parentesco_emerg TEXT,
            
            -- Documentos - Enhanced
            nis_trabalhador TEXT,
            nr_rg TEXT,
            orgao_emissor_rg TEXT,
            dt_exped_rg TEXT,
            uf_rg TEXT,
            nr_ctps TEXT,
            serie_ctps TEXT,
            uf_ctps TEXT,
            dt_exped_ctps TEXT,
            nr_reg_cnh TEXT,
            categoria_cnh TEXT,
            uf_cnh TEXT,
            dt_exped_cnh TEXT,
            dt_pri_hab TEXT,
            dt_valid_cnh TEXT,
            nr_rne TEXT,
            orgao_emissor_rne TEXT,
            uf_rne TEXT,
            dt_exped_rne TEXT,
            nr_passaporte TEXT,
            pais_origem_passaporte TEXT,
            dt_exped_passaporte TEXT,
            dt_valid_passaporte TEXT,
            nr_ric TEXT,
            orgao_emissor_ric TEXT,
            uf_ric TEXT,
            dt_exped_ric TEXT,
            nr_titulo TEXT,
            zona_titulo TEXT,
            secao_titulo TEXT,
            cod_munic_titulo TEXT,
            nm_cidade_titulo TEXT,
            uf_titulo TEXT,
            dt_exped_titulo TEXT,
            nr_certidao TEXT,
            dt_exped_certidao TEXT,
            regiao_militar TEXT,
            tipo_certidao TEXT,
            nr_certidao2 TEXT,
            nr_serie TEXT,
            dt_exped_certidao2 TEXT,
            categoria_certidao TEXT,
            nr_registro_conselho TEXT,
            orgao_emissor_conselho TEXT,
            uf_conselho TEXT,
            dt_exped_conselho TEXT,
            dt_validade_conselho TEXT,
            
            -- Trabalhador Estrangeiro
            dt_chegada TEXT,
            class_trab_estrang TEXT,
            casado_br TEXT,
            filhos_br TEXT,
            
            -- Vínculo
            matricula TEXT,
            tp_reg_trab TEXT,
            tp_reg_prev TEXT,
            cad_ini TEXT,
            
            -- InfoCeletista
            dt_adm TEXT,
            tp_admissao TEXT,
            ind_admissao TEXT,
            nr_proc_trab TEXT,
            tp_reg_jor TEXT,
            nat_atividade TEXT,
            dt_base TEXT,
            cnpj_sind_categ_prof TEXT,
            mat_anot_jud TEXT,
            dt_opc_fgts TEXT,
            
            -- Trabalho Temporário
            hip_leg TEXT,
            just_contr TEXT,
            tp_insc_estab TEXT,
            nr_insc_estab TEXT,
            cpf_trab_subst TEXT,
            
            -- InfoEstatutario
            tp_prov TEXT,
            dt_exercicio TEXT,
            tp_plan_rp TEXT,
            ind_teto_rgps TEXT,
            ind_abono_perm TEXT,
            dt_ini_abono TEXT,
            
            -- InfoContrato
            nm_cargo TEXT,
            cbo_cargo TEXT,
            dt_ingr_cargo TEXT,
            nm_funcao TEXT,
            cbo_funcao TEXT,
            acum_cargo TEXT,
            cod_categoria TEXT,
            salario_contratual REAL,
            und_sal_fixo TEXT,
            tipo_contrato TEXT,
            duracao_contrato TEXT,
            clau_assec TEXT,
            obj_det TEXT,
            
            -- Sucessão de Vínculo
            sucessao_tp_insc TEXT,
            sucessao_nr_insc TEXT,
            sucessao_matric_ant TEXT,
            sucessao_dt_transf TEXT,
            sucessao_observacao TEXT,
            
            -- Transferência Doméstica
            cpf_substituido TEXT,
            transf_matric_ant TEXT,
            transf_dt_transf TEXT,
            
            -- Mudança de CPF
            cpf_ant TEXT,
            mudanca_matric_ant TEXT,
            dt_alt_cpf TEXT,
            mudanca_observacao TEXT,
            
            -- Afastamento
            dt_ini_afast TEXT,
            cod_mot_afast TEXT,
            
            -- Desligamento
            dt_deslig TEXT,
            
            -- Cessão
            dt_ini_cessao TEXT,
            
            -- Dados do empregador
            cnpj_empregador TEXT,
            
            -- JSON completo para análise
            json_data TEXT,
            data_importacao TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """,
    # Tabela de dependentes vinculada ao trabalhador (S-2200) - 100% Coverage
    "dependentes": """
        CREATE TABLE IF NOT EXISTS esocial_dependentes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cpf_trabalhador TEXT,
            matricula TEXT,
            nome_dependente TEXT,
            cpf_dependente TEXT,
            tipo_dependente TEXT,
            sexo_dependente TEXT,
            data_nascimento TEXT,
            dep_irrf TEXT,
            dep_sf TEXT,
            inc_trab TEXT,
            descr_dep TEXT,
            cnpj_empregador TEXT,
            json_data TEXT,
            data_importacao TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """,
    # S-2205: Alteração de Dados Cadastrais
    "S-2205": """
        CREATE TABLE IF NOT EXISTS esocial_s2205 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cpf_trabalhador TEXT,
            nome_trabalhador TEXT,
            data_alteracao TEXT,
            sexo TEXT,
            raca_cor TEXT,
            estado_civil TEXT,
            grau_instrucao TEXT,
            data_nascimento TEXT,
            cnpj_empregador TEXT,
            matricula TEXT,
            json_data TEXT,
            data_importacao TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """,
    
    # S-2206: Alteração de Contrato de Trabalho
    "S-2206": """
        CREATE TABLE IF NOT EXISTS esocial_s2206 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cpf_trabalhador TEXT,
            matricula TEXT,
            data_alteracao TEXT,
            cod_cargo TEXT,
            cod_funcao TEXT,
            cod_lotacao TEXT,
            salario_contratual REAL,
            tipo_contrato TEXT,
            duracao_contrato TEXT,
            cnpj_empregador TEXT,
            json_data TEXT,
            data_importacao TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(cpf_trabalhador, matricula, data_alteracao)
        )
    """,
    
    # S-2230: Afastamento Temporário
    "S-2230": """
        CREATE TABLE IF NOT EXISTS esocial_s2230 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cpf_trabalhador TEXT,
            matricula TEXT,
            data_inicio TEXT,
            data_fim TEXT,
            codigo_motivo TEXT,
            descricao_motivo TEXT,
            cnpj_empregador TEXT,
            json_data TEXT,
            data_importacao TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """,
    
}

# Índices para melhorar a performance das consultas
INDEXES = {
    # S-1020: Tabela de Lotações Tributárias
    "idx_s1020_codigo": "CREATE INDEX IF NOT EXISTS idx_s1020_codigo ON esocial_s1020 (codigo)",
    "idx_s1020_cnpj": "CREATE INDEX IF NOT EXISTS idx_s1020_cnpj ON esocial_s1020 (cnpj_empregador)",
    
    # S-1030: Tabela de Cargos/Funções
    "idx_s1030_codigo": "CREATE INDEX IF NOT EXISTS idx_s1030_codigo ON esocial_s1030 (codigo)",
    "idx_s1030_cnpj": "CREATE INDEX IF NOT EXISTS idx_s1030_cnpj ON esocial_s1030 (cnpj_empregador)",
    
    # S-1200: Remuneração do Trabalhador
    "idx_s1200_periodo": "CREATE INDEX IF NOT EXISTS idx_s1200_periodo ON esocial_s1200 (periodo_apuracao)",
    "idx_s1200_cpf": "CREATE INDEX IF NOT EXISTS idx_s1200_cpf ON esocial_s1200 (cpf_trabalhador)",
    "idx_s1200_matricula": "CREATE INDEX IF NOT EXISTS idx_s1200_matricula ON esocial_s1200 (matricula)",
    "idx_s1200_cnpj": "CREATE INDEX IF NOT EXISTS idx_s1200_cnpj ON esocial_s1200 (cnpj_empregador)",
    
    # S-2200: Cadastramento Inicial do Vínculo
    "idx_s2200_cpf": "CREATE INDEX IF NOT EXISTS idx_s2200_cpf ON esocial_s2200 (cpf_trabalhador)",
    "idx_s2200_matricula": "CREATE INDEX IF NOT EXISTS idx_s2200_matricula ON esocial_s2200 (matricula)",
    "idx_s2200_cnpj": "CREATE INDEX IF NOT EXISTS idx_s2200_cnpj ON esocial_s2200 (cnpj_empregador)",
    
    # S-2205: Alteração de Dados Cadastrais
    "idx_s2205_cpf": "CREATE INDEX IF NOT EXISTS idx_s2205_cpf ON esocial_s2205 (cpf_trabalhador)",
    "idx_s2205_matricula": "CREATE INDEX IF NOT EXISTS idx_s2205_matricula ON esocial_s2205 (matricula)",
    "idx_s2205_data_alt": "CREATE INDEX IF NOT EXISTS idx_s2205_data_alt ON esocial_s2205 (data_alteracao)",
    
    # S-2206: Alteração de Contrato de Trabalho
    "idx_s2206_cpf": "CREATE INDEX IF NOT EXISTS idx_s2206_cpf ON esocial_s2206 (cpf_trabalhador)",
    "idx_s2206_matricula": "CREATE INDEX IF NOT EXISTS idx_s2206_matricula ON esocial_s2206 (matricula)",
    "idx_s2206_data_alt": "CREATE INDEX IF NOT EXISTS idx_s2206_data_alt ON esocial_s2206 (data_alteracao)",
    
    # S-2230: Afastamento Temporário
    "idx_s2230_cpf": "CREATE INDEX IF NOT EXISTS idx_s2230_cpf ON esocial_s2230 (cpf_trabalhador)",
    "idx_s2230_matricula": "CREATE INDEX IF NOT EXISTS idx_s2230_matricula ON esocial_s2230 (matricula)",
    "idx_s2230_data_inicio": "CREATE INDEX IF NOT EXISTS idx_s2230_data_inicio ON esocial_s2230 (data_inicio)",
}

# Consultas SQL para exportação de dados
EXPORT_QUERIES = {
    # Funcionários - Dados consolidados de funcionários
    "funcionarios": """
        SELECT 
            s2200.cpf_trabalhador AS cpf,
            s2200.nome_trabalhador AS nome,
            '' AS pis,
            s2200.sexo,
            s2200.raca_cor,
            s2200.estado_civil,
            s2200.grau_instrucao,
            s2200.data_nascimento,
            '' AS ctps_numero,
            '' AS ctps_serie,
            '' AS ctps_uf,
            s2200.matricula,
            s2200.dt_adm AS data_admissao,
            s2200.tp_admissao AS tipo_admissao,
            s2200.tp_reg_jor AS tipo_regime_jornada,
            s2200.nat_atividade AS natureza_atividade,
            s2200.cod_categoria,
            s2200.tipo_contrato,
            s2200.duracao_contrato,
            s2200.cnpj_empregador
        FROM esocial_s2200 s2200
    """,
    
    # Cargos - Dados de cargos
    "cargos": """
        SELECT 
            codigo,
            descricao,
            cbo,
            inicio_validade,
            fim_validade,
            cnpj_empregador
        FROM esocial_s1030
    """,
    
    # Lotações - Dados de lotações
    "lotacoes": """
        SELECT 
            codigo,
            descricao,
            tipo_lotacao,
            tipo_inscricao,
            nr_inscricao,
            inicio_validade,
            fim_validade,
            cnpj_empregador
        FROM esocial_s1020
    """,
    
    # Remunerações - Dados de remuneração
    "remuneracoes": """
        SELECT 
            periodo_apuracao,
            cpf_trabalhador,
            matricula,
            categoria,
            estabelecimento,
            codigo_rubrica,
            descricao_rubrica,
            valor_rubrica,
            tipo_rubrica,
            cnpj_empregador
        FROM esocial_s1200
    """,
    
    # Afastamentos - Dados de afastamento
    "afastamentos": """
        SELECT 
            cpf_trabalhador,
            matricula,
            data_inicio,
            data_fim,
            codigo_motivo,
            descricao_motivo,
            cnpj_empregador
        FROM esocial_s2230
    """,
    
    # Export queries for direct table access
    "esocial_s1020": "SELECT * FROM esocial_s1020",
    "esocial_s1030": "SELECT * FROM esocial_s1030",
    "esocial_s1200": "SELECT * FROM esocial_s1200",
    "esocial_s2200": "SELECT * FROM esocial_s2200",
    "esocial_s2205": "SELECT * FROM esocial_s2205",
    "esocial_s2206": "SELECT * FROM esocial_s2206",
    "esocial_s2230": "SELECT * FROM esocial_s2230",
    "esocial_dependentes": "SELECT * FROM esocial_dependentes",
}
