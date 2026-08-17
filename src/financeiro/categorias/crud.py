from dados.dados import (
    carregar_json,
    salvar_json,
    CAMINHO_CATEGORIAS,
    CAMINHO_TRANSACOES
)

from utils.id import criar_id


def buscar_categoria(id_buscar: int):
    lista_categorias = obter_todas_categorias()

    for categoria in lista_categorias:
        if categoria["id"] == id_buscar:
            return categoria

    return None


def nova_categoria(nome_categoria, limite_categoria):

    categorias_lista = carregar_json(CAMINHO_CATEGORIAS)

    id_categoria = criar_id(categorias_lista)

    categoria_nova = {
        "id": id_categoria,
        "nome": nome_categoria,
        "limite": limite_categoria
    }

    categorias_lista.append(categoria_nova)
    salvar_json(CAMINHO_CATEGORIAS, categorias_lista)

    return True


def editar_categoria(id_alterar, novo_nome, novo_valor):

    categorias_lista = carregar_json(CAMINHO_CATEGORIAS)

    for categoria in categorias_lista:
        if categoria["id"] == id_alterar:
            categoria["nome"] = novo_nome
            categoria["limite"] = novo_valor

            salvar_json(CAMINHO_CATEGORIAS, categorias_lista)

            return True

    return False


def remover_categoria(id_remover):

    categorias_lista = carregar_json(CAMINHO_CATEGORIAS)
    transacoes_lista = carregar_json(CAMINHO_TRANSACOES)

    for categoria in categorias_lista:
        if categoria["id"] == id_remover:

            for transacao in transacoes_lista:
                if transacao["categoria_id"] == id_remover:
                    return False

            categorias_lista.remove(categoria)
            salvar_json(CAMINHO_CATEGORIAS, categorias_lista)

            return True

    return False

def obter_todas_categorias():
    return carregar_json(CAMINHO_CATEGORIAS)