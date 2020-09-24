import configparser
from collections import defaultdict

import pyodbc

from noticias_ner import config
from noticias_ner.cnpj.repositorio import RepositorioCNPJ


class RepositorioCNPJCorporativo(RepositorioCNPJ):
    def buscar_empresas_por_razao_social(self, razao_social):
        dao = DaoRFB_SQLServer()
        empresas = dao.buscar_empresa_por_razao_social(razao_social)
        map_empresas_to_cnpjs = defaultdict(list)

        if len(empresas) > 0:
            tipo_busca = "BUSCA EXATA RFB"
            map_empresas_to_cnpjs = {nome:cnpj for cnpj, nome in empresas}
        else:
            #TODO busca Solr
            pass

        dao.encerrar_conexao()
        return map_empresas_to_cnpjs, tipo_busca


class DaoRFB_SQLServer:
    """
    Classe de acesso a uma base que contém os dados de pessoa jurídica disponibilizados pela Receita Federal do Brasil.
    """

    def __init__(self):
        """
        Construtor da classe.
        """
        cfg = configparser.ConfigParser()
        cfg.read_file(open(config.arquivo_config))
        self.conn = pyodbc.connect(
            'DRIVER={' + cfg.get("bd",
                                 "driver") + '};' + f'SERVER={cfg.get("bd", "server")};'
                                                    f'Database={cfg.get("bd", "database")};UID={cfg.get("bd","uid")};'
                                                    f'PWD={cfg.get("bd","pwd")}')

    def buscar_empresa_por_razao_social(self, nome):
        """
        Busca as empresas que possuam razão social idêntica ao nome passado como parâmetro.

        :param Nome procurado.
        :return As empresas que possuam razão social idêntica ao nome passado como parâmetro.
        """
        c = self.conn.cursor()
        cursor = c.execute(
            "SELECT [num_cnpj], [nome] FROM [BD_RECEITA].[dbo].[CNPJ] WHERE [nome] = ? and [ind_matriz_filial] = ?",
            (nome, 1))
        return cursor.fetchall()

    def encerrar_conexao(self):
        self.conn.close()

