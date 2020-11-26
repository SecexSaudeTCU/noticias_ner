# -*- coding: utf-8 -*-
import logging
import os

import pandas as pd
from cnpjutil.cnpj.fabrica_provedor_cnpj import get_repositorio_cnpj

from noticias_ner import config
from noticias_ner.cnpj.identificacao_cnpjs import adicionar_aos_resultados, persistir_informacoes


def identificar_possiveis_empresas_citadas(caminho_arquivo, filtrar_por_empresas_unicas=False):
    """
    Executa o passo responsavel por, a partir das entidades do tipo ORGANIZACAO, identificar possiveis valores para os
    CNPJs dessas empresas, utilizando inicialmente busca textual.
    :param caminho_arquivo:  Caminho para o arquivo de entrada.
    :param filtrar_por_empresas_unicas:  Caso seja True, retorna apenas entidades do tipo ORGANIZACAO que estejam
    associadas a exatamente uma razao social.
    :return: Caminho para o arquivo de saida.
    """
    df = pd.read_excel(caminho_arquivo)
    resultado_analise = dict()
    data = link = midia = texto = titulo = ufs = None
    repositorio_cnpj = get_repositorio_cnpj(str(config.arquivo_config_cnpj))

    for i in range(len(df)):
        classificacao, entidade, (data, link, midia, texto, titulo, ufs) = __get_valores(df, i, data, link, midia,
                                                                                         texto, titulo, ufs)

        adicionar_aos_resultados(classificacao, entidade, filtrar_por_empresas_unicas, repositorio_cnpj,
                                 resultado_analise, (data, link, midia, texto, titulo, ufs))

    persistir_informacoes(repositorio_cnpj, resultado_analise)

    logger = logging.getLogger('covidata')
    logger.info('Processamento concluído.')

    return config.arquivo_gerado_final


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

    return classificacao, entidade, (data, link, midia, texto, titulo, uf)


if __name__ == '__main__':
    identificar_possiveis_empresas_citadas(os.path.join(config.diretorio_dados, 'ner.xlsx'),
                                           filtrar_por_empresas_unicas=True)
