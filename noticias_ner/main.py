import configparser
import os
import sys
from datetime import date

from noticias_ner import config
from noticias_ner.noticias.extrator_entidades_noticias import obter_textos, extrair_entidades
from noticias_ner.noticias.identificacao_cnpjs import identificar_possiveis_empresas_citadas
from noticias_ner.util.mail import enviar_email


def __enviar_email_com_resultados(arquivos, data_inicial):
    cfg = configparser.ConfigParser()
    cfg.read_file(open(config.diretorio_config_email.joinpath('mail.cfg')))
    text = open(config.diretorio_config_email.joinpath("conteudo.txt"), "r", encoding='utf8').read()
    dia_inicio = date.fromisoformat(data_inicial)
    dia = dia_inicio.day
    mes = dia_inicio.month
    ano = dia_inicio.year
    data_formatada = f'{dia}/{mes}/{ano}'
    text = text.replace('{data_inicial}', data_formatada)
    html = open(config.diretorio_config_email.joinpath("conteudo.html"), "r", encoding='utf8').read()
    html = html.replace('{data_inicial}', data_formatada)
    enviar_email(arquivos, "[RISKDATA] Relação de organizações privadas citadas em notícias da mídia",
                 text, html)


if __name__ == '__main__':
    data_inicial = None

    if len(sys.argv) == 1:
        print('Exemplo de execução: main.py -t"<texto da consulta>" -d"<data inicial>"')
        exit()

    if len(sys.argv) > 1:
        query = sys.argv[1][2:]

        if len(sys.argv) == 3:
            data_inicial = sys.argv[2][2:]

    # Baixa as notícias da Web
    if data_inicial:
        obter_textos(query, data_inicial)
    else:
        obter_textos(query)

    # Executa a extração de entidades
    arquivo_entidades = extrair_entidades(os.path.join(config.diretorio_dados, 'com_textos.xlsx'))

    # Filtra apenas as entidades do tipo ORGANIZAÇÃO e enriquece com nomes de empresas/CNPJs candidatos na base da
    # Receita Federal
    arquivo_final = identificar_possiveis_empresas_citadas(os.path.join(config.diretorio_dados, 'ner.xlsx'),
                                                           filtrar_por_empresas_unicas=True)
    __enviar_email_com_resultados([arquivo_entidades, arquivo_final], data_inicial)
