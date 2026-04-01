import sys
import os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from entrada_saida import carregar_dados_brutos
from limpeza import executar_limpeza

st.set_page_config(
    page_title="Hapvida",
    page_icon="🏥",
    layout="wide",
)


@st.cache_data
def carregar_dados():
    """
    Tenta carregar o CSV já limpo.
    Se der ruim, carrega o bruto e executa a limpeza.
    """
    base = os.path.join(os.path.dirname(__file__), "..", "data")
    caminho_limpo = os.path.join(base, "RECLAMEAQUI_HAPVIDA_LIMPO.csv")
    caminho_bruto = os.path.join(base, "RECLAMEAQUI_HAPVIDA.csv")

    if os.path.exists(caminho_limpo):
        df = pd.read_csv(caminho_limpo, low_memory=False)
    else:
        df = executar_limpeza(carregar_dados_brutos(caminho_bruto))

    # Garante colunas essenciais para os filtros
    df["UF"]            = df["UF"].fillna("NÃO INFORMADO").astype(str).str.strip().str.upper()
    df["STATUS"]        = df["STATUS"].fillna("NÃO INFORMADO").astype(str).str.strip()
    df["DESCRICAO"]     = df["DESCRICAO"].fillna("").astype(str)
    df["TAMANHO_TEXTO"] = df["DESCRICAO"].str.len()
    df["DATA"]          = pd.to_datetime(df.get("DATA"), errors="coerce")

    return df


df_original = carregar_dados()


st.sidebar.title("Filtros Globais")
st.sidebar.markdown("---")

ufs_disponiveis = sorted(
    [uf for uf in df_original["UF"].unique() if uf != "NÃO INFORMADO"]
)

ufs_selecionadas = st.sidebar.multiselect(
    label="Estado (UF)",
    options=ufs_disponiveis,
    default=ufs_disponiveis,      
    placeholder="Selecione os estados...",
)

status_disponiveis = sorted(df_original["STATUS"].unique().tolist())

status_selecionados = st.sidebar.multiselect(
    label="Status da Reclamação",
    options=status_disponiveis,
    default=status_disponiveis,    
    placeholder="Selecione os status...",
)

tamanho_min = int(df_original["TAMANHO_TEXTO"].min())
tamanho_max = int(df_original["TAMANHO_TEXTO"].max())

faixa_tamanho = st.sidebar.slider(
    label="Faixa de Tamanho do Texto (caracteres)",
    min_value=tamanho_min,
    max_value=tamanho_max,
    value=(tamanho_min, tamanho_max),  
    step=50,
)

st.sidebar.markdown("---")
st.sidebar.caption("Consultoria Analítica Hapvida · 2025")


df_filtrado = df_original[
    df_original["UF"].isin(ufs_selecionadas)
    & df_original["STATUS"].isin(status_selecionados)
    & df_original["TAMANHO_TEXTO"].between(faixa_tamanho[0], faixa_tamanho[1])
]


st.title("Dashboard de Reclamações")
st.markdown("---")

col1, col2, col3 = st.columns(3)
col1.metric("Total de reclamações", f"{len(df_filtrado):,}".replace(",", "."))
col2.metric("Estados selecionados", len(ufs_selecionadas))
col3.metric("Status selecionados",  len(status_selecionados))

st.markdown("---")


# [1] Série Temporal com Tendência (Média Móvel)
st.subheader("Série Temporal de Reclamações com Tendência")

janela_mm = st.sidebar.slider(
    label="Janela da Média Móvel (meses)",
    min_value=2,
    max_value=12,
    value=3,
    step=1,
)

if df_filtrado.empty:
    st.warning("Nenhum dado encontrado para os filtros selecionados.")
else:
    mensal = (
        df_filtrado.dropna(subset=["DATA"])
        .resample("MS", on="DATA")
        .size()
        .reset_index(name="QTD_RECLAMACOES")
    )
    mensal["MEDIA_MOVEL"] = (
        mensal["QTD_RECLAMACOES"]
        .rolling(window=janela_mm, min_periods=1)
        .mean()
        .round(1)
    )
    # O plotly é interativo no Streamlit
    fig_serie = go.Figure()

    fig_serie.add_trace(go.Scatter(
        x=mensal["DATA"],
        y=mensal["QTD_RECLAMACOES"],
        mode="lines+markers",
        name="Reclamações mensais",
        line=dict(color="#1f77b4", width=2),
        marker=dict(size=5),
    ))

    fig_serie.add_trace(go.Scatter(
        x=mensal["DATA"],
        y=mensal["MEDIA_MOVEL"],
        mode="lines",
        name=f"Média móvel ({janela_mm} meses)",
        line=dict(color="#d62728", width=2.5, dash="dash"),
    ))

    fig_serie.update_layout(
        xaxis_title="Mês",
        yaxis_title="Quantidade de reclamações",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
        height=420,
        margin=dict(t=20),
    )

    st.plotly_chart(fig_serie, use_container_width=True)

st.markdown("---")

# [2] Análise Geográfica Avançada (Mapa Coroplético)
# TODO: adicionar aqui

# [3] Distribuição Espacial – Gráfico de Pareto por Estado
st.subheader("📊 Distribuição de Reclamações por Estado (Pareto)")

if df_filtrado.empty:
    st.warning("Nenhum dado encontrado para os filtros selecionados.")
else:
    pareto = (
        df_filtrado.groupby("UF", as_index=False)
        .size()
        .rename(columns={"size": "QTD"})
        .sort_values("QTD", ascending=False)
    )

    pareto["ACUMULADO_%"] = (pareto["QTD"].cumsum() / pareto["QTD"].sum() * 100).round(1)

    fig_pareto = go.Figure()

    # Barras de frequência por estado
    fig_pareto.add_trace(go.Bar(
        x=pareto["UF"],
        y=pareto["QTD"],
        name="Reclamações",
        marker_color="#d62728",
        yaxis="y1",
    ))

    # Linha acumulada (%)
    fig_pareto.add_trace(go.Scatter(
        x=pareto["UF"],
        y=pareto["ACUMULADO_%"],
        name="% Acumulado",
        mode="lines+markers",
        marker=dict(size=5),
        line=dict(color="#1f77b4", width=2),
        yaxis="y2",
    ))

    # Linha de referência 80%
    fig_pareto.add_hline(
        y=80,
        line_dash="dash",
        line_color="gray",
        annotation_text="80%",
        annotation_position="top right",
        yref="y2",
    )

    fig_pareto.update_layout(
        xaxis_title="Estado (UF)",
        yaxis=dict(title="Quantidade de reclamações"),
        yaxis2=dict(
            title="% Acumulado",
            overlaying="y",
            side="right",
            range=[0, 105],
            showgrid=False,
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
        height=450,
        margin=dict(t=20),
    )

    st.plotly_chart(fig_pareto, use_container_width=True)

st.markdown("---")

# [4] Proporção de Resoluções por STATUS
# TODO: adicionar aqui

# [5] Análise Estatística de Textos (Boxplot / Histograma)
# TODO: adicionar aqui

# [6] Mineração de Texto – WordCloud com NLP
# TODO: adicionar aqui