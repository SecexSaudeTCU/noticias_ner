import time
from collections import Counter

import pandas as pd

from noticias_ner import config
from noticias_ner.municipios.ibge import get_ufs
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
            print(f'Extraindo entidades texto {i}...')

            caminho_arquivo_texto = config.diretorio_dados.joinpath('relatorios_cgu').joinpath('txt').joinpath(
                f'arquivo_{id}.txt')
            with open(caminho_arquivo_texto, 'r', encoding='utf-8') as arquivo_texto:
                texto = arquivo_texto.read()
                entidades_texto = ner._extrair_entidades_de_texto(texto)
                print("--- %s segundos ---" % (time.time() - start_time))
                resultado_analise = dict()
                resultado_analise[(
                    id, id_arquivo, link, titulo, tipo_servico, grupo_atividade, linha_acao, avaliacao_politica_publica,
                    data_publicacao, localidades, trechos)] = entidades_texto

                df_gerado = pd.concat(
                    {k: pd.DataFrame(v, columns=['ENTIDADE', 'CLASSIFICAÇÃO']) for k, v in resultado_analise.items()})
                # Salva os resultados intermediários
                df_gerado.to_excel(f'ner_{i}.xlsx')

                df_final = df_final.append(df_gerado)

        return df_final

    def __inferir_uf_ocorrencia(self, entidades_texto):
        ufs = get_ufs()
        siglas = set(ufs.values())
        cnt = Counter()

        for entidade, tipo in entidades_texto:
            if tipo == 'LOCAL':
                nome_local = entidade.strip().upper()
                # Pode ser referência a UF
                if len(nome_local) == 2:
                    if nome_local in siglas:
                        cnt[entidade] += 1
                elif nome_local in ufs:
                    cnt[ufs[nome_local]] += 1
                else:
                    estados = self.map_municipios_estados[nome_local]
                    for estado in estados:
                        cnt[estado] += 1

        common = cnt.most_common()
        max = -1

        if len(common) > 0:
            max = common[0][1]

        # Retorna as UFs mais citadas
        ufs = [uf for uf, qtd in common if qtd == max]

        return ufs
