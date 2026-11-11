import pytest

from dados.models import Categoria
from rotas.categorias.crud import calcular_porcentagem_limite


def criar_categoria(client, headers, **dados):
    payload = {"nome": "mercado", "valor_inicial": 0, "valor_limite": 100}
    payload.update(dados)
    return client.post("/categorias/", json=payload, headers=headers)


def criar_transacao(client, headers, categoria_id, **dados):
    payload = {
        "descricao": "Compra",
        "valor": 50,
        "tipo": "despesa",
        "data": "2026-10-01",
        "categoria_id": categoria_id,
    }
    payload.update(dados)
    return client.post("/transacoes/", json=payload, headers=headers)


def test_criar_categoria_valida(client, headers):
    resposta = criar_categoria(client, headers, nome="testes")

    assert resposta.status_code == 201, resposta.text

    corpo = resposta.json()
    assert corpo["nome"] == "testes"
    assert corpo["valor_inicial"] == 0
    assert corpo["valor_limite"] == 100
    assert corpo["total_despesas"] == 0
    assert corpo["total_receitas"] == 0
    assert corpo["saldo"] == 0
    assert corpo["porcentagem_limite"] == 0.0


def test_criar_categoria_sem_valor_inicial_usa_zero(client, headers):
    resposta = client.post(
        "/categorias/",
        json={"nome": "lazer", "valor_limite": 200},
        headers=headers,
    )

    assert resposta.status_code == 201, resposta.text
    assert resposta.json()["valor_inicial"] == 0


def test_criar_categoria_nome_duplicado_retorna_400(client, headers):
    criar_categoria(client, headers)

    resposta = criar_categoria(client, headers)

    assert resposta.status_code == 400, resposta.text
    assert resposta.json()["detail"] == "Categoria com este nome já existe"


def test_criar_categoria_mesmo_nome_para_outro_usuario(
    client, headers, outro_headers
):
    minha = criar_categoria(client, headers)
    outra = criar_categoria(client, outro_headers)

    assert minha.status_code == 201, minha.text
    assert outra.status_code == 201, outra.text


@pytest.mark.parametrize(
    "nome,valor_inicial,valor_limite",
    [
        ("", 0, 100),
        ("a" * 101, 0, 100),
        ("mercado", -100, 100),
        ("mercado", 0, 0),
        ("mercado", 0, -100),
        ("mercado", 100, 100),
        ("mercado", 100, 50),
    ],
)
def test_criar_categoria_invalida(
    client, headers, nome, valor_inicial, valor_limite
):
    resposta = criar_categoria(
        client,
        headers,
        nome=nome,
        valor_inicial=valor_inicial,
        valor_limite=valor_limite,
    )

    assert resposta.status_code == 422, resposta.text


@pytest.mark.parametrize(
    "dados",
    [
        {},
        {"nome": "mercado"},
        {"valor_limite": 100},
    ],
)
def test_criar_categoria_sem_campos_obrigatorios(client, headers, dados):
    resposta = client.post("/categorias/", json=dados, headers=headers)

    assert resposta.status_code == 422, resposta.text


def test_listar_categorias_usuario(client, headers):
    criar_categoria(client, headers)

    resposta = client.get("/categorias/", headers=headers)

    assert resposta.status_code == 200, resposta.text
    assert len(resposta.json()) == 1
    assert resposta.json()[0]["nome"] == "mercado"
    assert resposta.json()[0]["valor_limite"] == 100


def test_listar_categorias_retorna_apenas_do_usuario(
    client, headers, outro_headers
):
    minha = criar_categoria(client, headers)
    outra = criar_categoria(client, outro_headers, nome="lazer")

    assert minha.status_code == 201, minha.text
    assert outra.status_code == 201, outra.text

    resposta = client.get("/categorias/", headers=headers)

    assert resposta.status_code == 200, resposta.text
    assert [item["id"] for item in resposta.json()] == [minha.json()["id"]]


