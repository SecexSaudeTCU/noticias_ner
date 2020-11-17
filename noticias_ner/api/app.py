from flasgger import Swagger
from flask import Flask

from noticias_ner.api.endpoints import ner_api

app = Flask(__name__)


def __inicializar_aplicacao():
    app.register_blueprint(ner_api)
    __criar_especificacao_swagger()


def __criar_especificacao_swagger():
    template = {
        "info": {
            "title": "RiskData NER - Extrator de entidades mencionadas em dados textuais",
            "description": "REST web service responsável por expor funcionalidades de extração de entidades em dados "
                           "textuais do RiskData NER.",
            "contact": {
                "responsibleOrganization": "TCU / SecexSaúde / NTDI",
                "responsibleDeveloper": "Monique Monteiro",
                "email": "moniquebm@tcu.gov.br",
            },
            "version": "0.0.1"
        },
    }
    Swagger(app, template=template)


if __name__ == "__main__":
    __inicializar_aplicacao()
    app.run(host='0.0.0.0', debug=True)
