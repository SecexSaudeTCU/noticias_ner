import os
import re

from noticias_ner import config
from noticias_ner.ner.bert.bert_ner import FinedTunedBERT_NER
from noticias_ner.util.conversor_txt import converter_para_txt


def parse_oficio(arquivo, ner=FinedTunedBERT_NER()):
    caminho = str(arquivo)
    print('Executando o parsing do arquivo ' + caminho)
    nome_arquivo = caminho[caminho.rfind(os.sep):]
    texto = open(caminho, 'r', encoding='utf-8').read()
    regex_cpf_cnpj = r'([0-9]{2}[\.]?[0-9]{3}[\.]?[0-9]{3}[\/]?[0-9]{4}[-]?[0-9]{2})|' \
                     r'([0-9]{3}[\.]?[0-9]{3}[\.]?[0-9]{3}[-]?[0-9]{2})'
    texto = __remover_assinatura(texto)
    texto = __remover_mencao_ministros(texto)

    if 'Citação' in nome_arquivo:
        responsaveis, cpfs, cnpjs, irregularidades = __parse(ner, regex_cpf_cnpj,
                                                             [r'O débito é decorrente d[e|o|a|os|as](.*?):'], texto)
    elif 'Oitiva' in nome_arquivo:
        responsaveis, cpfs, cnpjs, irregularidades = __parse(ner, regex_cpf_cnpj,
                                                             [r'ocorrência\(s\) descrita\(s\) a seguir:(.*?)\.\n'],
                                                             texto)

    return responsaveis, cpfs, cnpjs, irregularidades.strip()


def __remover_assinatura(texto):
    regex_assinatura = r'(Atenciosamente|Respeitosamente)(.*?)$'
    ocorrencias = re.findall(regex_assinatura, texto, flags=re.DOTALL)
    if len(ocorrencias) > 0:
        ocorrencia = ocorrencias[0]
        if len(ocorrencia[0]) > len(ocorrencia[1]):
            ocorrencia = ocorrencia[0]
        else:
            ocorrencia = ocorrencia[1]
        texto = texto.replace(ocorrencia, '')
    return texto


def __remover_mencao_ministros(texto):
    # Remove parágrafo que faz menção ao nome do ministro/relator, para evitar que o NER recupere como entidade
    regexes = [r'Conforme Despacho d[o|a] Presidente, Ministr[o|a](.*?)\.\n',
               r'Conforme Despacho d[o|a] Relator(a), Ministr[o|a](.*?)\.\n',
               r'Conforme delegação de competência conferida pel[o|a] Relator[a]?(.*?)\.\n']
    for regex in regexes:
        ocorrencias = re.findall(regex, texto, flags=re.DOTALL)
        if len(ocorrencias) > 0:
            texto = texto.replace(ocorrencias[0], '')
            return texto
    return texto


def __parse(ner, regex_cpf_cnpj, regexes_irregularidades, texto):
    # Extrai o nome da pessoa física ou jurídica por meio do NER
    entidades_texto = ner._extrair_entidades_de_texto(texto)
    responsaveis = set([entidade for entidade, tipo_entidade in entidades_texto if
                        tipo_entidade in ['PESSOA', 'ORGANIZAÇÃO']])
    cpfs_cnpjs = re.findall(regex_cpf_cnpj, texto, flags=re.DOTALL)
    cpfs = set([cpf for _, cpf in cpfs_cnpjs if len(cpf.strip()) > 0])
    cnpjs = set([cnpj for cnpj, _ in cpfs_cnpjs if len(cnpj.strip()) > 0])
    irregularidades = __parse_irregularidades(regexes_irregularidades, texto)
    return responsaveis, cpfs, cnpjs, irregularidades


def __parse_irregularidades(regexes_irregularidades, texto):
    for regex in regexes_irregularidades:
        ocorrencias = re.findall(regex, texto, flags=re.DOTALL)
        if len(ocorrencias) > 0:
            irregularidades = ocorrencias[0]

            if isinstance(irregularidades, tuple):
                irregularidades = irregularidades[0]
    return irregularidades


if __name__ == '__main__':
    diretorio = config.diretorio_dados.joinpath('pnae')
    diretorio_txt = diretorio.joinpath('txt')

    for root, subdirs, files in os.walk(diretorio):
        for file in files:
            if ('.pdf' in file or '.docx' in file or '.doc' in file or '.rtf' in file) and \
                    not '~$' in file and not 'Modelo' in file:
                converter_para_txt(os.path.join(root, file), diretorio_txt)
        else:
            print('Formato não suportado: ' + file)

    for root, subdirs, files in os.walk(diretorio_txt):
        for file in files:
            print(parse_oficio(arquivo=diretorio_txt.joinpath(file)))
