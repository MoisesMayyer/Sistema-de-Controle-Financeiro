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


def adicionar_valor_meta(id_meta, valor_adicionado: float) -> bool:

    lista_metas = obter_metas()

    for meta in lista_metas:

        if id_meta == meta["id"]:

            if meta["valor_atual"] + valor_adicionado <= meta["valor_meta"]:
                meta["valor_atual"] += valor_adicionado

                salvar_json(CAMINHO_METAS, lista_metas)
                return True

            return False

    return False


def adicionar_meta(nome_meta: str,valor_meta: float) -> None:

    lista_metas = obter_metas()

    metas = {
        "id": criar_id(lista_metas),
        "nome": nome_meta,
        "valor_atual": 0,
        "valor_meta": valor_meta,
    }

    lista_metas.append(metas)

    salvar_json(CAMINHO_METAS,lista_metas)


def editar_meta(novo_nome: str, valor_meta: float, valor_id: int) -> bool:

    lista_metas = obter_metas()

    for meta in lista_metas:

        if meta["id"] == valor_id:

            meta["nome"] = novo_nome
            meta["valor_meta"] = valor_meta

            salvar_json(CAMINHO_METAS, lista_metas)

            return True

    return False


def remover_meta(id_meta: int) -> bool:

    lista_metas = obter_metas()

    for meta in lista_metas:

        if meta["id"] == id_meta:

            lista_metas.remove(meta)
            salvar_json(CAMINHO_METAS,lista_metas)

            return True

    return False


def buscar_meta_por_id(id_meta: int):
    lista_metas = obter_metas()

    for meta in lista_metas:
        if meta["id"] == id_meta:
            return meta

    return None


