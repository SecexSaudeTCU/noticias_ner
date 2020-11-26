from transformers import BertForTokenClassification, DistilBertTokenizerFast, pipeline

# Carrega o modelo a partir de um diretório que só contém os arquivos a serem compartilhados
model = BertForTokenClassification.from_pretrained('monilouise/ner_pt_br')
tokenizer = DistilBertTokenizerFast.from_pretrained('neuralmind/bert-base-portuguese-cased'
                                                    , model_max_length=512
                                                    , do_lower_case=False
                                                    )
nlp1 = pipeline('ner', model=model, tokenizer=tokenizer)
nlp2 = pipeline('ner', model=model, tokenizer=tokenizer, grouped_entities=True)

result = nlp1("O Tribunal de Contas da União é localizado em Brasília e foi fundado por Rui Barbosa.  Fiscaliza contratos, por exemplo com empresas como a Veigamed e a Buyerbr.")
print(result)

result = nlp2("O Tribunal de Contas da União é localizado em Brasília e foi fundado por Rui Barbosa.  Fiscaliza contratos, por exemplo com empresas como a Veigamed e a Buyerbr.")
print(result)
