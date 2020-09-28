from abc import ABC, abstractmethod

from noticias_ner import config
from noticias_ner.cnpj.api_lucene import buscar_em_api_lucene


class RepositorioCNPJ(ABC):
    @abstractmethod
    def buscar_empresas_por_razao_social(self, razao_social):
        pass

    def persistir_informacoes(self, df):
        df.to_excel(config.arquivo_gerado_final)


class RepositorioCNPJAberto(RepositorioCNPJ):
    def buscar_empresas_por_razao_social(self, razao_social):
        return buscar_em_api_lucene(razao_social, config.url_api_cnpj_aberta)


