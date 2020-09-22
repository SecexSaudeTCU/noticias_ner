"""
Rotina de extração de notícias da aba News do Google a partir de string de busca e dias de início e fim.

"""
import datetime as DT
import logging
import os
import time
from datetime import date
from os import path

import pandas as pd
from GoogleNews import GoogleNews

from noticias_ner import config


def extrai_noticias_google(q, dia_inicio, dia_fim, num_limite_paginas=1, lang='pt-BR', sleep=1, tentativas=5):
    """
    Retorna data frame com as notícias obtidas na aba News do Google

    Parâmetros
    ----------
        q : str
            String de busca

        data_inicio, dta_fim : datatime.Date
            Datas de início e fim para realização da busca

        num_limite_num_limite_paginas : int
            Número máxima de páginas que serão obtidas.

        lang : str
            Código da lingua para realização da busca (padrão pt-BR)

        sleep : int
            Número de segundos para esperar entre tentativas após cada erro de obtenção de página

        tentativas : int
            Número de tentativas de obnteção de uma página antes de se considerar a extração concluída

    Retorno
    -------
        resultados : DataFrame
            Dataframe com os reulstados de busca
    """

    # String de busca formatado adequadamente para URL
    # q = urllib.parse.quote(q)

    # Strings com as datas no formato esperado pela lib GoogleNews
    formato_data = '%m/%d/%Y'
    dia_inicio_formatado = dia_inicio.strftime(formato_data)
    dia_fim_formatado = dia_fim.strftime(formato_data)

    # Instancia interface de busca ao Google News com idioma pt-BR e período adequado
    gn = GoogleNews(lang=lang, start=dia_inicio_formatado, end=dia_fim_formatado)

    # Inicializa lista para armazenar os resultados de busca
    resultados = []

    # Realiza busca da primeira página
    logger = logging.getLogger('covidata')
    logger.info(f'Buscando página 1')
    gn.search(q)
    print(len(gn.result()), gn.result())
    resultados = resultados + gn.result()
    gn.clear()

    # Para a página 2 em diante (p2 corresponde ao índice 1)
    for i in range(2, num_limite_paginas + 1):

        logger.info(f'Buscando página {i}')

        # Busca a página
        gn.getpage(i)

        # Adiciona reusltado à lista
        resultados = resultados + gn.result()

        print(len(gn.result()), gn.result())

        # Caso a consulta à página não tenha gerado resultados
        if gn.result() == []:
            logger.info(f'A consulta à página {i} não retornou nehnum resultado')

            # Diminui o contador de tentaivas
            tentativas = tentativas - 1
            logger.info(f'*** Há {tentativas} restantes ***')

            # Caso o número de tentativas tenha chegado a zero, interrompe a execução
            if tentativas < 1:
                break

            # Caso contrário
            else:
                # Pausa script por sleep segundos antes de buscar a próxima página
                logger.info(f'Execução interrompida por {sleep} segundos')
                time.sleep(sleep)

        # Apaga cache do resultado
        gn.clear()

    # Cria e retorna dataframe
    return pd.DataFrame(resultados)


def executar_busca(data_inicial, q):
    dia_inicio = __get_dia_inicio(data_inicial)
    dia_fim = date.today()

    # Número limite de páginas
    num_limite_paginas = 100

    # Realiza busca
    df = extrai_noticias_google(q, dia_inicio, dia_fim, num_limite_paginas=num_limite_paginas, sleep=10, tentativas=10)

    # Salva resultados
    if not path.exists(config.diretorio_dados):
        os.makedirs(config.diretorio_dados)

    caminho_arquivo_resultante = os.path.join(config.diretorio_dados, f'noticias_n_{len(df)}.xlsx')
    df.to_excel(caminho_arquivo_resultante)

    return caminho_arquivo_resultante


def __get_dia_inicio(data_inicial):
    if not data_inicial:
        today = DT.date.today()
        dia_inicio = today - DT.timedelta(days=7)
    else:
        dia_inicio = date.fromisoformat(data_inicial)
    return dia_inicio
