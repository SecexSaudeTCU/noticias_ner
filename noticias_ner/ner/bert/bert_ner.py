from abc import abstractmethod

from pandas.io.common import stringify_path
from transformers import pipeline, BertForTokenClassification, DistilBertTokenizerFast

from noticias_ner import config
from noticias_ner.ner.bert.bert_utils import pre_processar_texto
from noticias_ner.ner.ner_base import NER


class BaseBERT_NER(NER):
    def __init__(self, model):
        """
        Inicializa com um modelo passado como parâmetro.  Utiliza o tokenizador para língua portuguesa
        neuralmind/bert-base-portuguese-cased.
        """
        super().__init__()
        self.tokenizer = DistilBertTokenizerFast.from_pretrained('neuralmind/bert-base-portuguese-cased'
                                                                 , model_max_length=512
                                                                 , do_lower_case=False
                                                                 )
        self.nlp = pipeline('ner', model=model, tokenizer=self.tokenizer, grouped_entities=True)

    def _extrair_entidades_de_texto(self, texto, margem=100):
        if texto.strip() != '':
            # Respeitando o tamanho máximo de sequência para o qual o modelo foi originalmente treinado, quebra em
            # diferentes documentos quanto forem necessários.
            tokens = self.nlp.tokenizer.encode(texto)
            max_len = self.nlp.tokenizer.max_len
            max_len -= self.nlp.tokenizer.num_special_tokens_to_add()

            if len(tokens) > max_len:
                textos = pre_processar_texto(texto, self.nlp.tokenizer, max_len, margem)
                retornos = []

                for subtexto in textos:
                    resultado, _ = self._extrair_entidades_originais(subtexto)
                    retornos += self._pos_processar(resultado, subtexto)

                return retornos
            else:
                resultado, ids = self._extrair_entidades_originais(texto)
                return self._pos_processar(resultado, texto)
        else:
            return []

    def _extrair_entidades_originais(self, texto):
        resultado = self.nlp(texto)

        # Recupera a lista de tokens (aqui, subwords)
        palavras = texto.split()
        ids = [self.nlp.tokenizer.encode(palavra) for palavra in palavras]

        return resultado, ids

    @abstractmethod
    def _pos_processar(self, resultado, texto):
        pass


class FinedTunedBERT_NER(BaseBERT_NER):
    def __init__(self):
        """
        Inicializa o modelo treinado para a tarefa específicas (extração dos tipos de entidades estabelecidos para
        textos de notícias).
        Utiliza o tokenizador para língua portuguesa neuralmind/bert-base-portuguese-cased.
        """
        super().__init__(
            BertForTokenClassification.from_pretrained(stringify_path(config.diretorio_modelo_bert_finetuned)))

    def _get_map_labels(self):
        # Aqui, o mapeamento aplica-ser tanto à codificação BILO como aos nomes dos tipos das entidades já agrupados
        # (opção "grouped_entities")
        return {'B-ORG': 'ORGANIZAÇÃO', 'I-ORG': 'ORGANIZAÇÃO', 'L-ORG': 'ORGANIZAÇÃO', 'B-PESSOA': 'PESSOA',
                'I-PESSOA': 'PESSOA', 'L-PESSOA': 'PESSOA', 'B-PUB': 'INSTITUIÇÃO PÚBLICA',
                'I-PUB': 'INSTITUIÇÃO PÚBLICA', 'L-PUB': 'INSTITUIÇÃO PÚBLICA', 'B-LOC': 'LOCAL', 'I-LOC': 'LOCAL',
                'L-LOC': 'LOCAL', 'ORG': 'ORGANIZAÇÃO', 'PESSOA': 'PESSOA', 'PUB': 'INSTITUIÇÃO PÚBLICA',
                'LOC': 'LOCAL'}

    def _pos_processar(self, resultado, texto):
        retorno = []

        for dicionario in resultado:
            tipo_entidade = dicionario['entity_group']
            entidade = dicionario['word']

            if '##' in entidade:
                # Agrupa com a entidade anterior, caso a string esteja presente no texto, utilizando o critério de
                # considerar apenas a classificação do primeiro subtoken.
                if len(retorno) > 0:
                    entidade_anterior, tipo_entidade_anterior = retorno[-1]
                    entidade_completa = entidade_anterior + entidade.replace('##', '')

                    if entidade_completa in texto:
                        retorno.pop()
                        retorno.append((entidade_completa, tipo_entidade_anterior))
            else:
                retorno.append((entidade, self._get_map_labels()[tipo_entidade]))

        return retorno
