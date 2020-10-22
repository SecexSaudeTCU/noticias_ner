import pandas as pd

from noticias_ner import config
from noticias_ner.util.download import download

if __name__ == '__main__':
    diretorio = config.diretorio_dados.joinpath('relatorios_tcu')
    df = pd.read_excel(diretorio.joinpath('extracao relatorios fiscobras.xlsx'))
    arquivos = ['N/A'] * len(df)
    qtd_maxima = 100
    inicio = 101
    qtd = 0

    for i, row in df.iterrows():
        if i >= inicio:
            nome_arquivo = download(row.URL, diretorio)
            if nome_arquivo:
                arquivos[i] = nome_arquivo
                qtd += 1
            if qtd == qtd_maxima:
                break

    df['arquivo'] = arquivos
    df.to_excel(diretorio.joinpath('com_nomes_arquivos.xlsx'))
