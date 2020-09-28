# -*- coding: utf-8 -*-
import logging
import os

import pandas as pd

from noticias_ner import config
from noticias_ner.cnpj.fabrica_provedor_cnpj import get_repositorio_cnpj


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
    repositorio_cnpj = get_repositorio_cnpj()

    for i in range(len(df)):
        classificacao, data, entidade, link, midia, texto, titulo, ufs = __get_valores(df, i, data, link, midia, texto,
                                                                                       titulo, ufs)

        if (not pd.isna(entidade)) and classificacao == 'ORGANIZAÇÃO':
            # Desconsidera empresas com nome com menos de 3 caracteres - esses casos têm grande chance de serem
            # falso-positivos indicados pelo NER.
            if len(entidade.strip()) > 2:
                map_empresa_to_cnpjs, tipo_busca = repositorio_cnpj.buscar_empresas_por_razao_social(entidade)
                qtd = len(map_empresa_to_cnpjs)
                qtd_cnpjs = 0

                if qtd > 0:
                    qtd_cnpjs = len(next(iter(map_empresa_to_cnpjs.values())))

                # Só adiciona a empresa ao resultado se ela foi ecnontrada nas bases (base RFB ou índice Lucene RFB) e,
                # caso filtrar_por_empresas_unicas seja igual a True, se sua razão social é única e associda a um único
                # CNPJ, para evitar confusão com empresas diferentes registradas na mesma razão social.  Futuramente,
                # poderão ser implementados modelos que permitam identificar a empresa mais adequada.
                if qtd > 0 and ((not filtrar_por_empresas_unicas) or (
                        filtrar_por_empresas_unicas and qtd == 1 and qtd_cnpjs == 1)):
                    resultado_analise[(titulo, link, midia, data, texto, ufs, entidade)] = [
                        (razao_social, cnpjs, tipo_busca) for razao_social, cnpjs in map_empresa_to_cnpjs.items()]

    if len(resultado_analise) > 0:
        df = pd.concat(
            {k: pd.DataFrame(v, columns=['POSSÍVEIS EMPRESAS CITADAS', 'POSSÍVEIS CNPJs CITADOS', 'TIPO BUSCA']) for
             k, v in
             resultado_analise.items()})
        repositorio_cnpj.persistir_informacoes(df)

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

    return classificacao, data, entidade, link, midia, texto, titulo, uf


if __name__ == '__main__':
    identificar_possiveis_empresas_citadas(os.path.join(config.diretorio_dados, 'ner.xlsx'),
                                           filtrar_por_empresas_unicas=True)
