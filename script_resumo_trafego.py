from pathlib import Path

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)

import pandas as pd

from planilha_utils import atualizar_planilha, logger

PROPERTY_ID = "505865403"

ARQUIVO_EXCEL = Path(
    "output/relatorio_site_inyaga.xlsx"
)

#Cria o cliente do Google Analytics
client = BetaAnalyticsDataClient()

#Define a consulta
request = RunReportRequest(
    property=f"properties/{PROPERTY_ID}",
    dimensions=[#dimensão do dado, por data
        Dimension(name="date")
    ],
    metrics=[#metricas selecionadas
        Metric(name="activeUsers"),
        Metric(name="newUsers"),
        Metric(name="sessions"),
        Metric(name="screenPageViews"),
        Metric(name="engagementRate"),
        Metric(name="averageSessionDuration"),
        Metric(name="eventCount")
    ],
    date_ranges=[#inicio e fim do espaço amostral, 1 semana
        DateRange(
            start_date="7daysAgo",
            end_date="yesterday"
        )
    ],
)

#Executa a consulta
response = client.run_report(request)

#Lista para armazenar os dados
dados = []

# Percorre cada linha da resposta da requisição a API do Google Analytics
for row in response.rows:
    dados.append({
        'data': row.dimension_values[0].value,
        'usuarios_ativos': row.metric_values[0].value,
        'novos_usuarios': row.metric_values[1].value,
        'sessoes': row.metric_values[2].value,
        'visualizacoes': row.metric_values[3].value,
        'taxa_engajamento': row.metric_values[4].value,
        'tempo_medio_sessao': row.metric_values[5].value,
        'contagem_eventos': row.metric_values[6].value
    })

#Converte a lista em DataFrame
df = pd.DataFrame(dados)

if df.empty:
    logger.error("A consulta do Google Analytics não retornou linhas; atualização cancelada para evitar perda de dados.")
    raise ValueError("Consulta do Google Analytics retornou zero linhas.")


#converte a data para o formato YYYY-MM-DD
df['data'] = pd.to_datetime(df['data']).dt.strftime("%Y-%m-%d")

#converte as métricas para números
df['usuarios_ativos'] = pd.to_numeric(df["usuarios_ativos"])
df['novos_usuarios'] = pd.to_numeric(df['novos_usuarios'])
df["sessoes"] = pd.to_numeric(df["sessoes"])
df["visualizacoes"] = pd.to_numeric(df["visualizacoes"])
df['taxa_engajamento'] = pd.to_numeric(df['taxa_engajamento'])
df['tempo_medio_sessao'] = pd.to_numeric(df['tempo_medio_sessao'])
df['contagem_eventos'] = pd.to_numeric(df['contagem_eventos'])


#Exibe os dados no terminal(Opcional, basta remover o comentário da linha seguinte)
#print(df)

# Valida e consolida os dados, preservando as outras abas do arquivo.
atualizar_planilha(
    arquivo=ARQUIVO_EXCEL,
    dados_novos=df,
    nome_aba="Resumo_Diario",
    chaves=["data"],
)
