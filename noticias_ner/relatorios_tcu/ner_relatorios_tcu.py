import time
from os import path

import pandas as pd

from noticias_ner import config
from noticias_ner.ner.ner_base import ExtratorEntidades


class ExtratorEntidadesRelatoriosTCU(ExtratorEntidades):
    """
    Classe-base para implementações (algoritmos) específicas de reconhecimento de entidades nomeadas (named entity
    recognition - NER).
    """

    def extrair_entidades(self, df, ner):
        """
        Retorna as entidades encontradas nos textos contidos no dataframe passado como parâmetro.

        :param df Dataframe que contém os textos e seus respectivos metadados.
        :return Dataframe preenchido com as entidades encontradas.
        """
        df = df.fillna('N/A')
        df_final = pd.DataFrame()

        for i in range(0, len(df)):
            diretorio = config.diretorio_dados.joinpath('relatorios_tcu').joinpath('ner')
            nome_arquivo = path.join(diretorio, f'ner_{i}.xlsx')

            if not path.exists(nome_arquivo):
                fiscalis = df.loc[i, 'FISCALIS']
                nr_processo = df.loc[i, 'NR_PROCESSO']
                url = df.loc[i, 'URL']
                tipo_peca = df.loc[i, 'TIPO_PECA']
                data_inc = df.loc[i, 'DATA_INCL']
                cod_sisdoc = df.loc[i, 'COD_SISDOC']
                num_versao = df.loc[i, 'NUM_VERSAO']
                arquivo = df.loc[i, 'arquivo']

                if not arquivo == 'N/A':
                    start_time = time.time()

                    arquivo_txt = arquivo[:arquivo.find('.')] + '.txt'
                    caminho_arquivo_texto = config.diretorio_dados.joinpath('relatorios_tcu').joinpath('txt').joinpath(
                        arquivo_txt)
                    with open(caminho_arquivo_texto, 'r', encoding='utf-8') as arquivo_texto:
                        texto = arquivo_texto.read()
                        print(f'Extraindo entidades texto {i}...')
                        entidades_texto = ner._extrair_entidades_de_texto(texto, margem=350)
                        print("--- %s segundos ---" % (time.time() - start_time))
                        resultado_analise = dict()
                        resultado_analise[
                            (fiscalis, nr_processo, url, tipo_peca, data_inc, cod_sisdoc, num_versao)] = entidades_texto

                        df_gerado = pd.concat(
                            {k: pd.DataFrame(v, columns=['ENTIDADE', 'CLASSIFICAÇÃO']) for k, v in
                             resultado_analise.items()})
                        # Salva os resultados intermediários
                        df_gerado.to_excel(nome_arquivo)

            if path.exists(nome_arquivo):
                df_final = df_final.append(pd.read_excel(nome_arquivo))

        return df_final
