import json

import requests


def buscar_em_api_lucene(razao_social, url):
    resultado = json.loads(requests.get(url + razao_social).content)
    map_empresa_to_cnpjs = resultado['dados']['empresas']
    tipo_busca = resultado['dados']['tipo_busca']
    return map_empresa_to_cnpjs, tipo_busca