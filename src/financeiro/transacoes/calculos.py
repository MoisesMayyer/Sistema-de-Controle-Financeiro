from dados.dados import carregar_json, CAMINHO_TRANSACOES


def total_despesas():
    transacoes = carregar_json(CAMINHO_TRANSACOES)

    total = 0

    for t in transacoes:
        if t["tipo"] == "despesa":
            total += t["valor"]

    return total


def total_receitas():
    transacoes = carregar_json(CAMINHO_TRANSACOES)

    total = 0

    for t in transacoes:
        if t["tipo"] == "receita":
            total += t["valor"]

    return total


def saldo_atual():
    return total_receitas() - total_despesas()


def obter_resumo():
    receitas = total_receitas()
    despesas = total_despesas()

    return {
        "saldo": receitas - despesas,
        "receitas": receitas,
        "despesas": despesas,
    }

def calcular_gasto_categoria(id_categoria):
    total = 0

    lista_transacoes = carregar_json(CAMINHO_TRANSACOES)

    for transacao in lista_transacoes:

        if transacao['categoria_id'] == id_categoria and transacao["tipo"] == "despesa":
            total += transacao["valor"]

    return total