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
    acao_de_controle = situacao = municipio = data_homologacao = None
    repositorio_cnpj = get_repositorio_cnpj()

    for i in range(len(df)):
        classificacao, entidade, (acao_de_controle, situacao, municipio, data_homologacao) = __get_valores(df, i,
                                                                                                           acao_de_controle,
                                                                                                           situacao,
                                                                                                           municipio,
                                                                                                           data_homologacao)

        adicionar_aos_resultados(classificacao, entidade, filtrar_por_empresas_unicas, repositorio_cnpj,
                                 resultado_analise, (acao_de_controle, situacao, municipio, data_homologacao))

    persistir_informacoes(repositorio_cnpj, resultado_analise)

    logger = logging.getLogger('covidata')
    logger.info('Processamento concluído.')

    return config.arquivo_gerado_final


def __get_valores(df, i, acao_de_controle, situacao, municipio, data_homologacao):
    if not pd.isna(df.iloc[i, 0]):
        acao_de_controle = df.iloc[i, 0]
    if not pd.isna(df.iloc[i, 1]):
        situacao = df.iloc[i, 1]
    if not pd.isna(df.iloc[i, 2]):
        municipio = df.iloc[i, 2]
    if not pd.isna(df.iloc[i, 3]):
        data_homologacao = df.iloc[i, 3]

    entidade = df.iloc[i, 6]
    classificacao = df.iloc[i, 7]

    return classificacao, entidade, (acao_de_controle, situacao, municipio, data_homologacao)


if __name__ == '__main__':
    identificar_possiveis_empresas_citadas(config.diretorio_dados.joinpath('ner_constatacoes.xlsx'),
                                           filtrar_por_empresas_unicas=True)
