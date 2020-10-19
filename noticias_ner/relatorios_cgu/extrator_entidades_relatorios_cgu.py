import logging
import os
import time

import pandas as pd
from backports.datetime_fromisoformat import MonkeyPatch

from noticias_ner import config
from noticias_ner.ner.bert.bert_ner import FinedTunedBERT_NER
from noticias_ner.relatorios_cgu.ner_relatorios_cgu import ExtratorEntidadesRelatoriosCGU

MonkeyPatch.patch_fromisoformat()


def __get_NERs():
    return [
        FinedTunedBERT_NER()
    ]


def extrair_entidades(arquivo, extrator_entidades=ExtratorEntidadesRelatoriosCGU(), arquivo_saida='ner.xlsx'):
    """
    Extrai as entidade de um arquivo com extensão .xlsx que contém o conjunto de textos a serem analisados, bem como
    seus metadados.  O resultado é salvo em um arquivo XLSX.
    :param arquivo: Caminho para o arquivo.
    :return: Caminho para o arquivo gerado.
    """
    logger = logging.getLogger('covidata')
    df = pd.read_excel(arquivo)

    logger.info('Extraindo entidades relevantes dos relatórios...')
    ners = __get_NERs()
    caminho_arquivo = os.path.join(config.diretorio_dados, arquivo_saida)
    writer = pd.ExcelWriter(caminho_arquivo, engine='xlsxwriter')

    for ner in ners:
        algoritmo = ner.get_nome_algoritmo()
        logger.info('Aplicando implementação ' + algoritmo)
        start_time = time.time()
        df_resultado = extrator_entidades.extrair_entidades(df, ner)
        logger.info("--- %s segundos ---" % (time.time() - start_time))
        df_resultado.to_excel(writer, sheet_name=algoritmo)

    writer.save()
    logger.info('Processamento concluído.')
    return caminho_arquivo
