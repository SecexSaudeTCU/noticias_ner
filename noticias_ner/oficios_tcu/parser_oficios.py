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
    regex_cpf_cnpj = r'([0-9]{2}[\.]?[0-9]{3}[\.]?[0-9]{3}[\/]?[0-9]{4}[-]?[0-9]{2})|([0-9]{3}[\.]?' \
                     r'[0-9]{3}[\.]?[0-9]{3}[-]?[0-9]{2})'

    if 'Citação' in nome_arquivo:
        regexes_enderecamento = [r'Natureza: Citação(.*?)Prezada', r'Natureza: Citação(.*?)Prezado',
                                 r'Natureza: Citação(.*?)Senhora', r'Natureza: Citação(.*?)Senhor',
                                 r'Natureza: Citação(.*?)Senhor(a)',
                                 ]
        for regex in regexes_enderecamento:
            ocorrencias = re.findall(regex, texto, flags=re.DOTALL)
            if len(ocorrencias) > 0:
                enderecamento = ocorrencias[0]

                if isinstance(enderecamento, tuple):
                    enderecamento = enderecamento[0]

                # Extrai o nome da pessoa física ou jurídica por meio do NER
                entidades_texto = ner._extrair_entidades_de_texto(enderecamento)
                for entidade, tipo_entidade in entidades_texto:
                    if tipo_entidade == 'PESSOA':
                        responsavel = entidade
                        # Busca por CPF
                        cpfs = re.findall(regex_cpf_cnpj, enderecamento, flags=re.DOTALL)
                        if len(cpfs) > 0:
                            cpf_cnpj = cpfs[0][1]
                        break
                    elif tipo_entidade == 'ORGANIZAÇÃO':
                        responsavel = entidade

                        # Busca por CNPJ
                        cnpjs = re.findall(regex_cpf_cnpj, enderecamento, flags=re.DOTALL)
                        if len(cnpjs) > 0:
                            cpf_cnpj = cnpjs[0][0]
                        break

                break

        regexes_irregularidades = [r'O débito é decorrente de(.*?):', r'O débito é decorrente do(.*?):',
                                   r'O débito é decorrente da(.*?):', r'O débito é decorrente dos(.*?):',
                                   r'O débito é decorrente das(.*?):']
        for regex in regexes_irregularidades:
            ocorrencias = re.findall(regex, texto, flags=re.DOTALL)
            if len(ocorrencias) > 0:
                irregularidades = ocorrencias[0]

                if isinstance(irregularidades, tuple):
                    irregularidades = irregularidades[0]
    elif 'Oitiva' in nome_arquivo:
        return None

    return responsavel, cpf_cnpj, irregularidades.strip()


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
