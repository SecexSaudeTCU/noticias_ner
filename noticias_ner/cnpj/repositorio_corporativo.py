import json
import re
from collections import defaultdict

import pyodbc
import requests
import unidecode

from noticias_ner.cnpj import fabrica_provedor_cnpj
from noticias_ner.cnpj.api_lucene import buscar_em_api_lucene
from noticias_ner.cnpj.dao import DaoRFB
from noticias_ner.cnpj.repositorio import RepositorioCNPJ


def processar_descricao_contratado(descricao):
    descricao = descricao.strip()
    descricao = descricao.upper()

    # Remove espaços extras
    descricao = re.sub(' +', ' ', descricao)

    # Remove acentos
    descricao = unidecode.unidecode(descricao)

    # Remova caracteres especiais
    descricao = descricao.replace('&', '').replace('/', '').replace('-', '').replace('"', '')

    return descricao


class RepositorioCNPJCorporativo(RepositorioCNPJ):
    def buscar_empresas_por_razao_social(self, razao_social):
        dao_sql = DaoRFB_SQLServer()
        descricao = processar_descricao_contratado(razao_social)
        empresas, tipo_busca = dao_sql.buscar_empresa_por_razao_social(descricao)
        map_empresas_to_cnpjs = defaultdict(list)

        for cnpj, nome in empresas:
            map_empresas_to_cnpjs[nome].append(cnpj)

        # Caso não tenha encontrado nenhum resultado, utiliza como fallback o índice textual
        if len(empresas) == 0:
            dao_busca_textual = fabrica_provedor_cnpj.get_dao_busca_textual()
            map_empresas_to_cnpjs, tipo_busca = dao_busca_textual.buscar_empresa_por_razao_social(descricao)

        return map_empresas_to_cnpjs, tipo_busca


class DaoRFB_SQLServer(DaoRFB):
    """
    Classe de acesso a uma base que contém os dados de pessoa jurídica disponibilizados pela Receita Federal do Brasil.
    """

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

        tipo_busca = ''

        if len(resultado) > 0:
            tipo_busca = "BUSCA EXATA RFB"

        return resultado, tipo_busca


class DaoRFB_BuscaTextualLucene(DaoRFB):
    def buscar_empresa_por_razao_social(self, nome):
        return buscar_em_api_lucene(nome, self.cfg['busca']['url_busca_lucene'])


class DaoRFB_BuscaTextualCorporativa(DaoRFB):
    def buscar_empresa_por_razao_social(self, nome):
        headers = self.__gerar_cabecalho_autenticacao()

        # Começa pela busca mais exata possível, e à medida que não for encontrando resultados, parte para buscas
        # aproximadas.
        uri = 'url_api_busca_exata'
        resultado = self.__buscar(headers, nome, uri)

        if resultado['quantidadeEncontrada'] > 0:
            tipo_busca = "BUSCA EXATA ÍNDICE"
        else:
            tipo_busca = "BUSCA APROXIMADA ÍNDICE"
            resultado = self.__buscar(headers, nome, 'url_api_busca_parte_nome_exata')

            if resultado['quantidadeEncontrada'] == 0:
                resultado = self.__buscar(headers, nome, 'url_api_busca_parte_nome')

        map_empresas_to_cnpjs = defaultdict(list)
        for documento in (resultado['documentos']):
            map_empresas_to_cnpjs[documento['NOME']].append(documento['CNPJ'])

        if len(map_empresas_to_cnpjs) == 0:
            tipo_busca = ''

        return map_empresas_to_cnpjs, tipo_busca

    def __gerar_cabecalho_autenticacao(self):
        # TODO: Autenticação por meio de API
        token = self.cfg['busca']['token']
        user_fingerprint = self.cfg['busca']['x_ufp']
        headers = {'Authorization': token, 'X-UFP': user_fingerprint}
        return headers

    def __buscar(self, headers, nome, uri):
        url = self.cfg['busca'][uri]
        url = url.replace('{razao_social}', nome)
        response = requests.get(url, headers=headers, verify=False, timeout=60)
        content = response.content
        resultado = json.loads(content)
        return resultado

# resultado = DaoRFB_BuscaTextualCorporativa().buscar_empresa_por_razao_social(
#     processar_descricao_contratado('Buyerbr Serviços e Comércio Exteriror Ltda'))
# print(resultado)
