import pandas as pd

from noticias_ner import config
from noticias_ner.util.download import download

if __name__ == '__main__':
    diretorio = config.diretorio_dados.joinpath('relatorios_tcu')
    df = pd.read_excel(diretorio.joinpath('extracao relatorios fiscobras.xlsx'))
    arquivos = ['N/A'] * len(df)

    for i, row in df.iterrows():
        nome_arquivo = download(row.URL, diretorio)
        if nome_arquivo:
            arquivos[i] = nome_arquivo
        # TODO: tirar isso!
        break

    df['arquivo'] = arquivos
    df.to_excel(diretorio.joinpath('com_nomes_arquivos.xlsx'))
