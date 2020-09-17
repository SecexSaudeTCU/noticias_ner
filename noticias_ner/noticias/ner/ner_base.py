import time
from abc import ABC, abstractmethod
from collections import Counter

import pandas as pd
from seqeval.metrics import accuracy_score
from seqeval.metrics import classification_report
from seqeval.metrics import f1_score
from seqeval.metrics import precision_score
from seqeval.metrics import recall_score

from noticias_ner.municipios.ibge import get_map_municipios_estados, get_ufs


class NER(ABC):
    """
    Classe-base para implementações (algoritmos) específicas de reconhecimento de entidades nomeadas (named entity
    recognition - NER).
    """

    def __init__(self, nome_algoritmo=None):
        """
        Construtor da classe.
        """
        self.__nome_algoritmo = nome_algoritmo
        self.map_municipios_estados = get_map_municipios_estados()

    @abstractmethod
    def _get_map_labels(self):
        """
        Deve retornar um mapeamento (dicionário) de nomes de rótulos (categorias) utilizados pela implementação
        interna (algoritmo/biblioteca) para os nomes de rótulos/categorias visíveis pelo usuário final.
        """
        pass

    def get_nome_algoritmo(self):
        """
        Retorna o nome do algoritmo. Caso não tenha sido especificado na chamada ao construtor da classe, utiliza por
        padrão o nome da classe.
        """
        if self.__nome_algoritmo:
            return self.__nome_algoritmo

        return self.__class__.__name__

    def extrair_entidades(self, df):
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
            entidades_texto = self._extrair_entidades_de_texto(titulo + '. ' + texto)
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

    @abstractmethod
    def _extrair_entidades_de_texto(self, texto):
        """
        Retorna as entidades encontradas em um texto específico.

        :param texto O texto a ser analisado.
        :return As entidades encontradas, como uma lista de tuplas do tipo (termo, categoria), onde termo é a string que
        contém a entidade nomeadas, e categoria é a classificação (tipo de entidade).
        """
        pass

    def avaliar(self):
        """
        Retorna métricas de avaliação do modelo, em forma de string.
        """
        return ''


class Avaliacao():
    def __init__(self, y_true, y_pred):
        self.f1 = f1_score(y_true, y_pred)
        self.acuracia = accuracy_score(y_true, y_pred)
        self.precisao = precision_score(y_true, y_pred)
        self.recall = recall_score(y_true, y_pred)
        self.relatorio_classificacao = classification_report(y_true, y_pred)

    def __str__(self):
        return 'Avaliação a nível de entidades:\n' + f'precisão = {self.precisao}\n' + f'recall = {self.recall}\n' + \
               f'f-1 = {self.f1}\n' + f'acurácia = {self.acuracia}\n' + 'Relatório = \n' + self.relatorio_classificacao
