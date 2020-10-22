"""
Work in progress...

TODO:

"""
import logging
import os
import time

import pandas as pd
from newspaper import Article
import jsonlines

from noticias_ner import config


def get_text(url, max_retries=5, sleep=5):
    """
    Extrai e retorna texto do artigo da URL
    """
    logger = logging.getLogger('covidata')
    # Tentar max_retries vezes
    for i in range(0, max_retries):
        try:
            article = Article(url)
            article.download()
            article.parse()
        except:
            logger.error(f'Erro ao processar {url}. Tentando novamente em {sleep} segundos ({i + 1}/{max_retries})')
            time.sleep(sleep)
        return article.text

    logger.info(f'Número máximo de tentativas atingido. Retornando ERRO')
    return 'ERRO'


def recuperar_textos(caminho_arquivo_noticias):
    global row
    df = pd.read_excel(caminho_arquivo_noticias)
    textos = []
    logger = logging.getLogger('covidata')
    textos_json = []

    for i, row in df.iterrows():
        logger.info(f'Processando URL {i}')
        texto = get_text(row.link)
        textos.append(texto)
        textos_json.append({'text': texto})

    df['texto'] = textos
    df.to_excel(os.path.join(config.diretorio_dados, 'com_textos.xlsx'))

    metade = int(len(textos_json) / 2)

    with jsonlines.open('json1.jsonl', 'w') as writer:
        writer.write_all(textos_json[:metade])

    with jsonlines.open('json2.jsonl', 'w') as writer:
        writer.write_all(textos_json[metade:])

    return df
