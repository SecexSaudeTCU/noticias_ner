import logging
import os
import time

import pandas as pd

from noticias_ner import config
from noticias_ner.noticias.gnews import executar_busca
from noticias_ner.noticias.ner.bert.bert_ner import FinedTunedBERT_NER
from noticias_ner.noticias.parse_news import recuperar_textos


def __get_NERs():
    return [
        FinedTunedBERT_NER()
    ]


def extrair_entidades(arquivo):
    """
    Extrai as entidade de um arquivo com extensão .xlsx que contém o conjunto de textos a serem analisados, bem como
    seus metadados.  O resultado é salvo em um arquivo chamado ner.xlsx.

    :param arquivo Caminho para o arquivo.
    """
    logger = logging.getLogger('covidata')
    df = pd.read_excel(arquivo)

    logger.info('Extraindo entidades relevantes das notícias...')
    ners = __get_NERs()
    writer = pd.ExcelWriter(os.path.join(config.diretorio_dados, 'ner.xlsx'), engine='xlsxwriter')

    for ner in ners:
        algoritmo = ner.get_nome_algoritmo()
        logger.info('Aplicando implementação ' + algoritmo)
        start_time = time.time()
        df_resultado = ner.extrair_entidades(df)
        logger.info("--- %s segundos ---" % (time.time() - start_time))
        df_resultado.to_excel(writer, sheet_name=algoritmo)

    writer.save()
    logger.info('Processamento concluído.')


def obter_textos():
    """
    Obtém os textos de notícias da Internet.
    """
    logger = logging.getLogger('covidata')
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())
    start_time = time.time()
    logger.info('Buscando as notícias na Internet...')
    arquivo_noticias = executar_busca()
    recuperar_textos(arquivo_noticias)
    logger.info("--- %s minutos ---" % ((time.time() - start_time) / 60))


if __name__ == '__main__':
    #extrair_entidades(os.path.join(config.diretorio_noticias, 'com_textos_baseline.xlsx'))
    #obter_textos()
    extrair_entidades(os.path.join(config.diretorio_dados, 'com_textos.xlsx'))
