import time
from collections import Counter

import pandas as pd

from noticias_ner.municipios.ibge import get_map_municipios_estados, get_ufs
from noticias_ner.ner.ner_base import ExtratorEntidades


class ExtratorEntidadesNoticias(ExtratorEntidades):
    """
    Classe-base para implementações (algoritmos) específicas de reconhecimento de entidades nomeadas (named entity
    recognition - NER).
    """

    def __init__(self):
        """
        Construtor da classe.
        """
        self.map_municipios_estados = get_map_municipios_estados()

    def extrair_entidades(self, df, ner):
        """
        Retorna as entidades encontradas nos textos contidos no dataframe passado como parâmetro.

        :param df Dataframe que contém os textos e seus respectivos metadados.
        :return Dataframe preenchido com as entidades encontradas.
        """
        df = df.fillna('N/A')
        resultado_analise = dict()

        for i in range(0, len(df)):
            texto = df.loc[i, 'texto']
            titulo = df.loc[i, 'title']
            midia = df.loc[i, 'media']
            data = df.loc[i, 'date']
            link = df.loc[i, 'link']
            start_time = time.time()
            print(f'Extraindo entidades texto {i}...')
            entidades_texto = ner._extrair_entidades_de_texto(titulo + '. ' + texto)
            print("--- %s segundos ---" % (time.time() - start_time))
            # resultado_analise[(titulo, link, midia, data, texto)] = entidades_texto

            # Utiliza heurística para tentar inferir a UF da ocorrência
            print('Identificando UF da ocorrência...')
            uf_ocorrencia = self.__inferir_uf_ocorrencia(entidades_texto)
            print("--- %s segundos ---" % (time.time() - start_time))

            # Exibe as UFs mais relevantes em formato de string (separadas por vírgula quando houver mais de uma)
            if len(uf_ocorrencia) > 1:
                # Converte em representação de string e remove os colchetes
                uf_ocorrencia = str(uf_ocorrencia)[1:-1].replace('\'', '')
            elif len(uf_ocorrencia) == 1:
                uf_ocorrencia = uf_ocorrencia[0]
            else:
                uf_ocorrencia = 'N/A'

            resultado_analise[(titulo, link, midia, data, texto, uf_ocorrencia)] = entidades_texto

        df = pd.concat(
            {k: pd.DataFrame(v, columns=['ENTIDADE', 'CLASSIFICAÇÃO']) for k, v in resultado_analise.items()})

        return df

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