def test_buscar_categoria_propria(client, headers):
    criada = criar_categoria(client, headers)

    resposta = client.get(f"/categorias/{criada.json()['id']}", headers=headers)

    assert resposta.status_code == 200, resposta.text
    assert resposta.json()["nome"] == "mercado"


def test_listar_categoria_inexistente(client, headers):
    resposta = client.get("/categorias/99999999", headers=headers)

    assert resposta.status_code == 404, resposta.text
    assert resposta.json()["detail"] == "Categoria não encontrada"


def test_buscar_categoria_de_outro_usuario_retorna_404(
    client, headers, outro_headers
):
    criada = criar_categoria(client, outro_headers)

    resposta = client.get(f"/categorias/{criada.json()['id']}", headers=headers)

    assert resposta.status_code == 404, resposta.text
    assert resposta.json()["detail"] == "Categoria não encontrada"


def test_buscar_categoria_com_transacoes_calcula_agregados(client, headers):
    criada = criar_categoria(client, headers, valor_inicial=100, valor_limite=400)
    categoria_id = criada.json()["id"]

    receita = criar_transacao(
        client,
        headers,
        categoria_id,
        descricao="Salário",
        valor=200,
        tipo="receita",
    )
    despesa = criar_transacao(
        client,
        headers,
        categoria_id,
        descricao="Compras",
        valor=50,
    )

    assert receita.status_code == 201, receita.text
    assert despesa.status_code == 201, despesa.text

    resposta = client.get(f"/categorias/{categoria_id}", headers=headers)

    assert resposta.status_code == 200, resposta.text

    corpo = resposta.json()
    assert corpo["total_despesas"] == 50
    assert corpo["total_receitas"] == 200
    assert corpo["saldo"] == 250
    assert corpo["porcentagem_limite"] == 12.5


def test_porcentagem_limite_limitada_a_100(client, headers):
    criada = criar_categoria(client, headers, valor_limite=100)

    despesa = criar_transacao(
        client,
        headers,
        criada.json()["id"],
        valor=200,
    )
    assert despesa.status_code == 201, despesa.text

    resposta = client.get(f"/categorias/{criada.json()['id']}", headers=headers)

    assert resposta.status_code == 200, resposta.text
    assert resposta.json()["porcentagem_limite"] == 100.0


def test_calcular_porcentagem_limite_com_valor_limite_zero():
    assert calcular_porcentagem_limite(100, 0) == 0.0


def test_editar_categoria_propria(client, headers):
    criada = criar_categoria(client, headers)

    resposta = client.put(
        f"/categorias/{criada.json()['id']}",
        json={"nome": "lazer", "valor_limite": 200},
        headers=headers,
    )

    assert resposta.status_code == 200, resposta.text
    assert resposta.json()["nome"] == "lazer"
    assert resposta.json()["valor_limite"] == 200
    assert resposta.json()["valor_inicial"] == 0


def test_editar_categoria_valor_inicial(client, headers):
    criada = criar_categoria(client, headers)

    resposta = client.put(
        f"/categorias/{criada.json()['id']}",
        json={"valor_inicial": 50, "valor_limite": 300},
        headers=headers,
    )

    assert resposta.status_code == 200, resposta.text
    assert resposta.json()["valor_inicial"] == 50
    assert resposta.json()["valor_limite"] == 300


def test_editar_categoria_mantendo_o_proprio_nome(client, headers):
    criada = criar_categoria(client, headers)

    resposta = client.put(
        f"/categorias/{criada.json()['id']}",
        json={"nome": "mercado"},
        headers=headers,
    )

    assert resposta.status_code == 200, resposta.text
    assert resposta.json()["nome"] == "mercado"


