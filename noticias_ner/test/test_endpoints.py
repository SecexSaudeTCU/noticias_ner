import requests


def test_tipos_entidade(api_v1_host):
    endpoint = api_v1_host + '/tipos-entidade'
    response = requests.get(endpoint)
    assert response.status_code == 200
    json = response.json()
    assert 'ORGANIZAÇÃO' in json
    assert 'LOCAL' in json
    assert 'INSTITUIÇÃO PÚBLICA' in json
    assert 'PESSOA' in json
    assert len(json) == 4


def test_entidades_texto(api_v1_host):
    endpoint = api_v1_host + '/entidades-texto'
    payload = 'Em 7 de novembro, por iniciativa do então Ministro da Fazenda, Rui Barbosa, o Decreto nº 966-A criou o ' \
              'Tribunal de Contas da União, norteado pelos princípios da autonomia, fiscalização, julgamento, ' \
              'vigilância e energia.  A primeira constituição republicana institucionalizou o Tribunal de Contas da ' \
              'União e conferiu-lhe competências para liquidar as contas da receita e da despesa e verificar a sua ' \
              'legalidade antes de serem prestadas ao Congresso Nacional.  1893 - A instalação do Tribunal, graças ao ' \
              'empenho do Ministro da Fazenda do governo de Floriano Peixoto, Serzedello Corrêa.  1937 – Nesse ano, o ' \
              'Tribunal de Contas mudou-se para o prédio do Instituto de Previdência e Assistência dos Servidores do ' \
              'Estado (IPASE).  1944 – A sede do Tribunal de Contas mudou-se para o recém-inaugurado Palácio da ' \
              'Fazenda.  1961 - O Ministro Pereira Lira também foi o responsável pelos preparativos para a ' \
              'transferência do Tribunal de Contas para Brasília.'
    response = requests.post(endpoint, data=payload.encode('utf-8'))
    assert response.status_code == 200
    json = response.json()

    assert 'Congresso Nacional' in json['entidades']['INSTITUIÇÃO PÚBLICA']
    assert 'Tribunal de Contas da União' in json['entidades']['INSTITUIÇÃO PÚBLICA']
    assert 'IPASE' in json['entidades']['INSTITUIÇÃO PÚBLICA']
    assert 'Instituto de Previdência e Assistência dos Servidores do Estado' in json['entidades']['INSTITUIÇÃO PÚBLICA']

    assert 'Brasília' in json['entidades']['LOCAL']

    assert 'Rui Barbosa' in json['entidades']['PESSOA']
    assert 'Floriano Peixoto' in json['entidades']['PESSOA']
    assert 'Serzedello Corrêa' in json['entidades']['PESSOA']
    assert 'Pereira Lira' in json['entidades']['PESSOA']

    response = requests.post(endpoint + '?tipos=LOCAL,PESSOA', data=payload.encode('utf-8'))
    assert response.status_code == 200
    json = response.json()

    assert 'Brasília' in json['entidades']['LOCAL']

    assert 'Rui Barbosa' in json['entidades']['PESSOA']
    assert 'Floriano Peixoto' in json['entidades']['PESSOA']
    assert 'Serzedello Corrêa' in json['entidades']['PESSOA']
    assert 'Pereira Lira' in json['entidades']['PESSOA']

    assert len(json['entidades']) == 2


def test_entidades_arquivo(api_v1_host):
    endpoint = api_v1_host + '/entidades-arquivo'
    files = {'arquivo': open('arquivo.pdf', 'rb')}
    response = requests.post(endpoint, files=files)
    assert response.status_code == 200
    json = response.json()

    assert 'Ministério da Transparência' in json['entidades']['INSTITUIÇÃO PÚBLICA']
    assert 'RR' in json['entidades']['LOCAL']
    assert 'Boa Vista' in json['entidades']['LOCAL']

    endpoint = api_v1_host + '/entidades-arquivo?buscar-cnpj=S'
    files = {'arquivo': open('arquivo.docx', 'rb')}
    response = requests.post(endpoint, files=files)
    assert response.status_code == 200
    json = response.json()

    organizacoes = json['entidades']['ORGANIZAÇÃO']
    entidades_org = [org for org in organizacoes]
    assert 'Eletrosul Centrais Elétricas S . A' in entidades_org
    assert organizacoes['Eletrosul Centrais Elétricas S . A']['razao-social'] == 'ELETROSUL CENTRAIS ELETRICAS S/A'
    assert organizacoes['Eletrosul Centrais Elétricas S . A']['cnpj'] == '00073957000168'
