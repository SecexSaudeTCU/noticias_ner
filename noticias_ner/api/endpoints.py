import os
from collections import defaultdict

from cnpjutil.cnpj.fabrica_provedor_cnpj import get_repositorio_cnpj
from flask import jsonify, Response, request, flash, Blueprint
from werkzeug.utils import redirect, secure_filename

from noticias_ner import config
from noticias_ner.cnpj.identificacao_cnpjs import adicionar_aos_resultados
from noticias_ner.ner.bert.bert_ner import FinedTunedBERT_NER
from noticias_ner.util.conversor_txt import converter_para_txt

ner = FinedTunedBERT_NER()
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx', 'rtf'}

ner_api = Blueprint('ner_api', __name__)

@ner_api.route("/ner/tipos-entidade", methods=['GET'])
def recuperar_tipos_entidade():
    """
    Retorna os tipos de entidade suportados pelo modelo.
    ---
    responses:
        200:
            description: Os tipos de entidade suportados pelo modelo.
    """
    json_response = jsonify(__get_tipos_entidade_suportados()).data
    return Response(json_response, content_type="application/json; charset=utf-8")


@ner_api.route("/ner/entidades-texto", methods=['POST'])
def extrair_entidades_de_texto():
    """
    Extrai entidades a partir de um texto.
    ---
    consumes: ['text/plain']
    parameters:
        - name: texto
          in: body
          type: string
          required: true
          description: O texto a ser processado.
        - name: tipos
          in: query
          type: string
          description: A lista de tipos de entidades a serem retornados, separados por vírgulas.
        - name: buscar-cnpj
          in: query
          type: string
          description: Igual a S caso os CNPJs das entidades do tipo ORGANIZAÇÃO devam ser buscados.  Caso contrário,
                       igual a N (ou parâmetro omitido).
    responses:
        200:
            description: A lista de entidades encontradas, com os textos e respectivas classificações e, a depender dos
                         parâmetros especificados, CNPJ e razão social para entidades do tipo ORGANIZAÇÃO.
    """
    texto = request.data.decode("utf-8")
    return __extrair_entidades(texto)


@ner_api.route('/ner/entidades-arquivo', methods=['POST'])
def extrair_entidades_de_arquivo():
    """
        Extrai entidades a partir de um arquivo.
        ---
        consumes: ['text/plain']
        parameters:
            - name: arquivo
              in: formData
              type: file
              required: true
              description: Arquivo contendo o texto a ser processado.  Suporta arquivos TXT, PDF, DOCX, DOC ou RTF.
            - name: tipos
              in: query
              type: string
              description: A lista de tipos de entidades a serem retornados, separados por vírgulas.
            - name: buscar-cnpj
              in: query
              type: string
              description: Igual a S caso os CNPJs das entidades do tipo ORGANIZAÇÃO devam ser buscados.  Caso contrário,
                           igual a N (ou parâmetro omitido).
        responses:
            200:
                description: A lista de entidades encontradas, com os textos e respectivas classificações e, a depender dos
                             parâmetros especificados, CNPJ e razão social para entidades do tipo ORGANIZAÇÃO.
        """
    # check if the post request has the file part
    if 'arquivo' not in request.files:
        flash('Nenhum arquivo enviado.')
        return redirect(request.url)
    file = request.files['arquivo']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        flash('Nenhum arquivo selecionado.')
        return redirect(request.url)

    caminho_arquivo, filename = __processar_arquivo(file)

    texto = None

    if '.txt' in filename:
        with open(caminho_arquivo, encoding='utf-8') as arquivo:
            texto = arquivo.read()
    elif '.pdf' in filename or '.docx' in filename or '.doc' in filename or '.rtf' in filename:
        # Converte para texto
        texto = converter_para_txt(caminho_arquivo)

    if texto:
        return __extrair_entidades(texto)

    return None


def __processar_arquivo(file):
    if file and __allowed_file(file.filename):
        filename = secure_filename(file.filename)
        caminho_arquivo = os.path.join(config.diretorio_dados.joinpath('upload'), filename)
        file.save(caminho_arquivo)
    return caminho_arquivo, filename


def __extrair_entidades(texto):
    lista_tipos = __get_lista_tipos()

    entidades = ner._extrair_entidades_de_texto(texto)

    # Utiliza set para que não haja repetição de entidades do mesmo tipo.
    retorno = defaultdict(set)

    for ent, tipo in entidades:
        if tipo and tipo in lista_tipos and len(ent.strip()) > 0:
            retorno[tipo].add(ent)

    # Converte para lista para permitir a serialização em JSON.
    retorno = {k: list(v) for k, v in retorno.items()}

    if 'buscar-cnpj' in request.args:
        __processar_cnpjs(retorno)

    json_response = jsonify(entidades=retorno).data
    return Response(json_response, content_type="application/json; charset=utf-8")


def __processar_cnpjs(retorno):
    buscar_cnpj = request.args['buscar-cnpj']
    if buscar_cnpj == 'S':
        repositorio_cnpj = get_repositorio_cnpj(str(config.arquivo_config_cnpj))
        resultado_analise = dict()
        if 'ORGANIZAÇÃO' in retorno:
            empresas = retorno['ORGANIZAÇÃO']

            for empresa in empresas:
                adicionar_aos_resultados('ORGANIZAÇÃO', empresa, True, repositorio_cnpj, resultado_analise, ())

            resultado_analise = {k[0]: v for k, v in resultado_analise.items()}

            # Elimina os nomes de empresa repetidos.
            retorno['ORGANIZAÇÃO'] = set(retorno['ORGANIZAÇÃO'])

            # Cria uma nova estrutura de dados para abrigar os metadados de cada organização cujo CNPJ foi encontrado.
            organizacoes = dict()
            for empresa in retorno['ORGANIZAÇÃO']:
                if empresa in resultado_analise:
                    organizacoes[empresa] = {'razao-social': resultado_analise[empresa][0][0],
                                             'cnpj': resultado_analise[empresa][0][1][0]}

            retorno['ORGANIZAÇÃO'] = organizacoes


def __get_lista_tipos():
    if 'tipos' in request.args:
        tipos = request.args['tipos']
        lista_tipos = tipos.split(',')
    else:
        lista_tipos = __get_tipos_entidade_suportados()
    return lista_tipos


def __get_tipos_entidade_suportados():
    return list(set(ner._get_map_labels().values()))


def __allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
