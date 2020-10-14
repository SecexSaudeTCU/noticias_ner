import os
import re
import pandas as pd
from noticias_ner import config


def buscar_constatacoes(file):
    arquivo = open(os.path.join(root, file), 'r', encoding='utf-8')
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
                            r'CONCLUSÃO \n(.*?)$', r'Detalhamento das Constatações da Fiscalização(.*?)',
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

    linha_df = []

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


diretorio_pdf = config.diretorio_dados.joinpath('relatorios_cgu', 'txt')

for root, subdirs, files in os.walk(diretorio_pdf):
    linhas_df = []

    for file in files:
        linha_df = buscar_constatacoes(file)
        if len(linha_df) == 4:
            linhas_df.append(linha_df)

    df = pd.DataFrame(linhas_df, columns=['ARQUIVO', 'RESUMO DAS CONSTAÇÕES', 'CONSTATAÇÕES', 'EXPRESSÃO REGULAR'])
    df.to_excel('constatacoes.xlsx')
