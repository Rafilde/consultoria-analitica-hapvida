import pandas as pd

def carregar_dados_brutos():
    caminho = "../data/RECLAMEAQUI_HAPVIDA.csv"
    return pd.read_csv(caminho)

def salvar_dados_limpos(df):
    caminho = "../data/RECLAMEAQUI_HAPVIDA_LIMPO.csv"
    df.to_csv(caminho, index=False)