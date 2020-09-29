import configparser
from abc import ABC, abstractmethod

from noticias_ner import config


class DaoBase(ABC):
    def __init__(self):
        """
        Construtor da classe.
        """
        self.cfg = configparser.ConfigParser(interpolation=None)
        self.cfg.read_file(open(config.arquivo_config))


class DaoRFB(DaoBase):

    @abstractmethod
    def buscar_empresa_por_razao_social(self, nome):
        pass
