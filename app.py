"""
Dashboard Streamlit — Consultoria Analítica Hapvida
Análise de reclamações do ReclameAqui
"""

import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import pandas as pd
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, os.path.dirname(__file__))
from src.visualizacao import (
    plotar_mapa_geografico_por_ano,
    plotar_distribuicao_tamanho_texto_status,
)

# ── Configuração da página ────────────────────────────────────────────────────
st.set_page_config(
    page_title="Hapvida · ReclameAqui",
    page_icon="🏥",
    layout="wide",
)

# ── Carregamento de dados ─────────────────────────────────────────────────────
DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "RECLAMEAQUI_HAPVIDA_LIMPO.csv")


@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce")
    df["DESCRICAO"] = df["DESCRICAO"].astype(str)
    df["TAMANHO_RELATO"] = df["DESCRICAO"].str.len()
    return df


df_full = load_data()

# ── Sidebar — Filtros globais ─────────────────────────────────────────────────
st.sidebar.image(
    "https://upload.wikimedia.org/wikipedia/commons/thumb/6/64/Hapvida_logo.svg/320px-Hapvida_logo.svg.png",
    width='stretch',
)
st.sidebar.title("Filtros")

anos_disponiveis = sorted(df_full["DATA"].dt.year.dropna().unique().astype(int))
anos_selecionados = st.sidebar.multiselect(
    "Ano(s)",
    options=anos_disponiveis,
    default=anos_disponiveis,
)

ufs_disponiveis = sorted(df_full["UF"].dropna().unique())
ufs_selecionadas = st.sidebar.multiselect(
    "Estado(s) — UF",
    options=ufs_disponiveis,
    default=ufs_disponiveis,
)

status_disponiveis = sorted(df_full["STATUS"].dropna().unique())
status_selecionados = st.sidebar.multiselect(
    "Status da Reclamação",
    options=status_disponiveis,
    default=status_disponiveis,
)

tam_min_abs = int(df_full["TAMANHO_RELATO"].min())
tam_max_abs = int(df_full["TAMANHO_RELATO"].max())
faixa_tamanho = st.sidebar.slider(
    "Faixa de Tamanho do Relato (caracteres)",
    min_value=tam_min_abs,
    max_value=tam_max_abs,
    value=(tam_min_abs, tam_max_abs),
    step=50,
    help="Filtra reclamações pelo tamanho (em caracteres) da descrição.",
)

# ── Aplicar filtros ───────────────────────────────────────────────────────────
df = df_full.copy()

if anos_selecionados:
    df = df[df["DATA"].dt.year.isin(anos_selecionados)]
if ufs_selecionadas:
    df = df[df["UF"].isin(ufs_selecionadas)]
if status_selecionados:
    df = df[df["STATUS"].isin(status_selecionados)]
df = df[df["TAMANHO_RELATO"].between(faixa_tamanho[0], faixa_tamanho[1])]

if df.empty:
    st.warning("Nenhum registro encontrado com os filtros selecionados.")
    st.stop()

# ── Cabeçalho ─────────────────────────────────────────────────────────────────
st.title("🏥 Hapvida · Análise de Reclamações ReclameAqui")
st.caption(f"Base filtrada: **{len(df):,}** registros de {len(df_full):,} totais")

# ── KPIs principais ───────────────────────────────────────────────────────────
st.subheader("📌 Indicadores Gerais")

total = len(df)
resolvidas = (df["STATUS"] == "Resolvida").sum()
nao_respondidas = (df["STATUS"] == "Não respondida").sum()
taxa_resolucao = resolvidas / total * 100 if total else 0
taxa_omissao = nao_respondidas / total * 100 if total else 0
media_chars = df["TAMANHO_RELATO"].mean()

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total de Reclamações", f"{total:,}")
col2.metric("Resolvidas", f"{resolvidas:,}", f"{taxa_resolucao:.1f}%")
col3.metric("Não Respondidas", f"{nao_respondidas:,}", f"-{taxa_omissao:.1f}%", delta_color="inverse")
col4.metric("Taxa de Resolução", f"{taxa_resolucao:.1f}%")
col5.metric("Média de Caracteres/Relato", f"{media_chars:.0f}")

st.divider()

