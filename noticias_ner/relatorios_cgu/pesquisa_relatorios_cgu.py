import json
import os

import pandas as pd
import requests

from noticias_ner import config
from noticias_ner.util.download import download


def __processar_pagina(offset, linhas_df_metadados):
    url = f'https://eaud.cgu.gov.br/api/relatorios?colunaOrdenacao=dataPublicacao&direcaoOrdenacao=DESC&tamanhoPagina=15&offset={offset}&palavraChave=alimenta%C3%A7%C3%A3o+escolar&_=1602013087164'
    print(url)
    resultado = json.loads(requests.get(url).content)
    dados = resultado['data']

    for registro in dados:
        id = registro['id']
        url_arquivo = f'https://eaud.cgu.gov.br/relatorios/download/{id}'
        nome_arquivo = f'arquivo_{id}.pdf'
        download(url_arquivo, config.diretorio_dados.joinpath('relatorios_cgu'), nome_arquivo)
        linha_df_metadados = [id, registro['idArquivo'], url_arquivo, registro['titulo'], registro['tipoServico'],
                              registro['grupoAtividade'], registro['linhaAcao'], registro['avaliacaoPoliticaPublica'],
                              registro['dataPublicacao'], registro['localidades'], registro['trecho']]
        linhas_df_metadados.append(linha_df_metadados)

    return resultado


if __name__ == '__main__':
    linhas_df_metadados = []

    # Processa a primeira página
    resultado = __processar_pagina(0, linhas_df_metadados)

    # Processa as páginas subsequentes
    qtd = resultado['recordsTotal']
    for offset in range(15, qtd + 1, 15):
        print(offset)
        __processar_pagina(offset, linhas_df_metadados)

    colunas_df_metadados = ['ID', 'ID_ARQUIVO', 'LINK', 'TÍTULO', 'TIPO DE_SERVIÇO', 'GRUPO DE ATIVIDADE',
                            'LINHA DE AÇÃO', 'AVALIAÇÃO DE POLÍTICA PÚBLICA', 'PUBLICADO EM', 'LOCALIDADES', 'TRECHOS']
    df_metadados = pd.DataFrame(linhas_df_metadados, columns=colunas_df_metadados)
    df_metadados.to_excel(os.path.join(config.diretorio_dados, '', 'relatorios_cgu.xlsx'))
