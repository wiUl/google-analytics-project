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

request = RunReportRequest(
    property=f"properties/{PROPERTY_ID}",
    dimensions=[#dimensão do dado, por data, por localizacao
        Dimension(name="date"),
        Dimension(name="eventName"),
    ],
    metrics=[#metricas selecionadas
        Metric(name="eventCount"),
        Metric(name="totalUsers")
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
        'evento': row.dimension_values[1].value,
        'ocorrencias': row.metric_values[0].value,
        'usuarios': row.metric_values[1].value,
    })

#Converte a lista em DataFrame
df = pd.DataFrame(dados)

if df.empty:
    logger.error("A consulta do Google Analytics não retornou linhas; atualização cancelada para evitar perda de dados.")
    raise ValueError("Consulta do Google Analytics retornou zero linhas.")


#converte a data para o formato YYYY-MM-DD
df['data'] = pd.to_datetime(df['data']).dt.strftime("%Y-%m-%d")

#converte as métricas para números
df['ocorrencias'] = pd.to_numeric(df["ocorrencias"])
df['usuarios'] = pd.to_numeric(df["usuarios"])



#Exibe os dados no terminal(Opcional, basta remover o comentário da linha seguinte)
#print(df)

# Valida e consolida os dados, preservando as outras abas do arquivo.
atualizar_planilha(
    arquivo=ARQUIVO_EXCEL,
    dados_novos=df,
    nome_aba="Eventos",
    chaves=["data", "evento"],
)
