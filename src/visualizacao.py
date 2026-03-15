import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates 

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

def plotar_ranking_cidades(df, top_n=10):
    """Gera um gráfico de barras das cidades com mais reclamações."""
    top_cidades = df[['UF', 'CIDADE']].value_counts().head(top_n).reset_index(name='TOTAL')
    
    plt.figure(figsize=(12, 6))
    sns.barplot(data=top_cidades, x='TOTAL', y='CIDADE', hue='UF', palette='magma')
    plt.title(f'Top {top_n} Cidades com Mais Reclamações')
    return plt.show()