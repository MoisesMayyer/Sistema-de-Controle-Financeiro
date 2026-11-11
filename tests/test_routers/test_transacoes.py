import pytest

from dados.models import Transacao


def criar_categoria(client, headers, **dados):
    payload = {"nome": "mercado", "valor_inicial": 0, "valor_limite": 100}
    payload.update(dados)
    return client.post("/categorias/", json=payload, headers=headers)


def criar_transacao(client, headers, **dados):
    payload = {
        "descricao": "Compra",
        "valor": 50,
        "tipo": "despesa",
        "data": "2026-10-01",
    }
    payload.update(dados)
    return client.post("/transacoes/", json=payload, headers=headers)


def test_criar_transacao_valida(client, headers):
    categoria = criar_categoria(client, headers)
    assert categoria.status_code == 201, categoria.text

    resposta = criar_transacao(
        client,
        headers,
        categoria_id=categoria.json()["id"],
    )

    assert resposta.status_code == 201, resposta.text

    corpo = resposta.json()
    assert corpo["descricao"] == "Compra"
    assert corpo["valor"] == 50
    assert corpo["tipo"] == "despesa"
    assert corpo["data"] == "2026-10-01"
    assert corpo["categoria_id"] == categoria.json()["id"]


def test_criar_transacao_sem_categoria(client, headers):
    resposta = criar_transacao(client, headers)

    assert resposta.status_code == 201, resposta.text
    assert resposta.json()["categoria_id"] is None


@pytest.mark.parametrize("tipo", ["receita", "despesa"])
def test_criar_transacao_tipos_validos(client, headers, tipo):
    resposta = criar_transacao(client, headers, tipo=tipo)

    assert resposta.status_code == 201, resposta.text
    assert resposta.json()["tipo"] == tipo


@pytest.mark.parametrize(
    "dados",
    [
        {},
        {"descricao": "Compra", "valor": 50, "tipo": "despesa"},
        {"descricao": "", "valor": 50, "tipo": "despesa", "data": "2026-10-01"},
        {"descricao": "a" * 256, "valor": 50, "tipo": "despesa", "data": "2026-10-01"},
        {"descricao": "Compra", "valor": 0, "tipo": "despesa", "data": "2026-10-01"},
        {"descricao": "Compra", "valor": -10, "tipo": "despesa", "data": "2026-10-01"},
        {"descricao": "Compra", "valor": 50, "tipo": "transferencia", "data": "2026-10-01"},
        {"descricao": "Compra", "valor": 50, "tipo": "despesa", "data": "data-invalida"},
        {"descricao": "Compra", "valor": 50, "tipo": "despesa", "data": "2026-10-01", "categoria_id": "abc"},
    ],
)
def test_criar_transacao_dados_invalidos(client, headers, dados):
    resposta = client.post("/transacoes/", json=dados, headers=headers)

    assert resposta.status_code == 422, resposta.text


def test_criar_transacao_com_categoria_inexistente_retorna_400(client, headers):
    resposta = criar_transacao(client, headers, categoria_id=999999)

    assert resposta.status_code == 400, resposta.text
    assert resposta.json()["detail"] == "Categoria não encontrada"


def test_criar_transacao_com_categoria_de_outro_usuario_retorna_400(
    client, headers, outro_headers
):
    categoria = criar_categoria(client, outro_headers)
    assert categoria.status_code == 201, categoria.text

    resposta = criar_transacao(
        client,
        headers,
        categoria_id=categoria.json()["id"],
    )

    assert resposta.status_code == 400, resposta.text
    assert resposta.json()["detail"] == "Categoria não encontrada"


def test_listar_transacoes_retorna_apenas_do_usuario(
    client, headers, outro_headers
):
    minha = criar_transacao(client, headers)
    outra = criar_transacao(client, outro_headers)

    assert minha.status_code == 201, minha.text
    assert outra.status_code == 201, outra.text

    resposta = client.get("/transacoes/", headers=headers)

    assert resposta.status_code == 200, resposta.text
    assert [item["id"] for item in resposta.json()] == [minha.json()["id"]]


def test_buscar_transacao_propria(client, headers):
    criada = criar_transacao(client, headers)

    resposta = client.get(f"/transacoes/{criada.json()['id']}", headers=headers)

    assert resposta.status_code == 200, resposta.text
    assert resposta.json()["descricao"] == "Compra"


def test_buscar_transacao_de_outro_usuario_retorna_404(
    client, headers, outro_headers
):
    criada = criar_transacao(client, outro_headers)

    resposta = client.get(f"/transacoes/{criada.json()['id']}", headers=headers)

    assert resposta.status_code == 404, resposta.text
    assert resposta.json()["detail"] == "Transação não encontrada"


def test_buscar_transacao_inexistente_retorna_404(client, headers):
    resposta = client.get("/transacoes/999999", headers=headers)

    assert resposta.status_code == 404, resposta.text
    assert resposta.json()["detail"] == "Transação não encontrada"


