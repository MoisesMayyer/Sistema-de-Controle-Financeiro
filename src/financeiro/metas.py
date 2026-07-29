from dados.dados import carregar_json, CAMINHO_METAS, salvar_json
from utils.utils import criar_id

lista_metas = carregar_json(CAMINHO_METAS)

def calcular_porcentagem_meta(valor_atual, valor_meta):
    if valor_meta == 0:
        return 0

    porcentagem = (valor_atual / valor_meta) * 100

    return min(porcentagem, 100)

def adicionar_valor_meta():

    try:
        id_meta = int(input("Digite o id da meta: "))

        for meta in lista_metas:
            if id_meta == meta["id"]:
                valor_adicionado = int(
                    input("Digite o valor que deseja depositar na meta: ")
                )

                if valor_adicionado < 0:
                    raise ValueError

                meta["valor_atual"] += valor_adicionado

                salvar_json(CAMINHO_METAS, lista_metas)
                print("Valor adicionado com sucesso!")
                return

        print("Meta não encontrada.")

    except ValueError:
        print("Digite um valor válido.")


def adicionar_meta():
    nome_meta = input("digite o nome da nova meta: ")

    while True:
        try:
            valor_meta = int(input("digite o valor da meta: "))
            break
        except ValueError:
            print("digite um valor valido")

    metas = {
        "id": criar_id(lista_metas),
        "nome": nome_meta,
        "valor_atual": 0,
        "valor_meta": valor_meta,
    }

    lista_metas.append(metas)

    salvar_json(CAMINHO_METAS,lista_metas)


def editar_meta():
    id_alterar = int(input("digite o id que deseja alterar: "))
    for meta in lista_metas:
        if meta["id"] == id_alterar:
            meta["nome"] = input("digite o novo nome: ")

            try:
                meta["valor_meta"] = int(input("Digite o novo valor: "))
            except ValueError:
                print("Digite um valor válido.")

            salvar_json(CAMINHO_METAS, lista_metas)


def remover_meta():
    try:
        deletar_id = int(input("digite o id da meta que deseja remover:"))
        for meta in lista_metas:

            if meta["id"] == deletar_id:
                print("meta removida com sucesso!")

                lista_metas.remove(meta)
                salvar_json(CAMINHO_METAS,lista_metas)
                return

    except ValueError:
        print(f"digite um id valido")


