import pytest

from dados.models import Meta
from rotas.metas.crud import calcular_porcentagem_meta


def criar_meta(client, headers, **dados):
    payload = {"nome": "Viagem", "valor_inicial": 250, "valor_final": 1000}
    payload.update(dados)
    return client.post("/metas/", json=payload, headers=headers)


def test_criar_meta_valida(client, headers):
    resposta = criar_meta(
        client,
        headers,
        data_inicio="2026-10-01",
        data_fim="2026-12-31",
    )

    assert resposta.status_code == 201, resposta.text

    corpo = resposta.json()
    assert corpo["nome"] == "Viagem"
    assert corpo["valor_inicial"] == 250
    assert corpo["valor_final"] == 1000
    assert corpo["data_inicio"] == "2026-10-01"
    assert corpo["data_fim"] == "2026-12-31"
    assert corpo["porcentagem"] == 25.0


def test_criar_meta_sem_valor_inicial_usa_zero(client, headers):
    resposta = client.post(
        "/metas/",
        json={"nome": "Reserva", "valor_final": 1000},
        headers=headers,
    )

    assert resposta.status_code == 201, resposta.text
    assert resposta.json()["valor_inicial"] == 0
    assert resposta.json()["porcentagem"] == 0.0


def test_criar_meta_atingida_limita_porcentagem_a_100(client, headers):
    resposta = criar_meta(client, headers, valor_inicial=1000, valor_final=1000)

    assert resposta.status_code == 201, resposta.text
    assert resposta.json()["porcentagem"] == 100.0


def test_calcular_porcentagem_com_valor_final_zero():
    assert calcular_porcentagem_meta(100, 0) == 0.0


@pytest.mark.parametrize(
    "dados",
    [
        {},
        {"nome": "", "valor_final": 1000},
        {"nome": "a" * 101, "valor_final": 1000},
        {"nome": "Viagem", "valor_inicial": -1, "valor_final": 1000},
        {"nome": "Viagem", "valor_final": 0},
        {"nome": "Viagem", "valor_inicial": 500, "valor_final": 100},
        {"nome": "Viagem", "valor_final": 1000, "data_inicio": "2026-10-10", "data_fim": "2026-10-10",},
        {"nome": "Viagem", "valor_final": 1000, "data_inicio": "2026-12-31", "data_fim": "2026-10-01",},
    ],
)
def test_criar_meta_dados_invalidos(client, headers, dados):
    resposta = client.post("/metas/", json=dados, headers=headers)

    assert resposta.status_code == 422, resposta.text


def test_listar_metas_retorna_apenas_do_usuario(
    client, headers, outro_headers
):
    minha = criar_meta(client, headers)
    outra = criar_meta(client, outro_headers, nome="Curso")

    assert minha.status_code == 201, minha.text
    assert outra.status_code == 201, outra.text

    resposta = client.get("/metas/", headers=headers)

    assert resposta.status_code == 200, resposta.text
    corpo = resposta.json()
    assert [item["id"] for item in corpo["items"]] == [minha.json()["id"]]
    assert corpo["total"] == 1


def test_listar_metas_paginado(client, headers):
    for nome in ("Viagem", "Curso", "Reserva"):
        assert criar_meta(client, headers, nome=nome).status_code == 201

    pagina_1 = client.get("/metas/?skip=0&limit=2", headers=headers).json()
    pagina_2 = client.get("/metas/?skip=2&limit=2", headers=headers).json()

    assert pagina_1["total"] == 3
    assert pagina_1["skip"] == 0
    assert pagina_1["limit"] == 2
    assert len(pagina_1["items"]) == 2
    assert len(pagina_2["items"]) == 1
    assert pagina_2["total"] == 3

    ids = [item["id"] for item in pagina_1["items"] + pagina_2["items"]]
    assert len(ids) == len(set(ids)) == 3


