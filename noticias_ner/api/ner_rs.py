import json
import os
from collections import defaultdict

from flask import Flask, flash, request, redirect
from werkzeug.utils import secure_filename

from noticias_ner import config
from noticias_ner.cnpj.fabrica_provedor_cnpj import get_repositorio_cnpj
from noticias_ner.cnpj.identificacao_cnpjs import adicionar_aos_resultados
from noticias_ner.ner.bert.bert_ner import FinedTunedBERT_NER
from noticias_ner.util.conversor_txt import converter_para_txt

ner = FinedTunedBERT_NER()
app = Flask("app_name")

UPLOAD_FOLDER = config.diretorio_dados.joinpath('upload')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx', 'rtf'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route("/ner/entidades-texto", methods=['POST'])
def extrair_entidades_de_texto():
    dados = request.json
    texto = dados['texto']
    return __extrair_entidades(texto)


@app.route('/ner/entidades-arquivo', methods=['GET', 'POST'])
def extrair_entidades_de_arquivo():
    if request.method == 'POST':
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
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        caminho_arquivo = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(caminho_arquivo)
    return caminho_arquivo, filename


def __extrair_entidades(texto):
    if 'tipos' in request.args:
        tipos = request.args['tipos']
        lista_tipos = tipos.split(',')
    else:
        lista_tipos = list(set(ner._get_map_labels().values()))
    entidades = ner._extrair_entidades_de_texto(texto)
    retorno = defaultdict(list)

    for ent, tipo in entidades:
        if tipo and tipo in lista_tipos and len(ent.strip()) > 0:
            retorno[tipo].append(ent)

    if 'buscar-cnpj' in request.args:
        buscar_cnpj = request.args['buscar-cnpj']

        if buscar_cnpj == 'S':
            repositorio_cnpj = get_repositorio_cnpj()
            resultado_analise = dict()
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

    return json.dumps({'entidades': retorno}, ensure_ascii=False).encode('utf-8')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
