import pandas as pd 
import spacy
import re

nlp = spacy.load("pt_core_news_sm")

def _limpar_localidade(df):
    """
    Trata a coluna LOCAL separando em CIDADE e UF.
    Exemplo: 'Recife - PE' -> CIDADE: 'Recife', UF: 'PE'
    """
    df['LOCAL'] = df['LOCAL'].fillna("").astype(str).str.strip()

    split = df['LOCAL'].str.split(' - ', n=1, expand=True)

    df['CIDADE'] = split[0].str.strip()

    if split.shape[1] > 1:
        df['UF'] = split[1].str.strip()
    else:
        df['UF'] = pd.NA

    df['CIDADE'] = df['CIDADE'].mask(
        df['CIDADE'].str.lower().isin(['naoconsta', '', 'nan', '--', None, 'n/a', 'nao consta', 'desconecido', 'nao informado']),
        "NÃO INFORMADO"
    )

    df['UF'] = df['UF'].mask(
        df['UF'].isin(['naoconsta', '', 'nan', '--', None, 'n/a', 'nao consta', 'desconecido', 'nao informado']),
        "NÃO INFORMADO"
    )

    df['CIDADE'] = df['CIDADE'].str.upper()
    df['UF'] = df['UF'].str.upper()

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

NEGACOES = {'não', 'nem', 'nunca', 'jamais', 'nenhum', 'nada', 'ninguém'}
def _limpar_texto(texto):
    """
    Remove pontuação, aplica lematização com spaCy
    e remove stopwords mantendo negações.
    """
    if not isinstance(texto, str):
        return ""
    texto = str(texto)
    texto = re.sub(r'[^\w\s]', '', texto)
    doc = nlp(texto.lower())
    palavras_limpas = [
        token.lemma_.upper()
        for token in doc
        if not token.is_punct and not token.is_space
        and (not token.is_stop or token.lemma_ in NEGACOES)  
    ]
    return " ".join(palavras_limpas)

def _tratamento_tempo(df):
    """
    Realiza o tratamento da coluna TEMPO, removendo colunas redundantes e convertendo para datetime
    """
    colunas_redundantes = ['ANO', 'MES', 'DIA', 'DIA_DO_ANO', 'SEMANA_DO_ANO', 
                          'DIA_DA_SEMANA', 'TRIMETRES']

    df = df.drop(columns=[c for c in colunas_redundantes if c in df.columns])

    df = df.rename(columns={'TEMPO': 'DATA'})

    df['DATA'] = pd.to_datetime(df['DATA'], errors='coerce')

    return df

def executar_limpeza(df):
    """
    Executa as etapas de limpeza dos dados.
    """
    df = df.astype({
        "TEMA": "string",
        "LOCAL": "string",
        "CATEGORIA": "string",
        "STATUS": "string",
        "DESCRICAO": "string",
        "URL": "string"
    })

    df = _limpar_localidade(df)

    df = _tratamento_tempo(df)
    
    df['TEMA'] = df['TEMA'].str.strip().str.upper()

    df['DESCRICAO'] = df['DESCRICAO'].apply(_limpar_texto)

    df = df.astype({
        "CIDADE": "string",
        "UF": "string",
        "DESCRICAO": "string",
    })

    return df
