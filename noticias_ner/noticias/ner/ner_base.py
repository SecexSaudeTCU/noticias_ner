from abc import ABC, abstractmethod

from seqeval.metrics import accuracy_score
from seqeval.metrics import classification_report
from seqeval.metrics import f1_score
from seqeval.metrics import precision_score
from seqeval.metrics import recall_score


class ExtratorEntidades(ABC):
    @abstractmethod
    def extrair_entidades(self, df):
        pass


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
