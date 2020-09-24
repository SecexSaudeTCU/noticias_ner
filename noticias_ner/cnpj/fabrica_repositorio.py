import configparser
import importlib

from noticias_ner import config


def get_repositorio_cnpj():
    cfg = configparser.ConfigParser()
    cfg.read_file(open(config.arquivo_config))
    RepositorioCNPJ = getattr(importlib.import_module(cfg['cnpj']['modulo']), cfg['cnpj']['classe'])
    return RepositorioCNPJ()