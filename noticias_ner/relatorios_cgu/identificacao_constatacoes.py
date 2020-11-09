import os
import re
import pandas as pd
from noticias_ner import config


def buscar_constatacoes(file):
    arquivo = open(file, 'r', encoding='utf-8')
    texto = arquivo.read()
    expressoes_regulares = [r'Principais Fatos Encontrados(.*?)Principais Recomendações',
                            r'Sumário Executivo(.*?)Principais Recomendações',
                            r'CONSOLIDAÇÃO DOS RESULTADOS(.*?)CONCLUSÃO',
                            r'ensejaram tal certificação foram os seguintes:(.*?)Brasília',
                            r'ensejaram tal certificação foram os seguintes:(.*?)PRESIDÊNCIA DA REPÚBLICA',
                            r'FALHA\(s\) MEDIA\(s\)(.*?)FALHA\(s\) MEDIA\(s\)',
                            r'Falhas que resultaram em ressalvas(.*?)$',
                            r'(Irregularidades(.*?)Impropriedades)|(Impropriedades(.*?)PRESIDÊNCIA DA REPÚBLICA)',
                            r'. Conclusão(.*?)Anexo,'r'. Conclusão(.*?)Brasília/DF',
                            r'CONSOLIDAÇÃO DOS RESULTADOS(.*?)RECOMENDAÇÕES',
                            r'RESULTADOS DOS EXAMES(.*?)CONCLUSÃO',
                            r'Consolidação de Resultados(.*?)$',
                            r'Conclusão \n(.*?)$', r'Conclusão\n(.*?)$', r'CONSOLIDAÇÃO DOS RESULTADOS(.*?)CONCLUSÃO',
                            r'CONSOLIDAÇÃO DOS RESULTADOS(.*?)ANEXO',
                            r'RESULTADO DOS EXAMES(.*?)CONCLUSÃO',
                            r'CONCLUSÃO \n(.*?)$', r'Detalhamento das Constatações da Fiscalização(.*?)$',
                            r'Constatações da Fiscalização(.*?)$', r'Constatação(.*?)Constatação', r'Constatação(.*?)$',
                            r'CONSTATAÇÃO(.*?)CONSTATAÇÃO', r'CONSTATAÇÃO(.*?)$',
                            r' seguintes constatações:(.*?)PRESIDÊNCIA DA REPÚBLICA', r'ÁREA(.*):(.*?)ÁREA(.*)',
                            r'OUTRAS SITUAÇÕES DETECTADAS EM CAMPO, QUANTO A ATUAÇÃO DO PODER PUBLICO(.*?)$']
    matches = []
    expressao_escolhida = None

    for regex in expressoes_regulares:
        ocorrencias = re.findall(regex, texto, flags=re.DOTALL)
        if len(ocorrencias) > 0:
            matches += ocorrencias
            expressao_escolhida = regex
            break

    if len(matches) == 0:
        print('Nenhuma das expressões regulares consideradas funcionou para o arquivo ' + file)
        linha_df = [file, '', '', '']
    elif len(matches) == 1:
        linha_df = [file, '', matches[0], expressao_escolhida]
    elif len(matches) == 2:
        linha_df = [file, matches[0], matches[1], expressao_escolhida]
    else:
        linha_df = [file, '', matches, expressao_escolhida]

    return linha_df


#
# diretorio_pdf = config.diretorio_dados.joinpath('pnae', 'txt')
#
# for root, subdirs, files in os.walk(diretorio_pdf):
#     linhas_df = []
#
#     for file in files:
#         linha_df = buscar_constatacoes(file)
#         if len(linha_df) == 4:
#             linhas_df.append(linha_df)
#
#     df = pd.DataFrame(linhas_df, columns=['ARQUIVO', 'RESUMO DAS CONSTATAÇÕES', 'CONSTATAÇÕES', 'EXPRESSÃO REGULAR'])
#     df.to_excel('constatacoes.xlsx')

if __name__ == '__main__':
    df = pd.read_excel(config.diretorio_dados.joinpath('pnae').joinpath(
        'Ações de Controle PNAE achados CGU (adaptado da versão original da CGU) atualizado até 04_11_2020.xlsx'))
    diretorio = config.diretorio_dados.joinpath('pnae', 'txt')
    constatacoes = []
    acoes_de_controle = set()
    titulos = ['Ação de Controle', 'Situação', 'Município', 'Data de Homologação', 'Constatações encontradas']
    linhas = []

    for i, row in df.iterrows():
        acao_de_controle = row['Ação de Controle']
        situacao = row['Situação']
        municipio = row['Município']
        data_homologacao = row['Data de Homologação']

        if acao_de_controle not in acoes_de_controle:
            caminho_arquivo = diretorio.joinpath(f'arquivo_{acao_de_controle}.txt')

            if os.path.exists(caminho_arquivo):
                _, _, matches, _ = buscar_constatacoes(caminho_arquivo)
                linhas.append([acao_de_controle, situacao, municipio, data_homologacao, matches])

        acoes_de_controle.add(acao_de_controle)

    df_gerado = pd.DataFrame(columns=titulos, data=linhas)
    df_gerado.to_excel(config.diretorio_dados.joinpath('pnae').joinpath('constatacoes.xlsx'))
