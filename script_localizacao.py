from pathlib import Path

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)

import pandas as pd

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
        Dimension(name="country"),
        Dimension(name="region"),
        Dimension(name="city")
    ],
    metrics=[#metricas selecionadas
        Metric(name="activeUsers"),
        Metric(name="newUsers"),
        Metric(name="sessions"),
        Metric(name="screenPageViews"),
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
        'pais': row.dimension_values[1].value,
        'estado': row.dimension_values[2].value,
        'cidade': row.dimension_values[3].value,
        'usuarios_ativos': row.metric_values[0].value,
        'novos_usuarios': row.metric_values[1].value,
        'sessoes': row.metric_values[2].value,
        'visualizacoes': row.metric_values[3].value,
    })

#Converte a lista em DataFrame
df = pd.DataFrame(dados)


#converte a data para o formato YYYY-MM-DD
df['data'] = pd.to_datetime(df['data']).dt.strftime("%Y-%m-%d")

#converte as métricas para números
df['usuarios_ativos'] = pd.to_numeric(df["usuarios_ativos"])
df['novos_usuarios'] = pd.to_numeric(df["novos_usuarios"])
df["sessoes"] = pd.to_numeric(df["sessoes"])
df["visualizacoes"] = pd.to_numeric(df["visualizacoes"])


#Exibe os dados no terminal(Opcional, basta remover o comentário da linha seguinte)
#print(df)

#puxa os dados antigos da planilha
if ARQUIVO_EXCEL.exists():

    df_antigo = pd.read_excel(ARQUIVO_EXCEL, sheet_name="Localização")

else:
    df_antigo = pd.DataFrame()


#concatena dados antigos + dados novos
df_final = pd.concat([df_antigo, df], ignore_index=True)

#remove duplicatas
df_final = df_final.drop_duplicates(subset=["data", "pais", "estado", "cidade"], keep="last")

#ordena os dados por data
df_final = df_final.sort_values(by="data")

#Salva no Excel
with pd.ExcelWriter(
    ARQUIVO_EXCEL,
      engine="openpyxl",
      mode="a" if ARQUIVO_EXCEL.exists() else 'w',
      if_sheet_exists="replace") as writer:

    df_final.to_excel(writer, sheet_name="Localização", index=False)
