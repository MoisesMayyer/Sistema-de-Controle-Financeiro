

def criar_id(lista) -> int:
    if not lista:
        return 1

    return max(gasto["id"] for gasto in lista) + 1
