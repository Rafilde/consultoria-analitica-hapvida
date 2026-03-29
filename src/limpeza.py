"""
Módulo de limpeza de dados para ReclameAqui.
Funções para padronização, tratamento de nulos e conversão de tipos.
"""
import pandas as pd 
import spacy
import re

nlp = spacy.load("pt_core_news_sm")

def _limpar_localidade(df):
    """
    Trata a coluna LOCAL separando em CIDADE e UF.
    Exemplo: 'Recife - PE' -> CIDADE: 'Recife', UF: 'PE'
    """
    # Padronização de localidade
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

def _limpar_categoria(df):
    """
    Remove aspas duplas e simples, e limpa espaços extras.
    """
    # Padronização de categoria
    df['CATEGORIA'] = df['CATEGORIA'].str.replace('"', '', regex=False).str.replace("'", '', regex=False)
    
    df['CATEGORIA'] = df['CATEGORIA'].str.strip()
    
    return df
def _classificar_hierarquia_detalhada(df):
    """
    Classifica a CATEGORIA em Origem, Serviço e agrupa Problemas específicos.
    """
    
    def extrair_detalhes(row):
        cat = str(row['CATEGORIA']).upper()
        
        if 'PLANO' in cat:
            origem = 'PLANO DE SAÚDE'
        elif 'HAPVIDA' in cat:
            origem = 'HAPVIDA SAÚDE'
        else:
            origem = 'OUTROS'
            
        mapeamento = {
            'ATENDIMENTO': ['ATENDIMENTO', 'SAC', 'CANAIS'],
            'AGENDAMENTO': ['AGENDAMENTO', 'HORÁRIOS', 'MARCAR'],
            'EXAMES / PROCEDIMENTOS': ['EXAME', 'LAB', 'IMAGEM', 'RESULTADO'],
            'FINANCEIRO': ['COBRANÇA', 'REEMBOLSO', 'ESTORNO', 'REAJUSTE', 'PAGAMENTO'],
            'AUTORIZAÇÃO': ['AUTORIZAÇÃO', 'DEMORA', 'PRAZO', 'EXECUÇÃO'],
            'ESTRUTURA / REDE': ['REDE', 'CLÍNICA', 'LEITOS', 'INFRAESTRUTURA', 'CREDENCIADA'],
            'ADMINISTRATIVO': ['ADMINISTRATIVO', 'CARTÃO', 'CANCELAR', 'PORTABILIDADE', 'CADASTRAIS'],
            'INFORMAÇÃO': ['INFORMAÇÃO', 'PROPAGANDA']
        }
        
        servico = 'OUTROS'
        for chave, palavras in mapeamento.items():
            if any(p in cat for p in palavras):
                servico = chave
                break
        
        partes = [p.strip() for p in cat.split('<->')]
        remover = ['HAPVIDA SAÚDE', 'PLANOS DE SAÚDE', 'PLANO', 'PLANOS', 'PLANO DE SAÚDE', 'ADMINISTRATIVO', 'NÃO ENCONTREI MEU PROBLEMA']
        problemas = [p for p in partes if p not in remover and len(p) > 2]
        
        return pd.Series([origem, servico, ", ".join(problemas)])

    df[['TIPO_ORIGEM', 'TIPO_SERVICO', 'PROBLEMA']] = df.apply(extrair_detalhes, axis=1)

    df = df.drop(columns=['CATEGORIA'])
    
    return df

NEGACOES = {'não', 'nem', 'nunca', 'jamais', 'nenhum', 'nada', 'ninguém'}
def _limpar_texto(texto):
    """
    Remove pontuação, aplica lematização com spaCy
    e remove stopwords mantendo negações.
    """
    # Padronização de texto
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
    # Conversão de tempo
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
    # Início da limpeza
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

    df = _limpar_categoria(df) 
    df = _classificar_hierarquia_detalhada(df)
    
    df['TEMA'] = df['TEMA'].str.strip().str.upper()
    df['DESCRICAO'] = df['DESCRICAO'].apply(_limpar_texto)

    df = df.astype({
        "CIDADE": "string",
        "UF": "string",
        "DESCRICAO": "string",
    })

    return df

# Função de teste simples para mostrar participação
def testar_limpeza():
    """
    Testa funções de limpeza com exemplos fictícios.
    """
    import pandas as pd
    df_exemplo = pd.DataFrame({
        'LOCAL': ['Fortaleza - CE', 'Recife - PE', None],
        'CATEGORIA': ['Plano de Saúde', 'Atendimento', 'Reembolso'],
        'DESCRICAO': ['Reclamação: atendimento ruim!', 'Demora no reembolso.', 'Não foi resolvido.'],
        'TEMPO': ['2022-03-11 10:00', '2022-03-12 11:00', '2022-03-13 12:00']
    })
    print("Localidade:")
    print(_limpar_localidade(df_exemplo.copy()))
    print("Categoria:")
    print(_limpar_categoria(df_exemplo.copy()))
    print("Texto:")
    print(df_exemplo['DESCRICAO'].apply(_limpar_texto))
    print("Tempo:")
    print(_tratamento_tempo(df_exemplo.copy()))

if __name__ == "__main__":
    testar_limpeza()