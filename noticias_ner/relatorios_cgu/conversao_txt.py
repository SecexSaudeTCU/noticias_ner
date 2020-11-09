import os

from noticias_ner import config
from os import path

from noticias_ner.util.conversor_txt import converter_para_txt

if __name__ == '__main__':
    diretorio_pdf = config.diretorio_dados.joinpath('pnae')
    diretorio_txt = diretorio_pdf.joinpath('txt')

    if not path.exists(diretorio_txt):
        os.makedirs(diretorio_txt)

    for root, subdirs, files in os.walk(diretorio_pdf):
        for file in files:
            if '.pdf' in file:
                converter_para_txt(os.path.join(root, file), diretorio_txt)