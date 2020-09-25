from abc import ABC, abstractmethod

from noticias_ner import config
from noticias_ner.cnpj.api_lucene import buscar_em_api_lucene


class RepositorioCNPJ(ABC):
    @abstractmethod
    def buscar_empresas_por_razao_social(self, razao_social):
        pass

class RepositorioCNPJAberto(RepositorioCNPJ):
    def buscar_empresas_por_razao_social(self, razao_social):
        return buscar_em_api_lucene(razao_social, config.url_api_cnpj_aberta)