def test_editar_categoria_nome_duplicado_retorna_400(client, headers):
    criar_categoria(client, headers, nome="mercado")
    criada = criar_categoria(client, headers, nome="lazer")

    resposta = client.put(
        f"/categorias/{criada.json()['id']}",
        json={"nome": "mercado"},
        headers=headers,
    )

    assert resposta.status_code == 400, resposta.text
    assert resposta.json()["detail"] == "Categoria com este nome já existe"


@pytest.mark.parametrize(
    "dados",
    [
        {"valor_limite": 100},
        {"valor_inicial": 500},
    ],
)
def test_editar_categoria_com_valor_limite_menor_que_inicial_retorna_400(
    client, headers, dados
):
    criada = criar_categoria(client, headers, valor_inicial=100, valor_limite=400)

    resposta = client.put(
        f"/categorias/{criada.json()['id']}",
        json=dados,
        headers=headers,
    )

    assert resposta.status_code == 400, resposta.text
    assert resposta.json()["detail"] == "valor_limite deve ser maior que valor_inicial"


@pytest.mark.parametrize(
    "dados",
    [
        {"nome": ""},
        {"nome": "a" * 101},
        {"valor_inicial": -1},
        {"valor_limite": 0},
    ],
)
def test_editar_categoria_dados_invalidos(client, headers, dados):
    criada = criar_categoria(client, headers)

    resposta = client.put(
        f"/categorias/{criada.json()['id']}",
        json=dados,
        headers=headers,
    )

    assert resposta.status_code == 422, resposta.text


def test_editar_categoria_de_outro_usuario_retorna_404(
    client, headers, outro_headers
):
    criada = criar_categoria(client, outro_headers)

    resposta = client.put(
        f"/categorias/{criada.json()['id']}",
        json={"nome": "invasao"},
        headers=headers,
    )

    assert resposta.status_code == 404, resposta.text
    assert resposta.json()["detail"] == "Categoria não encontrada"


def test_remover_categoria_propria(client, headers, db_session):
    criada = criar_categoria(client, headers)

    resposta = client.delete(f"/categorias/{criada.json()['id']}", headers=headers)

    assert resposta.status_code == 200, resposta.text
    assert resposta.json()["message"] == "Categoria removida com sucesso"

    db_session.expire_all()
    assert db_session.get(Categoria, criada.json()["id"]) is None


def test_remover_categoria_de_outro_usuario_retorna_404(
    client, headers, outro_headers
):
    criada = criar_categoria(client, outro_headers)

    resposta = client.delete(f"/categorias/{criada.json()['id']}", headers=headers)

    assert resposta.status_code == 404, resposta.text


def test_remover_categoria_com_transacoes_retorna_400(
    client, headers, db_session
):
    criada = criar_categoria(client, headers)
    transacao = criar_transacao(client, headers, criada.json()["id"])
    assert transacao.status_code == 201, transacao.text

    resposta = client.delete(f"/categorias/{criada.json()['id']}", headers=headers)

    assert resposta.status_code == 400, resposta.text
    assert (
        resposta.json()["detail"]
        == "Não é possível remover categoria com transações associadas"
    )

    db_session.expire_all()
    assert db_session.get(Categoria, criada.json()["id"]) is not None


@pytest.mark.parametrize(
    ("metodo", "caminho"),
    [
        ("get", "/categorias/"),
        ("get", "/categorias/1"),
        ("post", "/categorias/"),
        ("put", "/categorias/1"),
        ("delete", "/categorias/1"),
    ],
)
def test_rotas_de_categorias_sem_token(client, metodo, caminho):
    json = None
    if metodo in ("post", "put"):
        json = {"nome": "mercado", "valor_inicial": 0, "valor_limite": 100}

    resposta = client.request(metodo.upper(), caminho, json=json)

    assert resposta.status_code == 401, resposta.text


def test_listar_categorias_token_invalido(client):
    resposta = client.get(
        "/categorias/", headers={"Authorization": "Bearer token.invalido.aqui"}
    )

    assert resposta.status_code == 401, resposta.text