import pathlib

# Define o caminho do diretório onde os dados serão armazenados
diretorio_raiz = pathlib.Path(__file__).parent.parent

diretorio_config = diretorio_raiz.joinpath('config')
arquivo_config = diretorio_config.joinpath('noticias_ner.cfg')
arquivo_config_cnpj = diretorio_config.joinpath('cnpj.cfg')

diretorio_dados = diretorio_raiz.joinpath('dados')
arquivo_gerado_final = diretorio_dados.joinpath('com_empresas.xlsx')

arquivo_noticias_rotulado = diretorio_dados.joinpath('labeled_4_labels.jsonl')
diretorio_raiz_modelos = diretorio_dados.joinpath('modelos')

diretorio_modelo_neuralmind_bert_base = diretorio_raiz_modelos.joinpath('bert-neuralmind').joinpath('base')
subdiretorio_modelo_neuralmind_bert_base = diretorio_modelo_neuralmind_bert_base.joinpath(
    'bert-base-portuguese-cased_pytorch_checkpoint')
vocab_bert_base = diretorio_modelo_neuralmind_bert_base.joinpath('vocab.txt')

diretorio_modelo_neuralmind_bert_large = diretorio_raiz_modelos.joinpath('bert-neuralmind').joinpath('large')
subdiretorio_modelo_neuralmind_bert_large = diretorio_modelo_neuralmind_bert_large.joinpath(
    'bert-large-portuguese-cased_pytorch_checkpoint')
vocab_bert_large = diretorio_modelo_neuralmind_bert_large.joinpath('vocab.txt')

diretorio_modelo_bert_finetuned = diretorio_raiz_modelos.joinpath('bert-neuralmind-finetuned')

# URL para a API/microserviço que encapsula a consulta a dados de CNPJ.  A ideia é que no futuro esta solução possa ser
# substituída, por exemplo, a alguma API do Solr do TCU ou da solução MAPA da STI.
url_api_cnpj_aberta = 'http://localhost:8090/cnpj_util/razao_social?q='
