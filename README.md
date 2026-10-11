# Automação de relatórios do Google Analytics 4 — Inyaga

Projeto em Python que consulta a propriedade do Google Analytics 4 (GA4) do site do projeto Inyaga e consolida seis relatórios em uma planilha Excel. A automação combina consultas à API, tratamento tabular com Pandas, atualização de abas com OpenPyXL, logging e acionamento de um fluxo do Power Automate Desktop (PAD).

> **Estado:** em desenvolvimento. A documentação descreve o código inspecionado; a execução ponta a ponta, o acesso à propriedade GA4 e o fluxo PAD não foram validados nesta revisão.

## Objetivos

- Automatizar consultas recorrentes ao GA4.
- Consolidar os resultados em abas específicas de uma planilha Excel.
- Atualizar registros por chaves definidas para cada relatório, reduzindo duplicações.
- Evitar substituir uma aba existente quando uma consulta não retorna dados.
- Registrar eventos e falhas para apoiar o diagnóstico.
- Solicitar a execução de um fluxo do Power Automate Desktop após a geração da planilha.

## Relatórios

Os seis scripts consultam, por padrão, o período de **sete dias atrás até ontem** (7daysAgo a yesterday).

| Script | Aba no Excel | Dimensões e indicadores principais |
| --- | --- | --- |
| **script_resumo_trafego.py** | Resumo_Diario | Data; usuários ativos e novos, sessões, visualizações, taxa de engajamento, duração média da sessão e eventos. |
| **script_paginas.py** | Paginas | Data, caminho e título da página; usuários ativos, sessões, visualizações e engajamento. |
| **script_aquisicao.py** | Aquisicao | Data, grupo de canais, origem e meio; usuários, sessões, visualizações e engajamento. |
| **script_dispositivos.py** | Dispositivos | Data e categoria de dispositivo; usuários, sessões, visualizações e engajamento. |
| **script_localizacao.py** | Localização | Data, país, região e cidade; usuários, sessões e visualizações. |
| **script_eventos.py** | Eventos | Data e nome do evento; contagem de eventos e usuários. |

O arquivo de saída é **output/relatorio_site_inyaga.xlsx**. A rotina **atualizar_planilha**, em **planilha_utils.py**, valida o tipo dos dados, nomes de colunas duplicados, presença das colunas-chave e valores nulos nas chaves. Ela combina os dados novos com os existentes, mantém o registro mais recente para cada chave e substitui apenas a aba correspondente. Quando a API não retorna linhas, os scripts interrompem a atualização em vez de gravar uma tabela vazia.

As chaves de consolidação configuradas nos scripts são:

- Resumo diário: data
- Páginas: data + endereco
- Aquisição: data + canal + origem + meio
- Dispositivos: data + dispositivo
- Localização: data + pais + estado + cidade
- Eventos: data + evento

## Tecnologias

- **Python** — orquestração e processamento.
- **Google Analytics Data API** e pacote google-analytics-data — consultas à propriedade GA4.
- **Pandas** — transformação, validação e consolidação tabular.
- **OpenPyXL** — atualização do arquivo Excel.
- **Power Automate Desktop** — execução de um fluxo externo à aplicação Python.
- **Logging** — mensagens de execução e diagnóstico.
- **Git/GitHub** — versionamento do projeto.

## Estrutura

~~~text
.
├── main.py
├── planilha_utils.py
├── script_resumo_trafego.py
├── script_paginas.py
├── script_aquisicao.py
├── script_dispositivos.py
├── script_localizacao.py
├── script_eventos.py
├── requirements.txt
├── docs/
│   └── monitoramento_power_automate.md
├── logs/
│   └── automacao.log
└── output/
    ├── relatorio_site_inyaga.xlsx
    └── flow_status.json
~~~

A pasta output é criada pelo programa quando necessário; a planilha e o arquivo de status são artefatos de execução e podem não existir antes da primeira execução. O repositório também contém atualmente um diretório __pycache__ versionado, que não aparece na estrutura acima por ser artefato gerado.

## Pré-requisitos

- Windows, pois o acionamento do PAD utiliza os.startfile e o esquema de URL ms-powerautomate:.
- Python e acesso ao terminal.
- Acesso autorizado à propriedade GA4 configurada nos scripts.
- Credenciais Google com permissão para consultar essa propriedade, configuradas por Application Default Credentials (ADC).
- Power Automate Desktop instalado e configurado com o fluxo correspondente.
- Excel ou outro leitor compatível para abrir a planilha gerada (opcional).

