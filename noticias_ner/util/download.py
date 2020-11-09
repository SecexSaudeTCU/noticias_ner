import os
from os import path

import requests


def download(url, diretorio, nome_arquivo=None):
    """
    Executa o download do arquivo.
    """
    if not path.exists(diretorio):
        os.makedirs(diretorio)

    caminho_arquivo = diretorio

    if nome_arquivo:
        caminho_arquivo = os.path.join(diretorio, nome_arquivo)

    if (not nome_arquivo) or (not os.path.exists(caminho_arquivo)):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/50.0.2661.102 Safari/537.36'}
        r = requests.get(url, headers=headers, verify=False, timeout=60)

        if r.status_code != 500:
            if 'Content-Disposition' in r.headers:
                caminho_arquivo = os.path.join(diretorio, nome_arquivo)

                with open(caminho_arquivo, 'wb') as f:
                    f.write(r.content)

            return nome_arquivo

        return None
