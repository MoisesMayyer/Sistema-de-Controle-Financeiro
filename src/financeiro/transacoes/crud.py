from dados.dados import (
    salvar_json,
    carregar_json,
    CAMINHO_TRANSACOES,
    CAMINHO_CATEGORIAS
    )

"""from financeiro.categorias.crud import (
    obter_todas_categorias,
    escolher_categoria,
    )"""

from utils.id import criar_id


def obter_transacoes():
    return carregar_json(CAMINHO_TRANSACOES)


def buscar_transacao(id_buscar: int):
    lista_transacoes = obter_transacoes()

    for transacao in lista_transacoes:
        if transacao["id"] == id_buscar:
            return transacao

    return None


def adicionar_transacao(descricao: str,valor:float, tipo: str, data: str):

    lista_transacoes = obter_transacoes()

    transacao = {
        "id": criar_id(lista_transacoes),
        "descricao": descricao,
        "valor": valor,
        "tipo": tipo,
        "categoria_id": None,
        "data": data
    }

    lista_transacoes.append(transacao)

    salvar_json(
        CAMINHO_TRANSACOES,
        lista_transacoes
    )
    return


def editar_transacao(id_editar: int, nova_descricao: str, valor: float, tipo_transacao: str, data_nova: str) -> bool:

    lista_transacoes = obter_transacoes()
    #categorias = obter_todas_categorias()

    if not lista_transacoes:
        return False

    for transacao in lista_transacoes:

        if transacao["id"] == id_editar:
            transacao["descricao"] = nova_descricao
            transacao["valor"] = valor
            transacao["tipo"] = tipo_transacao
            transacao["categoria_id"] = None
            transacao["data"] = data_nova

            salvar_json(CAMINHO_TRANSACOES, lista_transacoes)

            return True

    return False


def remover_transacao(id_remover: int) -> bool:

    lista_transacoes = obter_transacoes()

    if not lista_transacoes:
        return False

    for transacao in lista_transacoes:

        if transacao["id"] == id_remover:
            lista_transacoes.remove(transacao)

            salvar_json(CAMINHO_TRANSACOES,lista_transacoes)
            return True

    return False


def buscar_nome_categoria(categoria_id):

    lista_categorias = carregar_json(CAMINHO_CATEGORIAS)

    for categoria in lista_categorias:
        if categoria["id"] == categoria_id:
            return categoria["nome"]

    return "Sem categoria"