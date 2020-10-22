import os
from os import path

from tika import parser


def converter_para_txt(caminho_arquivo, diretorio_alvo):
    nome_arquivo_texto = caminho_arquivo[caminho_arquivo.rfind(path.sep) + 1:caminho_arquivo.rfind('.')] + '.txt'
    caminho_arquivo_texto = os.path.join(diretorio_alvo, nome_arquivo_texto)

    if not os.path.exists(caminho_arquivo_texto):
        raw = parser.from_file(caminho_arquivo)
        with open(caminho_arquivo_texto, 'w', encoding='utf-8') as arquivo:
            arquivo.write(raw['content'])
