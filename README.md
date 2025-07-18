# Processador e Migração de Dados do eSocial

## Descrição

Ferramenta para processamento e migração de dados do eSocial. O sistema processa arquivos XML do eSocial de diferentes versões de layouts (S-1020, S-1030, S-1200, S-2200, S-2205, S-2206, S-2230), armazena temporariamente em banco de dados SQLite e exporta para arquivos de saída conforme os templates definidos.

## Funcionalidades

- Processamento de múltiplos layouts do eSocial
- Detecção automática de layout dos arquivos XML
- Tratamento adequado de namespaces XML
- Armazenamento dos dados em banco SQLite
- Exportação para arquivos CSV padronizados, conforme templates definidos em proposta comercial
- Interface gráfica para facilitar a utilização
- Logs detalhados de operações e erros

## Layouts Suportados

Os seguintes layouts do eSocial são processados:

- S-1020: Tabela de Lotações Tributárias
- S-1030: Tabela de Cargos/Funções
- S-1200: Remuneração do Trabalhador
- S-2200: Cadastramento Inicial do Vínculo e Admissão/Ingresso do Trabalhador
- S-2205: Alteração de Dados Cadastrais do Trabalhador
- S-2206: Alteração de Contrato de Trabalho/Relação Estatutária
- S-2230: Afastamento Temporário

## Templates de Saída

Os seguintes arquivos CSV são gerados automaticamente a partir dos dados processados:

1. 01_CONVTRABALHADOR.csv – Trabalhador (S-2200, S-2205, S-2206)
2. 02_CONVCONTRATO.csv – Contrato (S-2200, S-2205, S-2206)
3. 03_CONVCONTRATOALT.csv – Contrato Alterações (S-2200, S-2205, S-2206)
4. 04_CONVDEPENDENTE.csv – Dependentes (S-2200, S-2205, S-2206)
5. 05_FERIAS.csv – Férias (S-2230, se enviado como afastamento)
6. 06_CONVFICHA.csv – Ficha Financeira (S-1200)
7. 07_CARGOS.csv – Cargos (S-1030)
8. 08_CONVAFASTAMENTO.csv – Afastamentos (S-2230)
9. 09_CONVATESTADO.csv – Atestados Médicos (S-2230, apenas afastamentos abaixo de 15 dias)

Todos os arquivos são gerados na pasta `data/output/` seguindo o padrão acima.

## Instalação

```bash
pip install -r requirements.txt
```

## Uso

1. Coloque os arquivos XML do eSocial na pasta `data/input/`
2. Execute o script principal:

```bash
python run.py
```

3. Os arquivos CSV de saída serão gerados na pasta `data/output/`

## Configuração

As configurações podem ser ajustadas no arquivo `.env` ou `config/settings.py`.
Ag

## Testes

O projeto utiliza pytest para testes automatizados. Os testes estão organizados na pasta `tests/` e são executados automaticamente via GitHub Actions sempre que houver um push ou pull request para as branches principais.

### Estrutura de Testes

- `tests/conftest.py`: Configurações e fixtures compartilhadas entre os testes
- `tests/test_database.py`: Testes para funcionalidades de banco de dados
- `tests/test_layout_processor.py`: Testes para o processador de layouts
- `tests/test_xml_processor.py`: Testes para o processador XML
- `tests/test_exportador_generico.py`: Testes para o exportador de dados
- `tests/test_gui.py`: Testes para a interface gráfica

### Executando os Testes

Para executar os testes:

```bash
# Executar todos os testes
python -m pytest tests/

# Executar com relatório de cobertura
python -m pytest --cov=src tests/

# Executar testes específicos
python -m pytest tests/test_database.py
```
