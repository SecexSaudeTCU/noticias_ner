# -*- coding: utf-8 -*-
import logging
import os

import pandas as pd

from noticias_ner import config
from noticias_ner.cnpj.fabrica_provedor_cnpj import get_repositorio_cnpj
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
    fiscalis = num_processo = url = tipo_peca = data = id_arq_catalogado = versao = None
    repositorio_cnpj = get_repositorio_cnpj()

    for i in range(len(df)):
        classificacao, entidade, (
            fiscalis, num_processo, url, tipo_peca, data, id_arq_catalogado, versao) = __get_valores(df, i, fiscalis,
                                                                                                     num_processo, url,
                                                                                                     tipo_peca, data,
                                                                                                     id_arq_catalogado,
                                                                                                     versao)

        adicionar_aos_resultados(classificacao, entidade, filtrar_por_empresas_unicas, repositorio_cnpj,
                                 resultado_analise,
                                 (fiscalis, num_processo, url, tipo_peca, data, id_arq_catalogado, versao))

    persistir_informacoes(repositorio_cnpj, resultado_analise)

    logger = logging.getLogger('covidata')
    logger.info('Processamento concluído.')

    return config.arquivo_gerado_final


def __get_valores(df, i, fiscalis, num_processo, url, tipo_peca, data, id_arq_catalogado, versao):
    if not pd.isna(df.iloc[i, 1]):
        fiscalis = df.iloc[i, 1]
    if not pd.isna(df.iloc[i, 2]):
        num_processo = df.iloc[i, 2]
    if not pd.isna(df.iloc[i, 3]):
        url = df.iloc[i, 3]
    if not pd.isna(df.iloc[i, 4]):
        tipo_peca = df.iloc[i, 4]
    if not pd.isna(df.iloc[i, 5]):
        data = df.iloc[i, 5]
    if not pd.isna(df.iloc[i, 6]):
        id_arq_catalogado = df.iloc[i, 6]
    if not pd.isna(df.iloc[i, 7]):
        versao = df.iloc[i, 7]

    entidade = df.iloc[i, 9]
    classificacao = df.iloc[i, 10]

    return classificacao, entidade, (fiscalis, num_processo, url, tipo_peca, data, id_arq_catalogado, versao)


if __name__ == '__main__':
    identificar_possiveis_empresas_citadas(config.diretorio_dados.joinpath('ner_tcu.xlsx'),
                                           filtrar_por_empresas_unicas=True)
