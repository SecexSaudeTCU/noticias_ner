import configparser
import importlib

from noticias_ner import config


def get_repositorio_cnpj():
    cfg = configparser.ConfigParser()
    cfg.read_file(open(config.arquivo_config))
    RepositorioCNPJ = getattr(importlib.import_module(cfg['cnpj']['modulo']), cfg['cnpj']['classe'])
    return RepositorioCNPJ()


def get_dao_busca_textual():
    cfg = configparser.ConfigParser()
    cfg.read_file(open(config.arquivo_config))
    DaoRFB = getattr(importlib.import_module(cfg['busca']['modulo_busca_textual']), cfg['busca']['dao_busca_textual'])
    return DaoRFB()
