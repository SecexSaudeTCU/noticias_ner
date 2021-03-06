import os
import sys

# Adiciona diretorio raiz ao PATH. Devido a ausência de setup.py, isto garante que as importações sempre funcionarão
from noticias_ner.relatorios_cgu.extrator_entidades_relatorios_cgu import extrair_entidades

diretorio_raiz = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
sys.path.append(diretorio_raiz)

from noticias_ner import config

if __name__ == '__main__':
    # Executa a extração de entidades
    arquivo_entidades = extrair_entidades(os.path.join(config.diretorio_dados, 'relatorios_cgu', 'relatorios_cgu.xlsx'))
