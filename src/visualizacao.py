import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates 
import pandas as pd
import plotly.express as px

UF_PARA_NOME = {
    "AC": "Acre",
    "AL": "Alagoas",
    "AP": "Amapa",
    "AM": "Amazonas",
    "BA": "Bahia",
    "CE": "Ceara",
    "DF": "Distrito Federal",
    "ES": "Espirito Santo",
    "GO": "Goias",
    "MA": "Maranhao",
    "MT": "Mato Grosso",
    "MS": "Mato Grosso do Sul",
    "MG": "Minas Gerais",
    "PA": "Para",
    "PB": "Paraiba",
    "PR": "Parana",
    "PE": "Pernambuco",
    "PI": "Piaui",
    "RJ": "Rio de Janeiro",
    "RN": "Rio Grande do Norte",
    "RS": "Rio Grande do Sul",
    "RO": "Rondonia",
    "RR": "Roraima",
    "SC": "Santa Catarina",
    "SP": "Sao Paulo",
    "SE": "Sergipe",
    "TO": "Tocantins",
}

UF_CENTROIDE = {
    "AC": (-9.9754, -67.8249),
    "AL": (-9.6658, -35.7350),
    "AP": (0.0349, -51.0694),
    "AM": (-3.1190, -60.0217),
    "BA": (-12.9777, -38.5016),
    "CE": (-3.7319, -38.5267),
    "DF": (-15.7939, -47.8828),
    "ES": (-20.3155, -40.3128),
    "GO": (-16.6869, -49.2648),
    "MA": (-2.5297, -44.3028),
    "MT": (-15.6010, -56.0974),
    "MS": (-20.4697, -54.6201),
    "MG": (-19.9167, -43.9345),
    "PA": (-1.4558, -48.4902),
    "PB": (-7.1195, -34.8450),
    "PR": (-25.4284, -49.2733),
    "PE": (-8.0476, -34.8770),
    "PI": (-5.0919, -42.8034),
    "RJ": (-22.9068, -43.1729),
    "RN": (-5.7945, -35.2110),
    "RS": (-30.0346, -51.2177),
    "RO": (-8.7608, -63.8999),
    "RR": (2.8235, -60.6753),
    "SC": (-27.5949, -48.5482),
    "SP": (-23.5505, -46.6333),
    "SE": (-10.9472, -37.0731),
    "TO": (-10.1840, -48.3336),
}

def configurar_estilo():
    """Define o estilo padrão para os gráficos da consultoria."""
    sns.set_theme(style="whitegrid")
    plt.rcParams['figure.facecolor'] = 'white'
    plt.rcParams['axes.titlesize'] = 16

def plotar_sazonalidade(df):
    """
    Gera o gráfico de linha para análise de sazonalidade com nomes dos meses no eixo X.
    """
    sazonalidade = df.resample('MS', on='DATA').size().reset_index(name='QTD_RECLAMACOES')

    fig, ax = plt.subplots(figsize=(14, 6))
    
    sns.lineplot(
        data=sazonalidade, 
        x='DATA', 
        y='QTD_RECLAMACOES', 
        marker='o', 
        color='#d63031', 
        linewidth=2.5,
        ax=ax
    )

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b/%Y'))
    
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    
    plt.xticks(rotation=45)

    plt.title('Sazonalidade: Volume de Reclamações Mensais (Hapvida)')
    plt.xlabel('Mês de Referência')
    plt.ylabel('Nº de Reclamações')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout() 
    return plt.show()


def plotar_serie_temporal_media_movel(df, janela=3):
    """
    Gera série temporal mensal com média móvel para evidenciar tendência.
    """
    serie = df.copy()
    serie["DATA"] = pd.to_datetime(serie["DATA"], errors="coerce")
    serie = serie.dropna(subset=["DATA"])

    mensal = (
        serie.resample("MS", on="DATA")
        .size()
        .reset_index(name="QTD_RECLAMACOES")
    )
    mensal["MEDIA_MOVEL"] = mensal["QTD_RECLAMACOES"].rolling(
        window=janela,
        min_periods=1,
    ).mean()

    fig, ax = plt.subplots(figsize=(14, 6))
    sns.lineplot(
        data=mensal,
        x="DATA",
        y="QTD_RECLAMACOES",
        marker="o",
        linewidth=2,
        color="#1f77b4",
        label="Reclamações mensais",
        ax=ax,
    )
    sns.lineplot(
        data=mensal,
        x="DATA",
        y="MEDIA_MOVEL",
        linewidth=2.5,
        color="#d62728",
        label=f"Média móvel ({janela} meses)",
        ax=ax,
    )

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b/%Y"))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    plt.xticks(rotation=45)
    plt.title("Série Temporal de Reclamações com Tendência")
    plt.xlabel("Mês")
    plt.ylabel("Quantidade de reclamações")
    plt.grid(True, alpha=0.25)
    plt.tight_layout()
    return plt.show()

