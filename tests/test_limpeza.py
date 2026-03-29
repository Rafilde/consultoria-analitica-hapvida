import pytest
import pandas as pd
import sys
import os
sys.path.append(os.path.abspath("src"))
from limpeza import _limpar_localidade, _limpar_categoria, _limpar_texto, _tratamento_tempo

def test_limpar_localidade():
    df = pd.DataFrame({'LOCAL': ['Recife - PE', 'Fortaleza - CE', None, 'naoconsta']})
    df_result = _limpar_localidade(df.copy())
    assert 'CIDADE' in df_result.columns
    assert 'UF' in df_result.columns
    assert df_result.loc[0, 'CIDADE'] == 'RECIFE'
    assert df_result.loc[0, 'UF'] == 'PE'
    assert df_result.loc[2, 'CIDADE'] == 'NÃO INFORMADO'
    assert df_result.loc[3, 'CIDADE'] == 'NÃO INFORMADO'

def test_limpar_categoria():
    df = pd.DataFrame({'CATEGORIA': ['"Plano de Saúde"', "'Atendimento'", 'Reembolso']})
    df_result = _limpar_categoria(df.copy())
    assert df_result.loc[0, 'CATEGORIA'] == 'Plano de Saúde'
    assert df_result.loc[1, 'CATEGORIA'] == 'Atendimento'
    assert df_result.loc[2, 'CATEGORIA'] == 'Reembolso'

def test_limpar_texto():
    texto = 'Reclamação: atendimento ruim!'
    resultado = _limpar_texto(texto)
    assert isinstance(resultado, str)
    assert 'RECLAMAÇÃO' in resultado or 'ATENDIMENTO' in resultado

def test_tratamento_tempo():
    df = pd.DataFrame({'TEMPO': ['2022-03-11 10:00', '2022-03-12 11:00']})
    df_result = _tratamento_tempo(df.copy())
    assert 'DATA' in df_result.columns
    assert pd.to_datetime(df_result.loc[0, 'DATA'], errors='coerce') is not pd.NaT
