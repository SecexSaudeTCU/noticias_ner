import os
import sys

from noticias_ner import config
from noticias_ner.noticias.extrator_entidades_noticias import obter_textos, extrair_entidades
from noticias_ner.noticias.identificacao_cnpjs import identificar_possiveis_empresas_citadas

if __name__ == '__main__':
    data_inicial = None

    if len(sys.argv) > 1:
        data_inicial = sys.argv[1]

    # Baixa as notícias da Web
    if data_inicial:
        obter_textos(data_inicial)
    else:
        obter_textos()

    # Executa a extração de entidades
    extrair_entidades(os.path.join(config.diretorio_dados, 'com_textos.xlsx'))

    # Filtra apenas as entidades do tipo ORGANIZAÇÃO e enriquece com nomes de empresas/CNPJs candidatos na base da
    # Receita Federal
    identificar_possiveis_empresas_citadas(os.path.join(config.diretorio_dados, 'ner.xlsx'),
                                           filtrar_por_empresas_unicas=True)