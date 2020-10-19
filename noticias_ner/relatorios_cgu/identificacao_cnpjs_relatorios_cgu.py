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
    id = id_arquivo = link = titulo = tipo_servico = grupo_atividade = linha_acao = avaliacao_politica_publica = \
        data_publicacao = localidades = trechos = None
    repositorio_cnpj = get_repositorio_cnpj()

    for i in range(len(df)):
        classificacao, entidade, (
            id, id_arquivo, link, titulo, tipo_servico, grupo_atividade, linha_acao, avaliacao_politica_publica,
            data_publicacao, localidades, trechos) = __get_valores(df, i, id, id_arquivo, link, titulo, tipo_servico,
                                                                   grupo_atividade, linha_acao,
                                                                   avaliacao_politica_publica,
                                                                   data_publicacao, localidades, trechos)

        adicionar_aos_resultados(classificacao, entidade, filtrar_por_empresas_unicas, repositorio_cnpj,
                                 resultado_analise,
                                 (id, id_arquivo, link, titulo, tipo_servico, grupo_atividade, linha_acao,
                                  avaliacao_politica_publica, data_publicacao, localidades, trechos))

    persistir_informacoes(repositorio_cnpj, resultado_analise)

    logger = logging.getLogger('covidata')
    logger.info('Processamento concluído.')

    return config.arquivo_gerado_final


def __get_valores(df, i, id, id_arquivo, link, titulo, tipo_servico, grupo_atividade, linha_acao,
                  avaliacao_politica_publica, data_publicacao, localidades, trechos):
    if not pd.isna(df.iloc[i, 0]):
        id = df.iloc[i, 0]
    if not pd.isna(df.iloc[i, 1]):
        id_arquivo = df.iloc[i, 1]
    if not pd.isna(df.iloc[i, 2]):
        link = df.iloc[i, 2]
    if not pd.isna(df.iloc[i, 3]):
        titulo = df.iloc[i, 3]
    if not pd.isna(df.iloc[i, 4]):
        tipo_servico = df.iloc[i, 4]
    if not pd.isna(df.iloc[i, 5]):
        grupo_atividade = df.iloc[i, 5]
    if not pd.isna(df.iloc[i, 6]):
        linha_acao = df.iloc[i, 6]
    if not pd.isna(df.iloc[i, 7]):
        avaliacao_politica_publica = df.iloc[i, 7]
    if not pd.isna(df.iloc[i, 8]):
        data_publicacao = df.iloc[i, 8]
    if not pd.isna(df.iloc[i, 9]):
        localidades = df.iloc[i, 9]
    if not pd.isna(df.iloc[i, 10]):
        trechos = df.iloc[i, 10]

    entidade = df.iloc[i, 12]
    classificacao = df.iloc[i, 13]

    return classificacao, entidade, (id, id_arquivo, link, titulo, tipo_servico, grupo_atividade, linha_acao, \
                                     avaliacao_politica_publica, data_publicacao, localidades, trechos)


if __name__ == '__main__':
    identificar_possiveis_empresas_citadas(
        'C:\\Users\\Monique\\Documents\\TCU\\SecexSaude\\noticias_ner\\noticias_ner\\ner_14.xlsx',
        filtrar_por_empresas_unicas=True)
