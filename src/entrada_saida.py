import pandas as pd

def carregar_dados_brutos(path="../data/RECLAMEAQUI_HAPVIDA.csv"):
    return pd.read_csv(path)

def salvar_dados_limpos(df, path="../data/RECLAMEAQUI_HAPVIDA_LIMPO.csv"):
    df.to_csv(path, index=False)