def test_editar_transacao_propria(client, headers):
    criada = criar_transacao(client, headers)

    resposta = client.put(
        f"/transacoes/{criada.json()['id']}",
        json={"descricao": "Aluguel", "valor": 1200},
        headers=headers,
    )

    assert resposta.status_code == 200, resposta.text
    assert resposta.json()["descricao"] == "Aluguel"
    assert resposta.json()["valor"] == 1200
    assert resposta.json()["tipo"] == "despesa"
    assert resposta.json()["data"] == "2026-10-01"


def test_editar_transacao_troca_categoria(client, headers):
    mercado = criar_categoria(client, headers, nome="mercado")
    lazer = criar_categoria(client, headers, nome="lazer")
    criada = criar_transacao(
        client,
        headers,
        categoria_id=mercado.json()["id"],
    )

    resposta = client.put(
        f"/transacoes/{criada.json()['id']}",
        json={"categoria_id": lazer.json()["id"]},
        headers=headers,
    )

    assert resposta.status_code == 200, resposta.text
    assert resposta.json()["categoria_id"] == lazer.json()["id"]


def test_editar_transacao_desvincula_categoria(client, headers):
    categoria = criar_categoria(client, headers)
    criada = criar_transacao(
        client,
        headers,
        categoria_id=categoria.json()["id"],
    )

    resposta = client.put(
        f"/transacoes/{criada.json()['id']}",
        json={"categoria_id": None},
        headers=headers,
    )

    assert resposta.status_code == 200, resposta.text
    assert resposta.json()["categoria_id"] is None


def test_editar_transacao_com_categoria_inexistente_retorna_400(
    client, headers
):
    criada = criar_transacao(client, headers)

    resposta = client.put(
        f"/transacoes/{criada.json()['id']}",
        json={"categoria_id": 999999},
        headers=headers,
    )

    assert resposta.status_code == 400, resposta.text
    assert resposta.json()["detail"] == "Categoria não encontrada"


def test_editar_transacao_com_categoria_de_outro_usuario_retorna_400(
    client, headers, outro_headers
):
    categoria = criar_categoria(client, outro_headers)
    criada = criar_transacao(client, headers)

    resposta = client.put(
        f"/transacoes/{criada.json()['id']}",
        json={"categoria_id": categoria.json()["id"]},
        headers=headers,
    )

    assert resposta.status_code == 400, resposta.text
    assert resposta.json()["detail"] == "Categoria não encontrada"


@pytest.mark.parametrize(
    "dados",
    [
        {"descricao": ""},
        {"descricao": "a" * 256},
        {"valor": 0},
        {"valor": -10},
        {"tipo": "transferencia"},
        {"data": "data-invalida"},
    ],
)
def test_editar_transacao_dados_invalidos(client, headers, dados):
    criada = criar_transacao(client, headers)

    resposta = client.put(
        f"/transacoes/{criada.json()['id']}",
        json=dados,
        headers=headers,
    )

    assert resposta.status_code == 422, resposta.text


def test_editar_transacao_de_outro_usuario_retorna_404(
    client, headers, outro_headers
):
    criada = criar_transacao(client, outro_headers)

    resposta = client.put(
        f"/transacoes/{criada.json()['id']}",
        json={"descricao": "invasao"},
        headers=headers,
    )

    assert resposta.status_code == 404, resposta.text
    assert resposta.json()["detail"] == "Transação não encontrada"


def test_remover_transacao_propria(client, headers, db_session):
    criada = criar_transacao(client, headers)

    resposta = client.delete(f"/transacoes/{criada.json()['id']}", headers=headers)

    assert resposta.status_code == 200, resposta.text
    assert resposta.json()["message"] == "Transação removida com sucesso"

    db_session.expire_all()
    assert db_session.get(Transacao, criada.json()["id"]) is None


def test_remover_transacao_de_outro_usuario_retorna_404(
    client, headers, outro_headers
):
    criada = criar_transacao(client, outro_headers)

    resposta = client.delete(f"/transacoes/{criada.json()['id']}", headers=headers)

    assert resposta.status_code == 404, resposta.text


@pytest.mark.parametrize(
    ("metodo", "caminho"),
    [
        ("get", "/transacoes/"),
        ("get", "/transacoes/1"),
        ("post", "/transacoes/"),
        ("put", "/transacoes/1"),
        ("delete", "/transacoes/1"),
    ],
)
def test_rotas_de_transacoes_sem_token(client, metodo, caminho):
    json = None
    if metodo in ("post", "put"):
        json = {
            "descricao": "Compra",
            "valor": 50,
            "tipo": "despesa",
            "data": "2026-10-01",
        }

    resposta = client.request(metodo.upper(), caminho, json=json)

    assert resposta.status_code == 401, resposta.text


def test_listar_transacoes_token_invalido(client):
    resposta = client.get(
        "/transacoes/", headers={"Authorization": "Bearer token.invalido.aqui"}
    )

    assert resposta.status_code == 401, resposta.text