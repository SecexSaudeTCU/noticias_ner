import json
from abc import ABC, abstractmethod

import requests

from noticias_ner import config


class RepositorioCNPJ(ABC):
    @abstractmethod
    def buscar_empresas_por_razao_social(self, razao_social):
        pass

class RepositorioCNPJAberto(RepositorioCNPJ):
    def buscar_empresas_por_razao_social(self, razao_social):
        resultado = json.loads(requests.get(config.url_api_cnpj + razao_social).content)
        map_empresa_to_cnpjs = resultado['dados']['empresas']
        tipo_busca = resultado['dados']['tipo_busca']
        return map_empresa_to_cnpjs, tipo_busca