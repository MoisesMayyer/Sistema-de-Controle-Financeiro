from dados.dados import salvar_json, carregar_json, CAMINHO_TRANSACOES, CAMINHO_CATEGORIAS
from financeiro.categorias.crud import obter_todas_categorias,escolher_categoria
from utils.utils import criar_id
from financeiro.transaçoes.calculos import total_receitas

lista_transacoes = carregar_json(CAMINHO_TRANSACOES)


def adicionar_transacao():

    categorias = obter_todas_categorias()

    if not categorias:
        print(
            "Nenhuma categoria cadastrada.\n"
            "Volte ao menu de categorias e crie uma antes de adicionar uma transação."
        )
        return


    descricao = input("Digite a descrição: ")

    while True:
        try:
            valor = float(input("Digite o valor: "))
            break

        except ValueError:
            print("Valor inválido. Digite apenas números.")


    while True:
        tipo = input(
            "Digite o tipo (receita/despesa): "
        ).lower()

        if tipo in ["receita", "despesa"]:
            break

        print("Tipo inválido.")


    data = input(
        "Digite a data (dd/mm/aaaa): "
    )


    categoria_id = escolher_categoria(categorias)


    transacao = {
        "id": criar_id(lista_transacoes),
        "descricao": descricao,
        "valor": valor,
        "tipo": tipo,
        "categoria_id": categoria_id,
        "data": data
    }


    lista_transacoes.append(transacao)

    salvar_json(
        CAMINHO_TRANSACOES,
        lista_transacoes
    )

    return "SUCESSO"


def listar_transacoes():
    if not lista_transacoes:
        print("Nenhuma transação registrada.")
        return

    for transacao in lista_transacoes:
        print(
            f"ID: {transacao['id']}\n"
            f"Descrição: {transacao['descricao']}\n"
            f"Valor: R$ {transacao['valor']:.2f}\n"
            f"Tipo: {transacao['tipo']}\n"
            f"Categoria_id: {transacao['categoria_id']}\n"
            f"Data: {transacao['data']}\n"
        )


def editar_transacao():
    if not lista_transacoes:
        print("Nenhuma transação registrada.")
        return

    while True:
        try:
            id_editar = int(input("Digite o ID que deseja editar: "))
            break
        except ValueError:
            print("Digite um valor válido.")

    for transacao in lista_transacoes:
        if transacao["id"] == id_editar:

            transacao["descricao"] = input("Digite a nova descrição: ")

            while True:
                try:
                    transacao["valor"] = float(input("Digite o novo valor: "))
                    break
                except ValueError:
                    print("Valor inválido. Digite apenas números.")

            transacao["tipo"] = input(
                "Digite o novo tipo (receita/despesa): "
            ).lower()

            transacao["categoria_id"] = input("Digite a nova categoria: ")

            transacao["data"] = input(
                "Digite a nova data (dd/mm/aaaa): "
            )

            salvar_json(CAMINHO_TRANSACOES, lista_transacoes)

            print("Transação editada com sucesso!")
            return

    print("Transação não encontrada.")


def remover_transacao():
    if not lista_transacoes:
        print("Nenhuma transação registrada.")
        return

    while True:
        try:
            id_remover = int(input("Digite o ID que deseja remover: "))
            break
        except ValueError:
            print("Digite apenas números.")

    for transacao in lista_transacoes:
        if transacao["id"] == id_remover:
            lista_transacoes.remove(transacao)
            salvar_json(CAMINHO_TRANSACOES,lista_transacoes)

            print("Transação removida com sucesso!")
            return

    print("Transação não encontrada.")


def total_despesas():
    if not lista_transacoes:
        print("Nenhuma transação registrada.")
        return

    total = 0

    for transacao in lista_transacoes:
        if transacao["tipo"] == "despesa":
            total += transacao["valor"]

    print(f"Total de despesas: R$ {total:.2f}")
    print(f"Total de receita: R$ {total_receitas()}")


def buscar_nome_categoria(categoria_id):
    lista_categorias = carregar_json(CAMINHO_CATEGORIAS)

    for categoria in lista_categorias:
        if categoria["id"] == categoria_id:
            return categoria["nome"]

    return "Sem categoria"

