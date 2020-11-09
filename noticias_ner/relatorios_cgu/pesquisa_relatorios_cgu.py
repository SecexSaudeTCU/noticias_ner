import json
import os

import pandas as pd
import requests

from noticias_ner import config
from noticias_ner.util.download import download


def __baixar_relatorio(acao_de_controle):
    # url = f'https://eaud.cgu.gov.br/api/relatorios?colunaOrdenacao=dataPublicacao&direcaoOrdenacao=DESC&tamanhoPagina=15&offset={offset}&palavraChave=alimenta%C3%A7%C3%A3o+escolar&_=1602013087164'
    url = f'https://eaud.cgu.gov.br/api/relatorios?colunaOrdenacao=dataPublicacao&direcaoOrdenacao=DESC&tamanhoPagina=15&palavraChave={acao_de_controle}&_=1602013087164'
    print(url)
    resultado = json.loads(requests.get(url).content)
    dados = resultado['data']

    if len(dados) > 0:
        registro = dados[0]
        id = registro['id']
        url_arquivo = f'https://eaud.cgu.gov.br/relatorios/download/{id}'
        nome_arquivo = f'arquivo_{acao_de_controle}.pdf'
        download(url_arquivo, config.diretorio_dados.joinpath('pnae'), nome_arquivo)


if __name__ == '__main__':
    df = pd.read_excel(config.diretorio_dados.joinpath('pnae').joinpath(
        'Ações de Controle PNAE achados CGU (adaptado da versão original da CGU) atualizado até 04_11_2020.xlsx'))

    for i, row in df.iterrows():
        __baixar_relatorio(row['Ação de Controle'])
