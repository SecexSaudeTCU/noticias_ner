import time
from os import path

import pandas as pd

from noticias_ner import config
from noticias_ner.ner.ner_base import ExtratorEntidades


class ExtratorEntidadesRelatoriosCGU(ExtratorEntidades):
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
            diretorio = config.diretorio_dados.joinpath('relatorios_cgu').joinpath('ner')
            nome_arquivo = path.join(diretorio, f'ner_{i}.xlsx')

            if not path.exists(nome_arquivo):
                id = df.loc[i, 'ID']
                id_arquivo = df.loc[i, 'ID_ARQUIVO']
                link = df.loc[i, 'LINK']
                titulo = df.loc[i, 'TÍTULO']
                tipo_servico = df.loc[i, 'TIPO DE_SERVIÇO']
                grupo_atividade = df.loc[i, 'GRUPO DE ATIVIDADE']
                linha_acao = df.loc[i, 'LINHA DE AÇÃO']
                avaliacao_politica_publica = df.loc[i, 'AVALIAÇÃO DE POLÍTICA PÚBLICA']
                data_publicacao = df.loc[i, 'PUBLICADO EM']
                localidades = df.loc[i, 'LOCALIDADES']
                trechos = df.loc[i, 'TRECHOS']
                start_time = time.time()

                caminho_arquivo_texto = config.diretorio_dados.joinpath('relatorios_cgu').joinpath('txt').joinpath(
                    f'arquivo_{id}.txt')
                with open(caminho_arquivo_texto, 'r', encoding='utf-8') as arquivo_texto:
                    texto = arquivo_texto.read()
                    print(f'Extraindo entidades texto {i}...')
                    entidades_texto = ner._extrair_entidades_de_texto(texto, margem=350)
                    print("--- %s segundos ---" % (time.time() - start_time))
                    resultado_analise = dict()
                    resultado_analise[(
                        id, id_arquivo, link, titulo, tipo_servico, grupo_atividade, linha_acao,
                        avaliacao_politica_publica,
                        data_publicacao, localidades, trechos)] = entidades_texto

                    df_gerado = pd.concat(
                        {k: pd.DataFrame(v, columns=['ENTIDADE', 'CLASSIFICAÇÃO']) for k, v in
                         resultado_analise.items()})
                    # Salva os resultados intermediários
                    df_gerado.to_excel(nome_arquivo)

            df_final = df_final.append(pd.read_excel(nome_arquivo))

        return df_final


class ExtratorEntidadesConstatacoes(ExtratorEntidades):
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
            diretorio = config.diretorio_dados.joinpath('relatorios_cgu').joinpath('ner').joinpath('constatacoes')
            nome_arquivo = path.join(diretorio, f'ner_{i}.xlsx')

            if not path.exists(nome_arquivo):
                arquivo = df.loc[i, 'ARQUIVO']
                constatacoes = df.loc[i, 'CONSTATAÇÕES']
                start_time = time.time()

                if len(constatacoes.strip()) > 0:
                    print(f'Extraindo entidades texto {i}...')
                    entidades_texto = ner._extrair_entidades_de_texto(constatacoes, margem=350)
                    print("--- %s segundos ---" % (time.time() - start_time))
                    resultado_analise = dict()
                    resultado_analise[(arquivo, constatacoes)] = entidades_texto

                    df_gerado = pd.concat(
                        {k: pd.DataFrame(v, columns=['ENTIDADE', 'CLASSIFICAÇÃO']) for k, v in resultado_analise.items()})

                    # Salva os resultados intermediários
                    df_gerado.to_excel(nome_arquivo)

                    df_final = df_final.append(df_gerado)

        return df_final
