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
    corpo = resposta.json()
    assert [item["id"] for item in corpo["items"]] == [minha.json()["id"]]
    assert corpo["total"] == 1


def test_listar_transacoes_paginado(client, headers):
    for i in range(3):
        assert criar_transacao(client, headers, descricao=f"Compra {i}").status_code == 201

    pagina_1 = client.get("/transacoes/?skip=0&limit=2", headers=headers).json()
    pagina_2 = client.get("/transacoes/?skip=2&limit=2", headers=headers).json()

    assert pagina_1["total"] == 3
    assert pagina_1["skip"] == 0
    assert pagina_1["limit"] == 2
    assert len(pagina_1["items"]) == 2
    assert len(pagina_2["items"]) == 1
    assert pagina_2["total"] == 3

    ids = [item["id"] for item in pagina_1["items"] + pagina_2["items"]]
    assert len(ids) == len(set(ids)) == 3


def test_listar_transacoes_filtra_por_busca(client, headers):
    assert criar_transacao(client, headers, descricao="Mercado").status_code == 201
    assert criar_transacao(client, headers, descricao="Aluguel").status_code == 201

    resposta = client.get("/transacoes/?busca=merca", headers=headers)

    assert resposta.status_code == 200, resposta.text
    corpo = resposta.json()
    assert [item["descricao"] for item in corpo["items"]] == ["Mercado"]
    assert corpo["total"] == 1


@pytest.mark.parametrize(
    "query",
    ["limit=0", "limit=101", "skip=-1"],
)
def test_listar_transacoes_paginacao_invalida(client, headers, query):
    resposta = client.get(f"/transacoes/?{query}", headers=headers)

    assert resposta.status_code == 422, resposta.text


def test_listar_transacoes_filtra_por_tipo(client, headers):
    assert criar_transacao(
        client, headers, descricao="Compra", tipo="despesa"
    ).status_code == 201
    assert criar_transacao(
        client, headers, descricao="Salario", tipo="receita"
    ).status_code == 201

    resposta = client.get("/transacoes/?tipo=receita", headers=headers)

    assert resposta.status_code == 200, resposta.text
    corpo = resposta.json()
    assert [item["descricao"] for item in corpo["items"]] == ["Salario"]
    assert corpo["total"] == 1


def test_listar_transacoes_filtra_por_categoria(client, headers):
    mercado = criar_categoria(client, headers)
    lazer = criar_categoria(client, headers, nome="lazer")

    assert criar_transacao(
        client, headers, descricao="Feira", categoria_id=mercado.json()["id"]
    ).status_code == 201
    assert criar_transacao(
        client, headers, descricao="Cinema", categoria_id=lazer.json()["id"]
    ).status_code == 201

    resposta = client.get(
        f"/transacoes/?categoria_id={mercado.json()['id']}", headers=headers
    )

    assert resposta.status_code == 200, resposta.text
    corpo = resposta.json()
    assert [item["descricao"] for item in corpo["items"]] == ["Feira"]
    assert corpo["total"] == 1


def test_listar_transacoes_filtra_por_periodo(client, headers):
    for data in ("2026-09-30", "2026-10-01", "2026-10-31", "2026-11-01"):
        assert criar_transacao(
            client, headers, descricao=f"Compra {data}", data=data
        ).status_code == 201

    resposta = client.get(
        "/transacoes/?data_inicio=2026-10-01&data_fim=2026-10-31", headers=headers
    )

    assert resposta.status_code == 200, resposta.text
    corpo = resposta.json()
    assert corpo["total"] == 2
    assert [item["data"] for item in corpo["items"]] == [
        "2026-10-31",
        "2026-10-01",
    ]


def test_listar_transacoes_ordena_por_data_mais_recente(client, headers):
    for data in ("2026-10-01", "2026-10-03", "2026-10-02"):
        assert criar_transacao(
            client, headers, descricao=f"Compra {data}", data=data
        ).status_code == 201

    resposta = client.get("/transacoes/", headers=headers)

    assert resposta.status_code == 200, resposta.text
    assert [item["data"] for item in resposta.json()["items"]] == [
        "2026-10-03",
        "2026-10-02",
        "2026-10-01",
    ]


def test_listar_transacoes_combina_filtros(client, headers):
    mercado = criar_categoria(client, headers)
    categoria_id = mercado.json()["id"]

    assert criar_transacao(
        client, headers, descricao="Feira outubro", tipo="despesa",
        data="2026-10-05", categoria_id=categoria_id,
    ).status_code == 201
    assert criar_transacao(
        client, headers, descricao="Feira novembro", tipo="despesa",
        data="2026-11-05", categoria_id=categoria_id,
    ).status_code == 201
    assert criar_transacao(
        client, headers, descricao="Salario outubro", tipo="receita",
        data="2026-10-05", categoria_id=categoria_id,
    ).status_code == 201

    resposta = client.get(
        "/transacoes/?tipo=despesa&data_inicio=2026-10-01"
        "&data_fim=2026-10-31&skip=0&limit=10",
        headers=headers,
    )

    assert resposta.status_code == 200, resposta.text
    corpo = resposta.json()
    assert [item["descricao"] for item in corpo["items"]] == ["Feira outubro"]
    assert corpo["total"] == 1


def test_listar_transacoes_data_inicio_maior_que_data_fim(client, headers):
    resposta = client.get(
        "/transacoes/?data_inicio=2026-11-01&data_fim=2026-10-01", headers=headers
    )

    assert resposta.status_code == 400, resposta.text
    assert resposta.json()["detail"] == "data_inicio deve ser anterior ou igual a data_fim"


def test_listar_transacoes_tipo_invalido(client, headers):
    resposta = client.get("/transacoes/?tipo=investimento", headers=headers)

    assert resposta.status_code == 422, resposta.text


def test_listar_transacoes_categoria_sem_transacoes_retorna_vazio(client, headers):
    resposta = client.get("/transacoes/?categoria_id=999999", headers=headers)

    assert resposta.status_code == 200, resposta.text
    corpo = resposta.json()
    assert corpo["items"] == []
    assert corpo["total"] == 0


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