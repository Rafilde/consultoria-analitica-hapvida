import pandas as pd 
import nltk
from nltk.corpus import stopwords
import re

nltk.download('stopwords')

def _limpar_localidade(df):
    """
    Trata a coluna LOCAL separando em CIDADE e UF.
    Exemplo: 'Recife - PE' -> CIDADE: 'Recife', UF: 'PE'
    """
    df['LOCAL'] = df['LOCAL'].str.strip() 

    df[['CIDADE', 'UF']] = df['LOCAL'].str.split(' - ', expand=True)

    df['UF'] = df['UF'].str.strip()
    df['CIDADE'] = df['CIDADE'].str.strip()

    df = df.drop(columns=['LOCAL'])

    return df

# Desenvolvendo
def _limpar_categoria(df):
    """
    Limpa a coluna CATEGORIA: remove aspas, separa a hierarquia <-> 
    e extrai apenas a causa raiz do problema.
    """
    df['CATEGORIA'] = df['CATEGORIA'].str.replace('"', '', regex=False).str.replace("'", '', regex=False)

    df['CATEGORIA'] = df['CATEGORIA'].str.strip()

    return df

def _limpar_texto(texto):
    """
    Remove pontuação, stopwords e deixa o texto em maiúsculo.
    """
    if not isinstance(texto, str):
        return ""
    
    texto_limpo = re.sub(r'[^\w\s]', '', texto)
    
    stops = set(stopwords.words('portuguese'))
    
    palavras = texto_limpo.split()
    
    palavras_limpas = [w.upper() for w in palavras if w.lower() not in stops]
    
    return " ".join(palavras_limpas)

def _tratamento_tempo(df):
    colunas_redundantes = ['ANO', 'MES', 'DIA', 'DIA_DO_ANO', 'SEMANA_DO_ANO', 
                          'DIA_DA_SEMANA', 'TRIMETRES']

    df = df.drop(columns=colunas_redundantes)

    df = df.rename(columns={'TEMPO': 'DATA'})

    df['DATA'] = pd.to_datetime(df['DATA'])

    return df

def executar_limpeza(df):
    """
    Executa as etapas de limpeza dos dados.
    """
    df = _limpar_localidade(df)

    df = _tratamento_tempo(df)
    
    df['TEMA'] = df['TEMA'].str.strip().str.upper()

    df['DESCRICAO'] = df['DESCRICAO'].apply(_limpar_texto)

    return df