def plotar_ranking_cidades(df, top_n=10):
    """Gera um gráfico de barras das cidades com mais reclamações."""
    top_cidades = df[['UF', 'CIDADE']].value_counts().head(top_n).reset_index(name='TOTAL')
    
    plt.figure(figsize=(12, 6))
    sns.barplot(data=top_cidades, x='TOTAL', y='CIDADE', hue='UF', palette='magma')
    plt.title(f'Top {top_n} Cidades com Mais Reclamações')
    return plt.show()


def plotar_mapa_geografico_por_ano(df):
    """
    Cria heatmap geográfico por UF com seletor de ano (slider via animação).
    """
    mapa = df.copy()
    mapa["DATA"] = pd.to_datetime(mapa["DATA"], errors="coerce")
    mapa = mapa.dropna(subset=["DATA", "UF"])
    mapa["ANO"] = mapa["DATA"].dt.year
    mapa["UF"] = mapa["UF"].astype(str).str.upper().str.strip()
    mapa = mapa[mapa["UF"].isin(UF_PARA_NOME.keys())]

    uf_ano = (
        mapa.groupby(["ANO", "UF"], as_index=False)
        .size()
        .rename(columns={"size": "QTD_RECLAMACOES"})
    )
    uf_ano["ESTADO"] = uf_ano["UF"].map(UF_PARA_NOME)

    uf_ano["LAT"] = uf_ano["UF"].map(lambda uf: UF_CENTROIDE[uf][0])
    uf_ano["LON"] = uf_ano["UF"].map(lambda uf: UF_CENTROIDE[uf][1])

    fig = px.scatter_geo(
        uf_ano,
        lat="LAT",
        lon="LON",
        color="QTD_RECLAMACOES",
        size="QTD_RECLAMACOES",
        size_max=40,
        animation_frame="ANO",
        hover_name="ESTADO",
        hover_data={"UF": True, "QTD_RECLAMACOES": True},
        color_continuous_scale="Reds",
        scope="south america",
        title="Heatmap de Reclamações por Estado com Seletor de Ano",
    )

    fig.update_geos(
        lataxis_range=[-35, 6],
        lonaxis_range=[-75, -30],
        visible=False,
        showcountries=True,
        showcoastlines=True,
        countrycolor="black",
        projection_type="mercator",
    )
    fig.update_layout(coloraxis_colorbar_title="Reclamações")
    return fig


def plotar_distribuicao_tamanho_texto_status(df, tipo="boxplot", bins=25):
    """
    Mostra distribuição do tamanho da descrição por STATUS.
    tipo: "boxplot" ou "histograma".
    """
    dist = df.copy()
    dist["STATUS"] = dist["STATUS"].astype(str)
    dist["DESCRICAO"] = dist["DESCRICAO"].astype(str)
    dist["TAMANHO_TEXTO"] = dist["DESCRICAO"].str.len()
    dist = dist.dropna(subset=["STATUS", "TAMANHO_TEXTO"])

    if tipo == "histograma":
        fig = px.histogram(
            dist,
            x="TAMANHO_TEXTO",
            color="STATUS",
            nbins=bins,
            barmode="overlay",
            opacity=0.65,
            title="Histograma do Tamanho da Descrição por STATUS",
            labels={"TAMANHO_TEXTO": "Tamanho da descrição (caracteres)"},
        )
        return fig

    fig = px.box(
        dist,
        x="STATUS",
        y="TAMANHO_TEXTO",
        color="STATUS",
        points="outliers",
        title="Boxplot do Tamanho da Descrição por STATUS",
        labels={
            "STATUS": "Status",
            "TAMANHO_TEXTO": "Tamanho da descrição (caracteres)",
        },
    )
    return fig

