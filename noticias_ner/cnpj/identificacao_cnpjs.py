import pandas as pd


def adicionar_aos_resultados(classificacao, entidade, filtrar_por_empresas_unicas, repositorio_cnpj, resultado_analise,
                             valores):
    if (not pd.isna(entidade)) and classificacao == 'ORGANIZAÇÃO':
        # Desconsidera empresas com nome com menos de 3 caracteres - esses casos têm grande chance de serem
        # falso-positivos indicados pelo NER.
        if len(entidade.strip()) > 2:
            #TODO: Investigar por que o algoritmo está gerando isso...
            entidade = entidade.replace('[UNK]','')
            map_empresa_to_cnpjs, tipo_busca = repositorio_cnpj.buscar_empresas_por_razao_social(entidade)
            qtd = len(map_empresa_to_cnpjs)
            qtd_cnpjs = 0

            if qtd > 0:
                qtd_cnpjs = len(next(iter(map_empresa_to_cnpjs.values())))

            # Só adiciona a empresa ao resultado se ela foi ecnontrada nas bases (base RFB ou índice Lucene RFB) e,
            # caso filtrar_por_empresas_unicas seja igual a True, se sua razão social é única e associda a um único
            # CNPJ, para evitar confusão com empresas diferentes registradas na mesma razão social.  Futuramente,
            # poderão ser implementados modelos que permitam identificar a empresa mais adequada.
            if qtd > 0 and ((not filtrar_por_empresas_unicas) or (
                    filtrar_por_empresas_unicas and qtd == 1 and qtd_cnpjs == 1)):
                resultado_analise[valores + (entidade,)] = [(razao_social, cnpjs, tipo_busca) for razao_social, cnpjs
                                                           in map_empresa_to_cnpjs.items()]


def persistir_informacoes(repositorio_cnpj, resultado_analise):
    if len(resultado_analise) > 0:
        df = pd.concat(
            {k: pd.DataFrame(v, columns=['POSSÍVEIS EMPRESAS CITADAS', 'POSSÍVEIS CNPJs CITADOS', 'TIPO BUSCA']) for
             k, v in
             resultado_analise.items()})
        repositorio_cnpj.persistir_informacoes(df)