As versões das bibliotecas estão listadas em requirements.txt. Não foi definida nem validada nesta revisão uma versão mínima específica de Python.

## Configuração e execução

### 1. Clonar o repositório

~~~bash
git clone https://github.com/wiUl/google-analytics-project.git
cd google-analytics-project
~~~

### 2. Criar e ativar um ambiente virtual

~~~bash
python -m venv .venv
~~~

No Windows PowerShell:

~~~powershell
.venv\Scripts\Activate.ps1
~~~

### 3. Instalar dependências

~~~bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
~~~

### 4. Configurar a autenticação do Google

O cliente BetaAnalyticsDataClient usa as credenciais padrão do Google. Configure ADC com uma identidade autorizada a consultar a propriedade GA4. Consulte a [documentação oficial de Application Default Credentials](https://cloud.google.com/docs/authentication/provide-credentials-adc).

**Não versione chaves privadas, arquivos de credenciais, tokens ou segredos.** Mantenha as credenciais fora do repositório.

### 5. Conferir os parâmetros locais

Antes de executar, confira os identificadores da propriedade GA4 definidos nos seis scripts de relatório e a constante FLOW_BASE_URL em main.py. Atualmente, esses parâmetros estão definidos diretamente no código; não são carregados de variáveis de ambiente. Configure-os para os recursos aos quais você tem acesso e não compartilhe identificadores internos desnecessariamente.

### 6. Executar

~~~bash
python main.py
~~~

O programa executa os seis scripts em sequência. Se algum script terminar com erro, a orquestração é interrompida. Depois das consultas, verifica se a planilha foi criada e não está vazia; em seguida, solicita a abertura do fluxo PAD e aguarda um resultado no arquivo output/flow_status.json.

## Integração com Power Automate Desktop

O monitoramento depende de um arquivo de status que o próprio fluxo PAD deve gravar ao terminar. As instruções de configuração estão em [docs/monitoramento_power_automate.md](docs/monitoramento_power_automate.md).

Resultado esperado em caso de sucesso:

~~~json
{"status": "success"}
~~~

Resultado esperado em caso de falha:

~~~json
{"status": "error", "message": "Descrição do erro"}
~~~

O Python consulta o arquivo a cada cinco segundos, por até 30 minutos. A abertura da URL do PAD apenas solicita a execução; o arquivo de status é que informa ao programa o resultado comunicado pelo fluxo. O PAD precisa ter permissão de escrita na pasta output do mesmo diretório local do projeto.

## Logs e diagnóstico

- Log: logs/automacao.log
- Planilha: output/relatorio_site_inyaga.xlsx
- Status do fluxo: output/flow_status.json

| Sintoma | Verificação sugerida |
| --- | --- |
| Erro de autenticação | Confira as ADC e as permissões de acesso à propriedade GA4. |
| Consulta sem linhas | Verifique o período, as dimensões, as métricas e se há dados disponíveis na propriedade. A execução cancela a atualização quando o resultado está vazio. |
| Falha ao gravar o Excel | Feche a planilha caso esteja aberta e confira as permissões do diretório. |
| Timeout do PAD | Confira se o fluxo correto iniciou e se grava um JSON válido no caminho esperado. |
| Módulo não encontrado | Ative o ambiente virtual correto e reinstale as dependências de requirements.txt. |

## Limitações e próximos passos

- A propriedade GA4 e a URL do fluxo PAD são configuradas diretamente nos arquivos Python; parametrizá-las por configuração externa melhoraria a portabilidade.
- O funcionamento ponta a ponta depende de credenciais Google válidas e de um fluxo PAD configurado no Windows.
- Não há testes automatizados identificados no escopo desta revisão; a execução e os resultados não foram verificados nesta tarefa.
- Recomenda-se adicionar __pycache__/ e logs gerados ao .gitignore e remover os artefatos gerados atualmente versionados em uma alteração separada. O arquivo logs/automacao.log deve ser revisado para garantir que não contenha dados operacionais sensíveis.
- Recomenda-se criar testes unitários para a validação, deduplicação e preservação de abas em planilha_utils.py.
- Recomenda-se mover os parâmetros de ambiente para configuração externa e documentar o procedimento de configuração do fluxo PAD.

## Autoria

Projeto hospedado por [wiUl no GitHub](https://github.com/wiUl). O escopo é a automação de relatórios de tráfego e engajamento para o site Inyaga.
