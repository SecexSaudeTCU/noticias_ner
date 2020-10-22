import os
import sys

# Adiciona diretorio raiz ao PATH. Devido a ausência de setup.py, isto garante que as importações sempre funcionarão
diretorio_raiz = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
sys.path.append(diretorio_raiz)

from noticias_ner import config
from noticias_ner.noticias.extrator_entidades_noticias_oss import extrair_entidades, obter_textos
from noticias_ner.noticias.identificacao_cnpjs_noticias import identificar_possiveis_empresas_citadas
from noticias_ner.util.mail import enviar_email


def __enviar_email_com_resultados(arquivos, data_inicial):
    diretorio_conteudo_email = config.diretorio_config.joinpath("mail")
    text = open(diretorio_conteudo_email.joinpath("conteudo.txt"), "r", encoding='utf8').read()
    dia = data_inicial.day
    mes = data_inicial.month
    ano = data_inicial.year
    data_formatada = f'{dia}/{mes}/{ano}'
    text = text.replace('{data_inicial}', data_formatada)
    html = open(diretorio_conteudo_email.joinpath("conteudo.html"), "r", encoding='utf8').read()
    html = html.replace('{data_inicial}', data_formatada)
    enviar_email(arquivos, "[RISKDATA] Relação de organizações privadas citadas em notícias da mídia",
                 text, html)


if __name__ == '__main__':
    # Obtém os textos das notícias
    #arquivo_saida = obter_textos(os.path.join(config.diretorio_dados, 'oss', 'Noticias_OSS.xlsx'))

    # Executa a extração de entidades
    #arquivo_entidades = extrair_entidades(arquivo_saida)
    arquivo_entidades = extrair_entidades(os.path.join(config.diretorio_dados, 'oss', 'com_textos.xlsx'))

    # Filtra apenas as entidades do tipo ORGANIZAÇÃO e enriquece com nomes de empresas/CNPJs candidatos na base da
    # Receita Federal
    arquivo_final = identificar_possiveis_empresas_citadas(os.path.join(config.diretorio_dados, 'oss', 'ner.xlsx'),
                                                           filtrar_por_empresas_unicas=True)
