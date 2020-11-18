import os
import sys

# Adiciona diretorio raiz ao PATH. Devido a ausência de setup.py, isto garante que as importações sempre funcionarão
diretorio_raiz = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
sys.path.append(diretorio_raiz)

from noticias_ner.api.app import app

if __name__ == '__main__':
    #app.run()
    app.run(host='0.0.0.0')
