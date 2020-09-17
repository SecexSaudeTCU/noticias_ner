import json
from collections import defaultdict

import requests


def get_ufs():
    """
    Retorna o mapeamento de nomes de estados para siglas.
    """
    # TODO: Reimplementar usando o fallback estados.json.
    estados = dict()
    resultado = json.loads(requests.get('https://servicodados.ibge.gov.br/api/v1/localidades/estados').content)

    for estado in resultado:
        estados[estado['nome'].upper()] = estado['sigla']

    return estados

def get_map_municipios_estados():
    municipios = json.loads(requests.get('https://servicodados.ibge.gov.br/api/v1/localidades/municipios').content)
    resultado = defaultdict(list)

    for municipio in municipios:
        resultado[municipio['nome'].upper()].append(municipio['microrregiao']['mesorregiao']['UF']['sigla'])

    return resultado
