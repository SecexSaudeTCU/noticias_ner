import itertools
import json
import os

import pandas as pd
import requests

from noticias_ner import config


def identificar_possiveis_empresas_citadas(caminho_arquivo, filtrar_por_empresas_unicas=False):
    """
    Executa o passo responsável por, a partir das entidades do tipo ORGANIZAÇÃO, identificar possíveis valores para os
    CNPJs dessas empresas, utilizando inicialmente busca textual.
    """
    df = pd.read_excel(caminho_arquivo)
    resultado_analise = dict()
    data = link = midia = texto = titulo = ufs = None

    for i in range(len(df)):
        classificacao, data, entidade, link, midia, texto, titulo, ufs = __get_valores(df, i, data, link, midia, texto,
                                                                                       titulo, ufs)

        if (not pd.isna(entidade)) and classificacao == 'ORGANIZAÇÃO':
            # Desconsidera empresas com nome com menos de 3 caracteres - esses casos têm grande chance de serem
            # falso-positivos indicados pelo NER.
            if len(entidade.strip()) > 2:
                map_empresa_to_cnpjs, tipo_busca = __buscar_empresas_por_razao_social(entidade)
                qtd = len(map_empresa_to_cnpjs)
                if qtd > 0 and ((not filtrar_por_empresas_unicas) or (filtrar_por_empresas_unicas and qtd == 1)):
                    resultado_analise[(titulo, link, midia, data, texto, ufs, entidade)] = [
                        (razao_social, cnpjs, tipo_busca) for razao_social, cnpjs in map_empresa_to_cnpjs.items()]

    df = pd.concat(
        {k: pd.DataFrame(v, columns=['POSSÍVEIS EMPRESAS CITADAS', 'POSSÍVEIS CNPJs CITADOS', 'TIPO BUSCA']) for k, v in
         resultado_analise.items()})

    df.to_excel(os.path.join(config.diretorio_dados, 'com_empresas.xlsx'))
    print('Processamento concluído.')


def __get_valores(df, i, data, link, midia, texto, titulo, uf):
    if not pd.isna(df.iloc[i, 0]):
        titulo = df.iloc[i, 0]
    if not pd.isna(df.iloc[i, 1]):
        link = df.iloc[i, 1]
    if not pd.isna(df.iloc[i, 2]):
        midia = df.iloc[i, 2]
    if not pd.isna(df.iloc[i, 3]):
        data = df.iloc[i, 3]
    if not pd.isna(df.iloc[i, 4]):
        texto = df.iloc[i, 4]
    if not pd.isna(df.iloc[i, 5]):
        uf = df.iloc[i, 5]

    entidade = df.iloc[i, 7]
    classificacao = df.iloc[i, 8]

    return classificacao, data, entidade, link, midia, texto, titulo, uf


def __buscar_empresas_por_razao_social(razao_social):
    resultado = json.loads(requests.get(config.url_api_cnpj + razao_social).content)
    map_empresa_to_cnpjs = resultado['dados']['empresas']
    tipo_busca = resultado['dados']['tipo_busca']
    return map_empresa_to_cnpjs, tipo_busca


if __name__ == '__main__':
    identificar_possiveis_empresas_citadas(os.path.join(config.diretorio_dados, 'ner.xlsx'))
