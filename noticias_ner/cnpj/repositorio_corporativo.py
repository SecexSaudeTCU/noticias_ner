import json
import os
import re
import sys
from collections import defaultdict

import pyodbc
import requests
import unidecode

# Adiciona diretorio raiz ao PATH. Devido a ausência de setup.py, isto garante que as importações sempre funcionarão
diretorio_raiz = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, os.pardir)
sys.path.append(diretorio_raiz)

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

    def persistir_informacoes(self, df):
        super().persistir_informacoes(df)
        listas_cnpjs = df['POSSÍVEIS CNPJs CITADOS']
        daoTipologias = DaoTipologias()
        daoRFB = DaoRFB_SQLServer()

        for lista_cnpj in listas_cnpjs:
            for cnpj in lista_cnpj:
                empresas_relacionadas = daoRFB.recuperar_empresas_relacionadas(cnpj)

                if not daoTipologias.existe_cadastro_para_cnpj(cnpj):
                    daoTipologias.inserir_cnpj_em_lista_empresas_citadas(cnpj)

                empresas_relacionadas = daoRFB.recuperar_empresas_relacionadas(cnpj)

                for empresa in empresas_relacionadas:
                    if daoTipologias.existe_contratacao_por_estado_ou_municipio(empresa):
                        daoTipologias.inserir_cnpj_em_lista_empresas_relacionadas(empresa)


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

    def recuperar_empresas_relacionadas(self, cnpj):
        """
        Recupera outras empresas em que os sócios/ex-sócios das empresas citadas na mídia também são ou foram sócios.
        :param cnpj:
        :return:
        """
        conexao = self.__get_conexao()

        with conexao:
            c = conexao.cursor()
            cursor = c.execute(
                "SELECT distinct NUM_CNPJ_EMPRESA FROM [BD_RECEITA_HIST].[dbo].[SOCIO] WHERE NUM_CPF IN "
                "(SELECT NUM_CPF FROM [BD_RECEITA_HIST].[dbo].[SOCIO] WHERE NUM_CNPJ_EMPRESA = ?)",
                (cnpj,))
            resultado = cursor.fetchall()

        return resultado


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


class DaoTipologias:
    def __get_conexao(self):
        conn = pyodbc.connect('DRIVER={' + self.cfg.get("bd", "driver") + '};' +
                              f'SERVER={self.cfg.get("bd", "server")};'
                              f'Database={self.cfg.get("bd_tipologias", "database")};'
                              f'UID={self.cfg.get("bd", "uid")};PWD={self.cfg.get("bd", "pwd")}')
        return conn

    def existe_cadastro_para_cnpj(self, cnpj):
        conexao = self.__get_conexao()

        with conexao:
            c = conexao.cursor()
            cursor = c.execute(
                "SELECT * FROM [BDU_SGI].[covidata].[CVDT_FRE04_Resultado] WHERE CNPJ = ?", (cnpj,))
            resultado = cursor.fetchall()
            return len(resultado) > 0

    def existe_contratacao_por_estado_ou_municipio(self, cnpj):
        conexao = self.__get_conexao()

        with conexao:
            c = conexao.cursor()
            cursor = c.execute(
                "SELECT * FROM [BDU_SGI].[covidata].[DADOS_TRATADOS] WHERE CONTRATADO_CNPJ = ?", (cnpj,))
            resultado = cursor.fetchall()
            return len(resultado) > 0

    def inserir_cnpj_em_lista_empresas_citadas(self, cnpj):
        conexao = self.__get_conexao()

        with conexao:
            c = conexao.cursor()
            c.execute(
                "INSERT INTO [BDU_SGI].[covidata].[CVDT_FRE04_Resultado] (TIPOLOGIA, CNPJ, OCORRENCIAS) VALUES(?,?,?)",
                ('CVDT_FRE04', cnpj, 1))
            c.commit()

    def inserir_cnpj_em_lista_empresas_relacionadas(self, cnpj):
        conexao = self.__get_conexao()

        with conexao:
            c = conexao.cursor()
            c.execute(
                "INSERT INTO [BDU_SGI].[covidata].[CVDT_FRE05_Resultado] (TIPOLOGIA, CNPJ, OCORRENCIAS) VALUES(?,?,?)",
                ('CVDT_FRE05', cnpj, 1))
            c.commit()

print('Testando DaoRFB_SQLServer().recuperar_empresas_relacionadas():')
print(DaoRFB_SQLServer().recuperar_empresas_relacionadas('00837999000128'))

print('Testando DaoTipologias().existe_cadastro_para_cnpj():')
print(DaoTipologias().existe_cadastro_para_cnpj('02482618000160'))

print('Testando DaoTipologias().existe_contratacao_por_estado_ou_municipio():')
print(DaoTipologias().existe_contratacao_por_estado_ou_municipio('20416210000172'))