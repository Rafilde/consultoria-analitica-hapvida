import sys
import os
import streamlit as st
import pandas as pd

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
# TODO: adicionar aqui

# [2] Análise Geográfica Avançada (Mapa Coroplético)
# TODO: adicionar aqui

# [3] Distribuição Espacial – Gráfico de Pareto por Estado
# TODO: adicionar aqui

# [4] Proporção de Resoluções por STATUS
# TODO: adicionar aqui

# [5] Análise Estatística de Textos (Boxplot / Histograma)
# TODO: adicionar aqui

# [6] Mineração de Texto – WordCloud com NLP
# TODO: adicionar aqui