def test_listar_metas_filtra_por_busca(client, headers):
    assert criar_meta(client, headers, nome="Viagem").status_code == 201
    assert criar_meta(client, headers, nome="Curso").status_code == 201

    resposta = client.get("/metas/?busca=cur", headers=headers)

    assert resposta.status_code == 200, resposta.text
    assert [item["nome"] for item in resposta.json()["items"]] == ["Curso"]
    assert resposta.json()["total"] == 1


@pytest.mark.parametrize(
    "query",
    ["limit=0", "limit=101", "skip=-1"],
)
def test_listar_metas_paginacao_invalida(client, headers, query):
    resposta = client.get(f"/metas/?{query}", headers=headers)

    assert resposta.status_code == 422, resposta.text


def test_buscar_meta_propria(client, headers):
    criada = criar_meta(client, headers)

    resposta = client.get(f"/metas/{criada.json()['id']}", headers=headers)

    assert resposta.status_code == 200, resposta.text
    assert resposta.json()["nome"] == "Viagem"


def test_buscar_meta_de_outro_usuario_retorna_404(
    client, headers, outro_usuario, outro_headers
):
    criada = criar_meta(client, outro_headers)

    resposta = client.get(f"/metas/{criada.json()['id']}", headers=headers)

    assert resposta.status_code == 404, resposta.text
    assert resposta.json()["detail"] == "Meta não encontrada"


def test_buscar_meta_inexistente_retorna_404(client, headers):
    resposta = client.get("/metas/999999", headers=headers)

    assert resposta.status_code == 404, resposta.text


def test_editar_meta_propria(client, headers):
    criada = criar_meta(client, headers)

    resposta = client.put(
        f"/metas/{criada.json()['id']}",
        json={"nome": "Viagem atualizada", "valor_final": 2000},
        headers=headers,
    )

    assert resposta.status_code == 200, resposta.text
    assert resposta.json()["nome"] == "Viagem atualizada"
    assert resposta.json()["valor_final"] == 2000
    assert resposta.json()["valor_inicial"] == 250
    assert resposta.json()["porcentagem"] == 12.5


def test_editar_meta_valor_inicial_e_datas(client, headers):
    criada = criar_meta(
        client,
        headers,
        data_inicio="2026-10-01",
        data_fim="2026-12-31",
    )

    resposta = client.put(
        f"/metas/{criada.json()['id']}",
        json={
            "valor_inicial": 500,
            "data_inicio": "2026-10-05",
            "data_fim": "2026-11-30",
        },
        headers=headers,
    )

    assert resposta.status_code == 200, resposta.text
    assert resposta.json()["valor_inicial"] == 500
    assert resposta.json()["data_inicio"] == "2026-10-05"
    assert resposta.json()["data_fim"] == "2026-11-30"
    assert resposta.json()["porcentagem"] == 50.0


def test_editar_meta_de_outro_usuario_retorna_404(
    client, headers, outro_headers
):
    criada = criar_meta(client, outro_headers)

    resposta = client.put(
        f"/metas/{criada.json()['id']}",
        json={"nome": "invasao"},
        headers=headers,
    )

    assert resposta.status_code == 404, resposta.text
    assert resposta.json()["detail"] == "Meta não encontrada"


def test_editar_meta_com_valor_final_menor_que_inicial_retorna_400(
    client, headers
):
    criada = criar_meta(client, headers)

    resposta = client.put(
        f"/metas/{criada.json()['id']}",
        json={"valor_final": 100},
        headers=headers,
    )

    assert resposta.status_code == 400, resposta.text
    assert resposta.json()["detail"] == "valor_final não pode ser menor que valor_inicial"


def test_editar_meta_com_data_fim_anterior_a_inicio_retorna_400(
    client, headers
):
    criada = criar_meta(
        client,
        headers,
        data_inicio="2026-10-01",
        data_fim="2026-12-31",
    )

    resposta = client.put(
        f"/metas/{criada.json()['id']}",
        json={"data_fim": "2026-09-30"},
        headers=headers,
    )

    assert resposta.status_code == 400, resposta.text
    assert resposta.json()["detail"] == "data_fim deve ser posterior a data_inicio"


