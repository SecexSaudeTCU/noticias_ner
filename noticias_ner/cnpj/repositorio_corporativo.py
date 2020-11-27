import pyodbc
from cnpjutil.cnpj.dao import DaoBase
from cnpjutil.cnpj.repositorio_corporativo import RepositorioCNPJCorporativo, \
    DaoRFB_SQLServer

from noticias_ner import config


class RepositorioCNPJCorporativoPersistente(RepositorioCNPJCorporativo):
    def persistir_informacoes(self, df):
        #Primeiramente, salva as informações em arquivo Excel, para em seguida enviar por e-mail
        df.to_excel(config.arquivo_gerado_final)

        listas_cnpjs = df['POSSÍVEIS CNPJs CITADOS']
        daoTipologias = DaoTipologias(str(config.arquivo_config))
        daoRFB = DaoRFB_SQLServer(self.arquivo_configuracoes)

        for lista_cnpj in listas_cnpjs:
            for cnpj in lista_cnpj:
                if not daoTipologias.existe_cadastro_para_cnpj(cnpj):
                    daoTipologias.inserir_cnpj_em_lista_empresas_citadas(cnpj)

                empresas_relacionadas = daoRFB.recuperar_empresas_relacionadas(cnpj)

                for empresa in empresas_relacionadas:
                    cnpj_relacionado = empresa[0]

                    # Se já não estiver na tabela da primeira tipologia
                    if not daoTipologias.existe_cadastro_para_cnpj(
                            cnpj_relacionado) and not daoTipologias.existe_cadastro_para_cnpj_relacionado(
                        cnpj_relacionado):
                        daoTipologias.inserir_cnpj_em_lista_empresas_relacionadas(cnpj_relacionado)


class DaoTipologias(DaoBase):
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

    def existe_cadastro_para_cnpj_relacionado(self, cnpj):
        conexao = self.__get_conexao()

        with conexao:
            c = conexao.cursor()
            cursor = c.execute(
                "SELECT * FROM [BDU_SGI].[covidata].[CVDT_FRE05_Resultado] WHERE CNPJ = ?", (cnpj,))
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
