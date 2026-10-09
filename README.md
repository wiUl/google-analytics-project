# Análise de tráfego do site Inyaga — Google Analytics

Projeto de automação para coletar, tratar e consolidar dados do Google Analytics 4 (GA4) do site do projeto Inyaga. Os relatórios são obtidos pela API do Google Analytics e organizados em uma planilha Excel para apoiar análises de tráfego, engajamento, aquisição e comportamento dos visitantes.

O repositório reúne scripts Python para consultar diferentes dimensões e métricas do GA4, utilitários para validar e consolidar resultados e um script principal que coordena a execução dos relatórios e aciona um fluxo do Power Automate Desktop.

## Objetivos
- Automatizar a extração de dados do Google Analytics 4.
- Organizar os resultados em abas específicas de uma única planilha Excel.
- Evitar registros duplicados por meio de chaves definidas para cada relatório.
- Preservar dados existentes quando uma consulta não retorna linhas.
- Registrar eventos, avisos e falhas para facilitar o diagnóstico.
- Acionar um fluxo do Power Automate Desktop após a geração dos relatórios.

## Tecnologias utilizadas
| Tecnologia | Utilização |
| --- | --- |
| **Python** | Linguagem principal e orquestração da automação. |
| **Google Analytics Data API (GA4)** | Consulta de dimensões e métricas da propriedade de Analytics. |
| **google-analytics-data** | Cliente Python para acessar a API do Google Analytics. |
| **Pandas** | Transformação, validação e consolidação dos dados em DataFrames. |
| **OpenPyXL** | Escrita e atualização das abas do arquivo Excel. |
| **Excel (.xlsx)** | Formato de saída dos relatórios. |
| **Power Automate Desktop** | Acionamento de um fluxo de automação após a atualização da planilha. |
| **Logging** | Registro de eventos no terminal e em arquivo. |
| **Git e GitHub** | Versionamento e hospedagem do código. |

## Relatórios gerados
Os scripts consultam, por padrão, o período dos **últimos sete dias até ontem** (7daysAgo a yesterday). Os resultados são consolidados em output/relatorio_site_inyaga.xlsx.

| Script | Aba do Excel | Conteúdo |
| --- | --- | --- |
| script_resumo_trafego.py | Resumo_Diario | Indicadores diários gerais: usuários ativos, novos usuários, sessões, visualizações, taxa de engajamento, duração média da sessão e eventos. |
| script_paginas.py | Paginas | Desempenho de páginas por data, endereço e título, com métricas de audiência e engajamento. |
| script_aquisicao.py | Aquisicao | Aquisição por grupo de canais padrão da sessão, origem e meio. |
| script_dispositivos.py | Dispositivos | Métricas por data e categoria de dispositivo. |
| script_localizacao.py | Localização | Métricas por data, país, região/estado e cidade. |
| script_eventos.py | Eventos | Ocorrências de eventos e usuários por data e nome do evento. |

### Atualização e validação
O módulo planilha_utils.py centraliza a atualização das abas. Ele verifica o formato dos dados, a presença das colunas-chave e se os valores dessas chaves estão preenchidos. Em seguida, combina registros antigos e novos, remove duplicatas mantendo a versão mais recente e ordena os dados antes de salvar a aba correspondente.

Se uma consulta não retornar linhas, a rotina evita substituir a aba existente por uma tabela vazia. Erros de gravação também são registrados.

## Estrutura do repositório
```text
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
├── logs/
│   └── automacao.log
└── output/
    ├── relatorio_site_inyaga.xlsx
    └── flow_status.json
```

As pastas logs/ e output/ são criadas pelo programa quando necessário. Os arquivos gerados durante a execução podem não estar versionados no Git.

