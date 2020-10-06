from tika import parser
from os import path
import os

from noticias_ner import config


def converter_para_txt(caminho_arquivo, diretorio_alvo):
    nome_arquivo_texto = caminho_arquivo[caminho_arquivo.rfind(path.sep) + 1:caminho_arquivo.rfind('.')] + '.txt'
    caminho_arquivo_texto = os.path.join(diretorio_alvo, nome_arquivo_texto)

    if not os.path.exists(caminho_arquivo_texto):
        raw = parser.from_file(caminho_arquivo)
        with open(caminho_arquivo_texto, 'w', encoding='utf-8') as arquivo:
            arquivo.write(raw['content'])


if __name__ == '__main__':
    diretorio_pdf = config.diretorio_dados.joinpath('relatorios_cgu')
    diretorio_txt = diretorio_pdf.joinpath('txt')

    if not path.exists(diretorio_txt):
        os.makedirs(diretorio_txt)

    for root, subdirs, files in os.walk(diretorio_pdf):
        for file in files:
            if '.pdf' in file:
                converter_para_txt(os.path.join(root, file), diretorio_txt)
