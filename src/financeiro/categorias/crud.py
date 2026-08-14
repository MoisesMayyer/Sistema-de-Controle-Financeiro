from dados.dados import (
    carregar_json,
    salvar_json,
    CAMINHO_CATEGORIAS,
    CAMINHO_TRANSACOES
)

from utils.id import criar_id


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


def escolher_categoria(categorias: list[dict]) -> int:

    print("\nCategorias disponíveis:")

    for categoria in categorias:
        print(
            f"{categoria['id']} - {categoria['nome']}"
        )

    while True:
        try:
            escolha = int(
                input("\nEscolha uma categoria: ")
            )

            for categoria in categorias:
                if categoria["id"] == escolha:
                    return categoria["id"]

            print("Categoria não encontrada.")

        except ValueError:
            print("Digite apenas números.")


def obter_todas_categorias():
    return carregar_json(CAMINHO_CATEGORIAS)