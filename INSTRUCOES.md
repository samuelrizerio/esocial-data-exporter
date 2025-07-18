# Instruções de Uso - Processador eSocial

## Configuração do Ambiente

### Requisitos

- Python 3.6 ou superior
- Bibliotecas necessárias (instaláveis via pip):
  - lxml
  - tqdm
  - Tkinter (para interface gráfica)

### Instalação

1. Clone o repositório ou descompacte o arquivo do projeto:

```bash
git clone [url-do-repositorio]
```

2. Acesse o diretório do projeto:

```bash
cd esocial-migration
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

## Modo de Uso

### Interface Gráfica

1. Execute o script da interface gráfica:

```bash
python esocial_gui.py
```

2. Na interface:
   - Selecione o diretório com os arquivos XML do eSocial
   - Escolha o diretório de saída para salvar os arquivos exportados
   - Clique em "Processar Arquivos XML"
   - Após o processamento, vá para a aba "Exportar" e clique em "Exportar"

### Linha de Comando

Para processar via linha de comando:

1. Execute o script principal:

```bash
python run.py --input [diretorio-dos-xmls] --output [diretorio-de-saida]
```

Parâmetros disponíveis:

- `--input`, `-i`: Diretório contendo os arquivos XML do eSocial
- `--output`, `-o`: Diretório onde serão salvos os arquivos de saída
- `--database`, `-d`: Caminho para o arquivo do banco de dados SQLite (opcional)
- `--templates`, `-t`: Diretório contendo os templates para exportação (opcional)
- `--log-level`, `-l`: Nível de log (DEBUG, INFO, WARNING, ERROR) (opcional)

## Organização dos XML

Os arquivos XML devem seguir o formato definido pelo eSocial, com suporte para os seguintes layouts:

- S-1020: Tabela de Lotações Tributárias
- S-1030: Tabela de Cargos/Funções
- S-1200: Remuneração do Trabalhador
- S-2200: Cadastramento Inicial do Vínculo e Admissão/Ingresso do Trabalhador
- S-2205: Alteração de Dados Cadastrais do Trabalhador
- S-2206: Alteração de Contrato de Trabalho/Relação Estatutária
- S-2230: Afastamento Temporário

## Dados Exportados

Os dados são exportados conforme os templates definidos na pasta `templates/`. Cada template especifica o formato de saída, incluindo os nomes das colunas e os mapeamentos para os campos do eSocial.

## Solução de Problemas

### Erros comuns

1. **Erro ao abrir arquivo XML**:

   - Verifique se o arquivo está íntegro e segue o formato do eSocial
   - Verifique permissões de leitura no arquivo

2. **Layout não reconhecido**:

   - Verifique se o arquivo XML está no formato correto do eSocial
   - O sistema suporta múltiplas versões do eSocial, mas alguns layouts podem não ser reconhecidos

3. **Erro ao exportar para arquivo de saída**:
   - Verifique se existe template correspondente na pasta de templates
   - Verifique permissões de escrita no diretório de saída

### Logs

Os logs da aplicação são armazenados na pasta `logs/` e podem ser úteis para diagnóstico de problemas.
