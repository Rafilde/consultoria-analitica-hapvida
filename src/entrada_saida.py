import pandas as pd

def carregar_dados_brutos():
    caminho = "../data/RECLAMEAQUI_HAPVIDA.csv"
    return pd.read_csv(caminho)