## Pré-requisitos
- Windows, para o acionamento do Power Automate Desktop pelo esquema de URL ms-powerautomate:.
- Python instalado e acessível pelo terminal.
- Acesso à propriedade do Google Analytics 4 consultada pelo projeto.
- Credenciais do Google com permissão para consultar a propriedade.
- Power Automate Desktop instalado e com o fluxo correto configurado.
- Excel ou aplicativo compatível para consultar a planilha gerada (opcional).

## Configuração e execução
### 1. Clonar o repositório
```bash
git clone https://github.com/wiUl/google-analytics-project.git
cd google-analytics-project
```

### 2. Criar e ativar um ambiente virtual
```bash
python -m venv .venv
```
No Windows PowerShell:
```powershell
.venv\Scripts\Activate.ps1
```

### 3. Instalar as dependências
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configurar a autenticação do Google
O cliente BetaAnalyticsDataClient utiliza as credenciais padrão do Google (Application Default Credentials). Configure uma conta ou conta de serviço autorizada a consultar a propriedade GA4, seguindo a [documentação oficial sobre Application Default Credentials](https://cloud.google.com/docs/authentication/provide-credentials-adc).

**Não versione arquivos de credenciais, chaves privadas ou tokens.** Mantenha-os fora do repositório.

### 5. Executar a automação
Com as credenciais configuradas e o Power Automate Desktop preparado, execute:
```bash
python main.py
```

O main.py executa sequencialmente os seis scripts. Se algum deles falhar, a execução é interrompida e o erro é registrado. Após verificar que a planilha foi criada e não está vazia, o programa solicita a execução do fluxo do Power Automate Desktop.

## Integração com Power Automate Desktop
A URL de execução é configurada pela constante FLOW_BASE_URL em main.py. Ela deve apontar para o ambiente e o identificador do fluxo correto.

Para o Python detectar o término do fluxo, o Power Automate Desktop precisa gravar output/flow_status.json ao final da execução, na pasta output deste projeto.

Em caso de sucesso, o conteúdo esperado é:
```json
{"status": "success"}
```
Em caso de falha:
```json
{"status": "error", "message": "Descrição do erro"}
```

O programa verifica o arquivo a cada cinco segundos e aguarda até 30 minutos. Se o arquivo não for criado, a execução termina com erro de tempo esgotado. Abrir a URL do Power Automate, por si só, não confirma que o fluxo terminou.

> **Importante:** ajuste FLOW_BASE_URL para o fluxo correto e configure as ações finais do PAD para gravar o status esperado. O perfil do Chrome, se utilizado, é definido nas ações do próprio fluxo, não nos scripts de consulta do Google Analytics.

## Logs e solução de problemas
- **Log principal:** logs/automacao.log.
- **Planilha gerada:** output/relatorio_site_inyaga.xlsx.
- **Status do PAD:** output/flow_status.json.

Problemas comuns:
- **Erro de autenticação:** confira as credenciais padrão do Google e a permissão de acesso à propriedade GA4.
- **Consulta sem resultados:** verifique o período, as dimensões e as métricas. O projeto evita apagar a aba existente quando a resposta está vazia.
- **Falha ao salvar o Excel:** feche a planilha caso esteja aberta e execute novamente.
- **Espera até o limite de tempo do PAD:** confirme que o fluxo correto foi iniciado e que ele grava flow_status.json no caminho esperado.
- **Dependências:** instale os pacotes usando requirements.txt no mesmo ambiente Python que executará o projeto.

## Possíveis evoluções
- Parametrizar a propriedade GA4, o período de consulta e os caminhos de saída.
- Separar configurações do código usando variáveis de ambiente.
- Adicionar testes automatizados para a consolidação e validação dos dados.
- Agendar a execução e documentar o fluxo completo.
- Construir dashboards a partir da planilha consolidada.

## Status
**Em desenvolvimento.** O projeto contém extração de seis conjuntos de relatórios, consolidação em Excel, registro de logs e integração com Power Automate Desktop. As credenciais e o fluxo PAD precisam ser configurados no ambiente de execução.