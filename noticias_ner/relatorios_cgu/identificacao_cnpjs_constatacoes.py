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
    arquivo = constatacao = None
    repositorio_cnpj = get_repositorio_cnpj()

    for i in range(len(df)):
        classificacao, entidade, (arquivo, constatacao) = __get_valores(df, i, arquivo, constatacao)

        adicionar_aos_resultados(classificacao, entidade, filtrar_por_empresas_unicas, repositorio_cnpj,
                                 resultado_analise, (arquivo, constatacao))

    persistir_informacoes(repositorio_cnpj, resultado_analise)

    logger = logging.getLogger('covidata')
    logger.info('Processamento concluído.')

    return config.arquivo_gerado_final


def __get_valores(df, i, arquivo, constatacao):
    if not pd.isna(df.iloc[i, 0]):
        arquivo = df.iloc[i, 0]
    if not pd.isna(df.iloc[i, 1]):
        constatacao = df.iloc[i, 1]

    entidade = df.iloc[i, 3]
    classificacao = df.iloc[i, 4]

    return classificacao, entidade, (arquivo, constatacao)


if __name__ == '__main__':
    diretorio = config.diretorio_dados.joinpath('relatorios_cgu').joinpath('ner').joinpath('constatacoes')
    for root, subdirs, files in os.walk(diretorio):
        for file in files:
            identificar_possiveis_empresas_citadas(os.path.join(root, file), filtrar_por_empresas_unicas=True)
