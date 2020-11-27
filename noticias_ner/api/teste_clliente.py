import requests

headers = {
    'accept': 'application/json',
    'Content-Type': 'text/plain',
}
params = (
    ('tipos', 'ORGANIZAÇÃO,INSTITUIÇÃO PÚBLICA,LOCAL,PESSOA'),
    ('buscar-cnpj', 'N'),
)
texto = 'O Tribunal de Contas da União é um órgão público sediado em Brasília, com atribuição de julgamento de contas de' \
        ' gestores que utilizam recursos públicos. Também aprecia as contas do Presidente da República. A empresa ' \
        'SKY LINE teve suas contas julgadas irregulares por má gestão de recurso público.'
r = requests.post('http://localhost:5000/ner/entidades-texto', headers=headers, params=params,
                  data=texto.encode(encoding='utf-8'))
r.json()
