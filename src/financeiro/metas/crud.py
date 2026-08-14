from dados.dados import (
    carregar_json,
     CAMINHO_METAS,
     salvar_json
    )

from utils.id import criar_id

def obter_metas():
    return carregar_json(CAMINHO_METAS)


def calcular_porcentagem_meta(valor_atual, valor_meta):
    if valor_meta == 0:
        return 0

    porcentagem = (valor_atual / valor_meta) * 100

    return min(porcentagem, 100)


def adicionar_valor_meta():
    lista_metas = obter_metas()

    try:
        id_meta = int(input("Digite o id da meta: "))

        for meta in lista_metas:
            if id_meta == meta["id"]:
                valor_adicionado = int(
                    input("Digite o valor que deseja depositar na meta: ")
                )

                if valor_adicionado < 0:
                    raise ValueError

                if meta["valor_atual"] + valor_adicionado <= meta["valor_meta"]:
                    meta["valor_atual"] += valor_adicionado

                else:
                    print("O valor adicionado excede o valor da meta.")
                    return

                salvar_json(CAMINHO_METAS, lista_metas)
                print("Valor adicionado com sucesso!")
                return

        print("Meta não encontrada.")

    except ValueError:
        print("Digite um valor válido.")


def adicionar_meta():

    lista_metas = obter_metas()

    while True:
        try:
            nome_meta = input("digite o nome da nova meta: ")

            if nome_meta.strip() == "":
                print("O nome da meta não pode ser vazio.")
                raise ValueError

            valor_meta = int(input("digite o valor da meta: "))

            if valor_meta <= 0:
                print("digite um valor valido")
                raise ValueError

            break

        except ValueError:
            print("Tente novamente")

    metas = {
        "id": criar_id(lista_metas),
        "nome": nome_meta,
        "valor_atual": 0,
        "valor_meta": valor_meta,
    }

    lista_metas.append(metas)

    salvar_json(CAMINHO_METAS,lista_metas)


def editar_meta():

    lista_metas = obter_metas()

    try:
        id_alterar = int(input("Digite o id da meta: "))

        for meta in lista_metas:

            if meta["id"] == id_alterar:

                novo_nome = input("Digite o novo nome: ").strip()

                if novo_nome == "":
                    raise ValueError

                novo_valor = int(input("Digite o novo valor: "))

                if novo_valor <= 0:
                    raise ValueError

                meta["nome"] = novo_nome
                meta["valor_meta"] = novo_valor

                salvar_json(CAMINHO_METAS, lista_metas)

                print("Meta alterada com sucesso!")
                return

        print("Meta não encontrada.")

    except ValueError:
        print("Digite valores válidos.")




def remover_meta():

    lista_metas = obter_metas()

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


