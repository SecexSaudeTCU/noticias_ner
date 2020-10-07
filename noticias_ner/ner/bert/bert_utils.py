import re


# Code is partially inspired by https://huggingface.co/transformers/master/custom_datasets.html

def pre_processar_tokens(tokens, tags, tokenizer, max_len):
    """
    Pré-processa uma sequência de tokens, quebrando conjuntos com quantidade de tokens superior a um limite especificado
    em conjuntos de sequências menores.

    :param tokens A sequência original de tokens.
    :param tags A sequência de tags atribuídas à sequência de tokens (previamente definidas de forma supervisionada).
    :param tokenizer O tokenizador em uso.  Será usado para contabilizar os tokens a serem gerados pelo tonkenizador,
    uma vez que essa quantidade pode superar o limite pré-estabelecido pelo modelo a ser treinado.
    :param max_len O limite máximo de tokens estabelecido pelo modelo a ser treinado/utilizado.
    :return As subsequências de tokens e tags obtidos pela quebra, na forma de uma tupla de listas
    (token_docs, tag_docs).
    """
    subword_len_counter = 0
    indices_sublistas = [0]
    token_docs = []
    tag_docs = []

    for i, token in enumerate(tokens):
        current_subwords_len = len(tokenizer.tokenize(token))

        # Filtra caracteres especiais
        if current_subwords_len == 0:
            continue

        if (subword_len_counter + current_subwords_len) >= max_len:
            indices_sublistas.append(i)
            subword_len_counter = current_subwords_len
        else:
            subword_len_counter += current_subwords_len

    for i in range(0, len(indices_sublistas)):
        if i + 1 < len(indices_sublistas):
            token_docs.append(tokens[indices_sublistas[i]:indices_sublistas[i + 1]])
            tag_docs.append(tags[indices_sublistas[i]:indices_sublistas[i + 1]])
        else:
            token_docs.append(tokens[indices_sublistas[i]:])
            tag_docs.append(tags[indices_sublistas[i]:])

    return token_docs, tag_docs


def pre_processar_texto(texto, tokenizer, max_len, margem=100):
    """
    Pré-processa um texto, quebrando textos com quantidade de tokens superior a um limite especificado
    em conjuntos de textos menores.

    :param texto O texto original.
    :param tokenizer O tokenizador em uso.  Será usado para contabilizar os tokens a serem gerados pelo tonkenizador,
    uma vez que essa quantidade pode superar o limite pré-estabelecido pelo modelo a ser treinado.
    :param max_len O limite máximo de tokens estabelecido pelo modelo a ser treinado/utilizado.
    :return A lista de subtextos obtidos pela quebra.
    """
    subword_len_counter = 0
    indices_sublistas = [0]
    docs = []
    tokens = re.findall(r"[\w']+|[-.,!?;()/]", texto)
    inicio = 0

    # Aparantemente, o tokenizador está com um comportamento não determinístico que faz com que mesmo quebranto textos
    # que tenham uma quantidade de tokens além do suportado, ainda assim os subtextos resultantes tenham mais de max_len
    # tokens.  Assim, estou adicionando uma margem de segurança.
    max_len -= margem

    for token in tokens:
        current_subwords_len = len(tokenizer.tokenize(token))
        # Salva a posição do token atual no texto
        posicao_token_no_texto = texto.find(token, inicio)
        inicio = posicao_token_no_texto + len(token)

        # Filtra caracteres especiais
        if current_subwords_len == 0:
            continue

        if (subword_len_counter + current_subwords_len) >= max_len:
            indices_sublistas.append(posicao_token_no_texto)
            subword_len_counter = current_subwords_len
        else:
            subword_len_counter += current_subwords_len

    for posicao_token_no_texto in range(0, len(indices_sublistas)):
        if posicao_token_no_texto + 1 < len(indices_sublistas):
            novo_texto = texto[indices_sublistas[posicao_token_no_texto]:indices_sublistas[posicao_token_no_texto + 1]]
            assert len(tokenizer.tokenize(novo_texto)) < (max_len + margem)
            docs.append(novo_texto)
        else:
            novo_texto = texto[indices_sublistas[posicao_token_no_texto]:]
            assert len(tokenizer.tokenize(novo_texto)) < (max_len + margem)
            docs.append(novo_texto)

    return docs
