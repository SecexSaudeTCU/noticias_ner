import configparser
import re
from collections import defaultdict

import pyodbc
import unidecode

from noticias_ner import config
from noticias_ner.cnpj.repositorio import RepositorioCNPJ


class RepositorioCNPJCorporativo(RepositorioCNPJ):
    def buscar_empresas_por_razao_social(self, razao_social):
        dao = DaoRFB_SQLServer()
        descricao = self.processar_descricao_contratado(razao_social)
        empresas = dao.buscar_empresa_por_razao_social(descricao)
        map_empresas_to_cnpjs = defaultdict(list)
        tipo_busca = ''

        if len(empresas) > 0:
            print('Descrição buscada: ' + descricao)
            print('Número de registros retornados = ' + str(len(empresas)))
            tipo_busca = "BUSCA EXATA RFB"

            for cnpj, nome in empresas:
                map_empresas_to_cnpjs[nome].append(cnpj)

            print(map_empresas_to_cnpjs)
        else:
            # TODO busca Solr
            pass

        return map_empresas_to_cnpjs, tipo_busca

    def processar_descricao_contratado(self, descricao):
        descricao = descricao.strip()
        descricao = descricao.upper()

        # Remove espaços extras
        descricao = re.sub(' +', ' ', descricao)

        # Remove acentos
        descricao = unidecode.unidecode(descricao)

        # Remova caracteres especiais
        descricao = descricao.replace('&', '').replace('/', '').replace('-', '').replace('"', '')

        return descricao


class DaoRFB_SQLServer:
    """
    Classe de acesso a uma base que contém os dados de pessoa jurídica disponibilizados pela Receita Federal do Brasil.
    """

    def __init__(self):
        """
        Construtor da classe.
        """
        self.cfg = configparser.ConfigParser()
        self.cfg.read_file(open(config.arquivo_config))

    def __get_conexao(self):
        conn = pyodbc.connect('DRIVER={' + self.cfg.get("bd", "driver") + '};' +
                              f'SERVER={self.cfg.get("bd", "server")};Database={self.cfg.get("bd", "database")};'
                              f'UID={self.cfg.get("bd", "uid")};PWD={self.cfg.get("bd", "pwd")}')
        return conn

    def buscar_empresa_por_razao_social(self, nome):
        """
        Busca as empresas que possuam razão social idêntica ao nome passado como parâmetro.

        :param Nome procurado.
        :return As empresas que possuam razão social idêntica ao nome passado como parâmetro.
        """
        conexao = self.__get_conexao()

        with conexao:
            c = conexao.cursor()
            cursor = c.execute(
                "SELECT [num_cnpj], [nome] FROM [BD_RECEITA].[dbo].[CNPJ] WHERE [nome] = ? and [ind_matriz_filial] = ?",
                (nome, 1))
            resultado = cursor.fetchall()

        return resultado