# ── Abas ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📅 Temporal",
    "🗺️ Geográfico",
    "🔧 Serviços",
    "📊 Status & Textos",
    "🚨 Omissão",
    "☁️ WordCloud NLP",
])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — TEMPORAL
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.subheader("Sazonalidade: Volume de Reclamações Mensais")

    mensal = (
        df.resample("MS", on="DATA")
        .size()
        .reset_index(name="QTD_RECLAMACOES")
    )

    janela = st.slider("Janela da Média Móvel (meses)", min_value=2, max_value=6, value=3)
    mensal["MEDIA_MOVEL"] = (
        mensal["QTD_RECLAMACOES"].rolling(window=janela, min_periods=1).mean()
    )

    fig_ts = px.line(
        mensal,
        x="DATA",
        y=["QTD_RECLAMACOES", "MEDIA_MOVEL"],
        markers=True,
        labels={"DATA": "Mês", "value": "Reclamações", "variable": "Série"},
        color_discrete_map={
            "QTD_RECLAMACOES": "#1f77b4",
            "MEDIA_MOVEL": "#d62728",
        },
        title="Série Temporal com Média Móvel",
    )
    fig_ts.update_layout(legend_title_text="Série", hovermode="x unified")
    st.plotly_chart(fig_ts, width='stretch')

    st.markdown("---")
    st.subheader("Distribuição de Reclamações por Dia da Semana")

    df_dow = df.copy()
    try:
        df_dow["DIA_SEMANA"] = df_dow["DATA"].dt.day_name(locale="pt_BR.UTF-8")
    except Exception:
        df_dow["DIA_SEMANA"] = df_dow["DATA"].dt.dayofweek.map({
            0: "Segunda", 1: "Terça", 2: "Quarta", 3: "Quinta",
            4: "Sexta", 5: "Sábado", 6: "Domingo",
        })
    ordem_dias = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
    dow_counts = df_dow["DIA_SEMANA"].value_counts().reindex(ordem_dias, fill_value=0).reset_index()
    dow_counts.columns = ["DIA_SEMANA", "TOTAL"]

    fig_dow = px.bar(
        dow_counts,
        x="DIA_SEMANA",
        y="TOTAL",
        color="TOTAL",
        color_continuous_scale="Reds",
        title="Volume de Reclamações por Dia da Semana",
        labels={"DIA_SEMANA": "Dia", "TOTAL": "Reclamações"},
    )
    fig_dow.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig_dow, width='stretch')


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — GEOGRÁFICO
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    col_mapa, col_ranking = st.columns([3, 2])

    with col_mapa:
        st.subheader("Heatmap Geográfico por Estado e Ano")
        if len(anos_selecionados) > 0:
            fig_mapa = plotar_mapa_geografico_por_ano(df)
            st.plotly_chart(fig_mapa, width='stretch')
        else:
            st.info("Selecione ao menos um ano para exibir o mapa.")

    with col_ranking:
        st.subheader("Top 10 Cidades")
        top_n = st.slider("Quantas cidades?", 5, 20, 10, key="top_cidades")
        top_cidades = (
            df[["UF", "CIDADE"]].value_counts().head(top_n).reset_index(name="TOTAL")
        )
        fig_cidades = px.bar(
            top_cidades,
            x="TOTAL",
            y="CIDADE",
            color="UF",
            orientation="h",
            title=f"Top {top_n} Cidades com Mais Reclamações",
            labels={"TOTAL": "Reclamações", "CIDADE": "Cidade"},
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig_cidades.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig_cidades, width='stretch')

    st.markdown("---")
    st.subheader("Distribuição Espacial — Gráfico de Pareto por Estado")
    pareto_uf = df["UF"].value_counts().reset_index()
    pareto_uf.columns = ["UF", "QTD"]
    pareto_uf = pareto_uf.sort_values("QTD", ascending=False).reset_index(drop=True)
    pareto_uf["ACUMULADO_%"] = pareto_uf["QTD"].cumsum() / pareto_uf["QTD"].sum() * 100

    fig_pareto = go.Figure()
    fig_pareto.add_trace(go.Bar(
        x=pareto_uf["UF"],
        y=pareto_uf["QTD"],
        name="Reclamações",
        marker_color="#d62728",
        yaxis="y1",
    ))
    fig_pareto.add_trace(go.Scatter(
        x=pareto_uf["UF"],
        y=pareto_uf["ACUMULADO_%"],
        name="% Acumulado",
        mode="lines+markers",
        marker_color="#1f77b4",
        yaxis="y2",
    ))
    fig_pareto.update_layout(
        title="Pareto de Reclamações por Estado (UF)",
        xaxis_title="Estado",
        yaxis=dict(title="Quantidade de Reclamações"),
        yaxis2=dict(title="% Acumulado", overlaying="y", side="right", range=[0, 101], ticksuffix="%"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
    )
    fig_pareto.add_hline(y=80, line_dash="dash", line_color="gray",
                         annotation_text="80%", annotation_position="bottom right", yref="y2")
    st.plotly_chart(fig_pareto, width='stretch')

    st.markdown("---")
    st.subheader("Eficiência de Atendimento por UF (Top 10 com Mais Pendências)")

    cruzamento_uf = pd.crosstab(df["UF"], df["STATUS"], normalize="index") * 100
    if "Não respondida" in cruzamento_uf.columns:
        cruzamento_uf = cruzamento_uf.sort_values("Não respondida", ascending=False).head(10)
    else:
        cruzamento_uf = cruzamento_uf.head(10)

    cruzamento_uf_reset = cruzamento_uf.reset_index().melt(id_vars="UF", var_name="Status", value_name="Percentual")
    fig_uf = px.bar(
        cruzamento_uf_reset,
        x="UF",
        y="Percentual",
        color="Status",
        barmode="stack",
        title="Distribuição de Status por UF (%)",
        labels={"Percentual": "% Reclamações", "UF": "Estado"},
        color_discrete_map={
            "Resolvida": "#2ecc71",
            "Não respondida": "#e74c3c",
            "Em análise": "#f39c12",
            "Respondida": "#3498db",
        },
    )
    st.plotly_chart(fig_uf, width='stretch')


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — SERVIÇOS
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    col_freq, col_heat = st.columns(2)

    with col_freq:
        st.subheader("Frequência por Tipo de Serviço")
        freq_servico = df["TIPO_SERVICO"].value_counts().reset_index(name="TOTAL")
        freq_servico.columns = ["TIPO_SERVICO", "TOTAL"]
        fig_freq = px.bar(
            freq_servico,
            x="TOTAL",
            y="TIPO_SERVICO",
            orientation="h",
            color="TOTAL",
            color_continuous_scale="Reds",
            title="Volume de Reclamações por Tipo de Serviço",
            labels={"TOTAL": "Reclamações", "TIPO_SERVICO": "Serviço"},
        )
        fig_freq.update_layout(
            yaxis={"categoryorder": "total ascending"},
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig_freq, width='stretch')

    with col_heat:
        st.subheader("Mapa de Calor: Eficiência por Serviço")
        cruzamento_servico = pd.crosstab(df["TIPO_SERVICO"], df["STATUS"], normalize="index") * 100

        fig_heat, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(
            cruzamento_servico,
            annot=True,
            cmap="YlOrBr",
            fmt=".1f",
            ax=ax,
            linewidths=0.5,
        )
        ax.set_title("Eficiência de Resolução por Tipo de Serviço (%)", fontsize=13)
        ax.set_xlabel("Status da Reclamação")
        ax.set_ylabel("Tipo de Serviço")
        plt.tight_layout()
        st.pyplot(fig_heat)
        plt.close(fig_heat)

    st.markdown("---")
    st.subheader("Frequência por Tipo de Origem")
    freq_origem = df["TIPO_ORIGEM"].value_counts().reset_index(name="TOTAL")
    freq_origem.columns = ["TIPO_ORIGEM", "TOTAL"]
    fig_origem = px.pie(
        freq_origem,
        names="TIPO_ORIGEM",
        values="TOTAL",
        title="Distribuição por Origem das Reclamações",
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )
    st.plotly_chart(fig_origem, width='stretch')


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — STATUS & TEXTOS
# ═══════════════════════════════════════════════════════════════════════════════
with tab4:
    col_status, col_texto = st.columns(2)

    with col_status:
        st.subheader("Frequência por Status")
        freq_status = df["STATUS"].value_counts().reset_index(name="TOTAL")
        freq_status.columns = ["STATUS", "TOTAL"]
        fig_status = px.pie(
            freq_status,
            names="STATUS",
            values="TOTAL",
            hole=0.4,
            title="Distribuição de Status",
            color_discrete_map={
                "Resolvida": "#2ecc71",
                "Não respondida": "#e74c3c",
                "Em análise": "#f39c12",
                "Respondida": "#3498db",
            },
        )
        st.plotly_chart(fig_status, width='stretch')

    with col_texto:
        st.subheader("Tamanho dos Relatos por Status")
        tipo_dist = st.radio(
            "Tipo de visualização",
            ["Boxplot", "Histograma"],
            horizontal=True,
            key="tipo_dist",
        )
        tipo_param = "boxplot" if tipo_dist == "Boxplot" else "histograma"
        fig_dist = plotar_distribuicao_tamanho_texto_status(df, tipo=tipo_param, bins=25)
        st.plotly_chart(fig_dist, width='stretch')

    st.markdown("---")
    st.subheader("Estatísticas Descritivas dos Relatos")
    st.dataframe(
        df["TAMANHO_RELATO"].describe().rename("Tamanho (caracteres)").round(1),
        width='stretch',
    )

    st.subheader("Top 5 Problemas Mais Relatados")
    top_problemas = df["PROBLEMA"].value_counts().head(5).reset_index(name="TOTAL")
    top_problemas.columns = ["PROBLEMA", "TOTAL"]
    st.dataframe(top_problemas, width='stretch', hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5 — OMISSÃO
# ═══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.subheader("Evolução da Taxa de Omissão / Negligência")
    st.markdown(
        "**Métrica:** `(Reclamações 'Não respondida' / Total de Reclamações) × 100`  \n"
        "Indica o percentual de clientes 'abandonados' no período."
    )

    anos_omissao = sorted(df["DATA"].dt.year.dropna().unique().astype(int))
    if not anos_omissao:
        st.warning("Sem dados para o período selecionado.")
    else:
        ano_omissao = st.selectbox("Selecionar Ano", options=anos_omissao, index=0)
        df_ano = df[df["DATA"].dt.year == ano_omissao].copy()

        if df_ano.empty:
            st.warning(f"Sem dados para {ano_omissao}.")
        else:
            df_ano["MES"] = df_ano["DATA"].dt.to_period("M")
            total_mes = df_ano.groupby("MES").size().rename("Total")
            nao_resp_mes = (
                df_ano[df_ano["STATUS"] == "Não respondida"]
                .groupby("MES")
                .size()
                .rename("Nao_Respondida")
            )
            df_taxa = pd.concat([total_mes, nao_resp_mes], axis=1).fillna(0)
            df_taxa["Taxa_Omissao"] = (df_taxa["Nao_Respondida"] / df_taxa["Total"]) * 100
            df_taxa.index = df_taxa.index.astype(str)
            df_taxa = df_taxa.reset_index().rename(columns={"MES": "Mês"})

            fig_omissao = px.area(
                df_taxa,
                x="Mês",
                y="Taxa_Omissao",
                title=f"Taxa de Omissão Mensal — {ano_omissao}",
                labels={"Taxa_Omissao": "Taxa de Omissão (%)", "Mês": "Mês"},
                color_discrete_sequence=["#e74c3c"],
            )
            fig_omissao.update_traces(line_width=2)
            fig_omissao.add_hline(
                y=df_taxa["Taxa_Omissao"].mean(),
                line_dash="dash",
                line_color="darkred",
                annotation_text=f"Média: {df_taxa['Taxa_Omissao'].mean():.1f}%",
                annotation_position="top right",
            )
            fig_omissao.update_layout(yaxis_range=[0, 100])
            st.plotly_chart(fig_omissao, width='stretch')

            col_a, col_b = st.columns(2)
            with col_a:
                st.metric(
                    "Pico de Omissão",
                    f"{df_taxa['Taxa_Omissao'].max():.1f}%",
                    f"Mês: {df_taxa.loc[df_taxa['Taxa_Omissao'].idxmax(), 'Mês']}",
                )
            with col_b:
                st.metric(
                    "Média Anual de Omissão",
                    f"{df_taxa['Taxa_Omissao'].mean():.1f}%",
                )

            st.dataframe(
                df_taxa[["Mês", "Total", "Nao_Respondida", "Taxa_Omissao"]]
                .rename(columns={
                    "Total": "Total Reclamações",
                    "Nao_Respondida": "Não Respondidas",
                    "Taxa_Omissao": "Taxa Omissão (%)",
                })
                .style.format({"Taxa Omissão (%)": "{:.1f}"}),
                width='stretch',
                hide_index=True,
            )

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 6 — WORDCLOUD NLP
# ═══════════════════════════════════════════════════════════════════════════════
with tab6:
    st.subheader("☁️ Mineração de Texto — Palavras Mais Frequentes nas Reclamações")
    st.markdown(
        "Stopwords removidas via **spaCy** (`pt_core_news_sm`). "
        "Apenas termos substantivos/relevantes são exibidos."
    )

    col_wc1, col_wc2 = st.columns([1, 2])

    with col_wc1:
        status_wc = st.selectbox(
            "Filtrar por Status",
            options=["Todos"] + sorted(df["STATUS"].dropna().unique().tolist()),
            key="wc_status",
        )
        max_words_wc = st.slider("Máx. de palavras", 30, 200, 80, key="wc_maxwords")

    # ── Geração da nuvem ──────────────────────────────────────────────────────
    @st.cache_data(show_spinner="Processando textos com spaCy…")
    def gerar_wordcloud(textos: list[str], max_words: int):
        import spacy
        from wordcloud import WordCloud

        try:
            nlp_wc = spacy.load("pt_core_news_sm", disable=["parser", "ner"])
        except OSError:
            return None, "spacy_missing"

        corpus = " ".join(t for t in textos if isinstance(t, str))
        # Processa em lotes para eficiência
        palavras = []
        for doc in nlp_wc.pipe(
            [corpus[i : i + 100_000] for i in range(0, len(corpus), 100_000)],
            batch_size=1,
        ):
            for token in doc:
                if (
                    not token.is_stop
                    and not token.is_punct
                    and not token.is_space
                    and not token.like_num
                    and len(token.text) > 2
                ):
                    palavras.append(token.lemma_.lower())

        texto_filtrado = " ".join(palavras)
        if not texto_filtrado.strip():
            return None, None

        wc = WordCloud(
            width=900,
            height=500,
            background_color="white",
            colormap="Reds",
            max_words=max_words,
            collocations=False,
            prefer_horizontal=0.85,
        ).generate(texto_filtrado)
        return wc, None

    df_wc = df if status_wc == "Todos" else df[df["STATUS"] == status_wc]

    if df_wc.empty:
        st.warning("Sem dados para gerar a nuvem com os filtros selecionados.")
    elif len(df_wc) > 5000:
        amostra = df_wc["DESCRICAO"].dropna().sample(5000, random_state=42).tolist()
        st.info("Amostra de 5.000 registros usada para performance.")
    else:
        amostra = df_wc["DESCRICAO"].dropna().tolist()

    if not df_wc.empty:
        wc_obj, erro_wc = gerar_wordcloud(amostra, max_words_wc)
        if erro_wc == "spacy_missing":
            st.error("Modelo spaCy não encontrado. Execute: `python -m spacy download pt_core_news_sm`")
        elif wc_obj:
            with col_wc2:
                fig_wc, ax_wc = plt.subplots(figsize=(10, 5))
                ax_wc.imshow(wc_obj, interpolation="bilinear")
                ax_wc.axis("off")
                titulo_wc = f"Status: {status_wc}" if status_wc != "Todos" else "Todos os status"
                ax_wc.set_title(f"WordCloud — {titulo_wc}", fontsize=14, pad=10)
                plt.tight_layout()
                st.pyplot(fig_wc)
                plt.close(fig_wc)

    st.markdown("---")
    st.subheader("Frequência das Principais Palavras (Top 30)")

    @st.cache_data(show_spinner="Contando frequências…")
    def top_palavras(textos: list[str], n: int = 30):
        import spacy
        from collections import Counter

        try:
            nlp_top = spacy.load("pt_core_news_sm", disable=["parser", "ner"])
        except OSError:
            return pd.DataFrame(columns=["Palavra", "Frequência"])

        corpus = " ".join(t for t in textos if isinstance(t, str))
        palavras = []
        for doc in nlp_top.pipe(
            [corpus[i : i + 100_000] for i in range(0, len(corpus), 100_000)],
            batch_size=1,
        ):
            for token in doc:
                if (
                    not token.is_stop
                    and not token.is_punct
                    and not token.is_space
                    and not token.like_num
                    and len(token.text) > 2
                ):
                    palavras.append(token.lemma_.lower())

        contagem = Counter(palavras).most_common(n)
        return pd.DataFrame(contagem, columns=["Palavra", "Frequência"])

    if not df_wc.empty:
        df_freq = top_palavras(amostra)
        if not df_freq.empty:
            fig_freq_wc = px.bar(
                df_freq,
                x="Frequência",
                y="Palavra",
                orientation="h",
                color="Frequência",
                color_continuous_scale="Reds",
                title=f"Top 30 Termos Mais Frequentes — {status_wc}",
            )
            fig_freq_wc.update_layout(
                yaxis={"categoryorder": "total ascending"},
                coloraxis_showscale=False,
                height=600,
            )
            st.plotly_chart(fig_freq_wc, width='stretch')


# ── Rodapé ────────────────────────────────────────────────────────────────────
st.divider()
st.caption("Dashboard de Consultoria Analítica · Hapvida · ReclameAqui")
