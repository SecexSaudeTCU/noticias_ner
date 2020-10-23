import os

from noticias_ner import config
from os import path

from noticias_ner.util.conversor_txt import converter_para_txt

if __name__ == '__main__':
    diretorio = config.diretorio_dados.joinpath('relatorios_tcu')
    diretorio_txt = diretorio.joinpath('txt')

    if not path.exists(diretorio_txt):
        os.makedirs(diretorio_txt)

    for root, subdirs, files in os.walk(diretorio):
        for file in files:
            if '.pdf' in file or '.docx' in file or '.doc' in file or '.rtf' in file:
                converter_para_txt(os.path.join(root, file), diretorio_txt)
            else:
                print('Formato não suportado: ' + file)
