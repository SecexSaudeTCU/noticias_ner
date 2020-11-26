from cnpjutil.cnpj.repositorio import RepositorioCNPJAberto

from noticias_ner import config


class RepositorioCNPJPersistente(RepositorioCNPJAberto):

    def persistir_informacoes(self, df):
        df.to_excel(config.arquivo_gerado_final)