@pytest.mark.parametrize(
    "dados",
    [
        {"nome": ""},
        {"nome": "a" * 101},
        {"valor_inicial": -1},
        {"valor_final": 0},
    ],
)
def test_editar_meta_dados_invalidos(client, headers, dados):
    criada = criar_meta(client, headers)

    resposta = client.put(
        f"/metas/{criada.json()['id']}",
        json=dados,
        headers=headers,
    )

    assert resposta.status_code == 422, resposta.text


def test_remover_meta_propria(client, headers, db_session):
    criada = criar_meta(client, headers)

    resposta = client.delete(f"/metas/{criada.json()['id']}", headers=headers)

    assert resposta.status_code == 200, resposta.text
    assert resposta.json()["message"] == "Meta removida com sucesso"

    db_session.expire_all()
    assert db_session.get(Meta, criada.json()["id"]) is None


def test_remover_meta_de_outro_usuario_retorna_404(
    client, headers, outro_headers
):
    criada = criar_meta(client, outro_headers)

    resposta = client.delete(f"/metas/{criada.json()['id']}", headers=headers)

    assert resposta.status_code == 404, resposta.text


def test_adicionar_valor_meta(client, headers):
    criada = criar_meta(client, headers)

    resposta = client.post(
        f"/metas/{criada.json()['id']}/adicionar-valor",
        json={"valor": 750},
        headers=headers,
    )

    assert resposta.status_code == 200, resposta.text
    assert resposta.json()["valor_inicial"] == 1000
    assert resposta.json()["porcentagem"] == 100.0


def test_adicionar_valor_acima_do_valor_final_retorna_400(client, headers):
    criada = criar_meta(client, headers)

    resposta = client.post(
        f"/metas/{criada.json()['id']}/adicionar-valor",
        json={"valor": 800},
        headers=headers,
    )

    assert resposta.status_code == 400, resposta.text
    assert resposta.json()["detail"] == "Valor excede o valor final da meta"


@pytest.mark.parametrize("dados", [{}, {"valor": 0}, {"valor": -10}])
def test_adicionar_valor_invalido(client, headers, dados):
    criada = criar_meta(client, headers)

    resposta = client.post(
        f"/metas/{criada.json()['id']}/adicionar-valor",
        json=dados,
        headers=headers,
    )

    assert resposta.status_code == 422, resposta.text


def test_adicionar_valor_meta_de_outro_usuario_retorna_404(
    client, headers, outro_headers
):
    criada = criar_meta(client, outro_headers)

    resposta = client.post(
        f"/metas/{criada.json()['id']}/adicionar-valor",
        json={"valor": 100},
        headers=headers,
    )

    assert resposta.status_code == 404, resposta.text


def test_adicionar_valor_meta_inexistente_retorna_404(client, headers):
    resposta = client.post(
        "/metas/999999/adicionar-valor",
        json={"valor": 100},
        headers=headers,
    )

    assert resposta.status_code == 404, resposta.text


@pytest.mark.parametrize(
    ("metodo", "caminho"),
    [
        ("get", "/metas/"),
        ("get", "/metas/1"),
        ("post", "/metas/"),
        ("put", "/metas/1"),
        ("delete", "/metas/1"),
        ("post", "/metas/1/adicionar-valor"),
    ],
)
def test_rotas_de_metas_sem_token(client, metodo, caminho):
    json = None
    if metodo in ("post", "put"):
        json = {"nome": "Viagem", "valor_final": 1000, "valor": 100}

    resposta = client.request(metodo.upper(), caminho, json=json)

    assert resposta.status_code == 401, resposta.text


def test_listar_metas_token_invalido(client):
    resposta = client.get(
        "/metas/", headers={"Authorization": "Bearer token.invalido.aqui"}
    )

    assert resposta.status_code == 401, resposta.text