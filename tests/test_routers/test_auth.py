import pytest


def test_login_senha_invalida(client):
    resposta = client.post("/auth/login", data={"username": "user1@example.com", "password": "senhainvalida"})

    assert resposta.status_code == 401, resposta.text


def test_login_email_invalido(client):
    resposta = client.post(
        "/auth/login",
        data={"username": "email@errado.com", "password": "senha12345"}
    )

    assert resposta.status_code == 401, resposta.text


@pytest.mark.parametrize(
    "user, senha",
    [
        {"email": "user1@example.com", "senha": ""},
        {"email": "", "senha": "senha12345"},
        {"email": "", "senha": ""},
    ]
)
def test_login_dados_vazios(client, user, senha):
    resposta = client.post("/auth/login", data={"username": user, "password": senha})

    assert resposta.status_code == 401, resposta.text


def test_login_valido(client, usuario):
    resposta = client.post(
        "/auth/login",
        data={"username": "user1@example.com", "password": "senha12345"},
    )

    assert resposta.status_code == 200, resposta.text

    corpo = resposta.json()
    assert corpo["token_type"] == "bearer"
    assert corpo["access_token"]


def test_login_conta_desativada(client, criar_usuario, db_session):
    criar_usuario(nome="ana", email="ana@xample.com", senha="senha123", ativo=False)

    resposta = client.post(
        "/auth/login",
        data={"username": "ana@example.com", "password": "senha123"},
    )

    assert resposta.status_code == 201, resposta.text

