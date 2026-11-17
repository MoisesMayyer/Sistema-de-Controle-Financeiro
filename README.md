# Controle Financeiro API

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.162-009688?logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.1-D71F00)
![Pydantic](https://img.shields.io/badge/Pydantic-2.14-E92063)
![PyJWT](https://img.shields.io/badge/PyJWT-2.15-000000?logo=jsonwebtokens&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-4169E1?logo=postgresql&logoColor=white)
![Alembic](https://img.shields.io/badge/Alembic-1.20-6BA81E)
![mypy](https://img.shields.io/badge/mypy-passing-2A6DB0)
![pytest](https://img.shields.io/badge/pytest-249%20testes-0A9EDC?logo=pytest&logoColor=white)
![Neon](https://img.shields.io/badge/Neon-0065FF?logo=neon&logoColor=white)
![Render](https://img.shields.io/badge/Render-46E3B7?logo=render&logoColor=white)

API REST **multi-usuário** de controle financeiro pessoal com autenticação JWT, isolamento de dados por usuário e deploy no Render + Neon.

[API](https://controle-financeiro-api.onrender.com) · [Swagger](https://controle-financeiro-api.onrender.com/docs)

> [!NOTE]
> Projeto de estudo e portfólio. Começou como um controle de terminal em JSON e foi reescrito para aprender **FastAPI**, **SQLAlchemy**, **Pydantic**, **PostgreSQL** e **Alembic**.

## Sumário

[Sobre](#sobre-o-projeto) · [Funcionalidades](#funcionalidades) · [Stack](#stack) · [Como rodar](#como-rodar) · [Deploy](#deploy) · [Como usar](#como-usar) · [Endpoints](#endpoints) · [Regras](#regras-de-negócio) · [Códigos](#códigos-de-status) · [Modelo de dados](#modelo-de-dados) · [Frontend](#frontend) · [Decisões](#decisões-técnicas) · [Qualidade](#qualidade) · [O que falta](#o-que-falta)

## Sobre o projeto

O sistema registra transações (receitas e despesas), organiza-as em categorias com limite de gastos e acompanha metas com percentual de progresso.

O diferencial é o **multi-usuário**: cada conta vê apenas os próprios dados, filtrados pelo `usuario_id` do token — nunca pelo corpo da requisição. Um **admin** lista usuários e gerencia qualquer conta.

```mermaid
flowchart LR
    subgraph Frontend["Frontend (docs/)"]
        DASH["Dashboard<br/>Saldo • Receitas • Despesas"]
        TRANS["Transações<br/>Filtros: tipo, categoria, período"]
        GOALS["Metas<br/>Progresso + Aportes"]
        CATS["Categorias<br/>Limite + Agregados"]
    end

    subgraph API["API FastAPI (Render)"]
        AUTH["Auth • JWT + Refresh rotativo"]
        USERS["Usuários • Admin"]
        TX["Transações CRUD"]
        CAT["Categorias + Agregados"]
        GOAL["Metas + Aportes"]
        RPT["Relatórios Mensais"]
    end

    DB[("PostgreSQL<br/>Neon")]

    DASH -->|HTTPS| AUTH
    TRANS -->|Bearer JWT| TX
    GOALS -->|Bearer JWT| GOAL
    CATS -->|Bearer JWT| CAT
    USERS -.->|Admin| USERS
    TX & CAT & GOAL & USERS -->|SQLAlchemy| DB
    RPT -->|Bearer JWT| TX
```

**O que o projeto cobre hoje:** autenticação, gestão de conta, CRUD de transações, categorias, metas e relatórios mensais. Ficam de fora recursos como importação/exportação, gráficos, recorrência e painel de administração.

## Funcionalidades

- **Contas:** cadastro, login, perfil, troca de senha, desativação e exclusão (remove dados em cascata).
- **Login:** senha protegida com **Argon2**, access token JWT de 30 min e refresh token de 7 dias com rotação stateless (novos tokens emitidos a cada refresh; tokens antigos expiram naturalmente).
- **Transações:** criar, listar, buscar, atualizar, excluir, com paginação, busca por descrição e filtros por tipo, categoria e período.
- **Categorias:** CRUD com agregados automáticos (saldo, total receitas/despesas, % do limite) e validação de limite > inicial.
- **Metas:** CRUD com aporte progressivo, teto de 100% no progresso e validação de datas/valores.
- **Relatórios:** soma mensal de receitas e despesas com isolamento por usuário.
- **Isolamento:** toda consulta usa o `usuario_id` do token; acesso a dado alheio responde **404**.
- **Auditoria:** timestamps `criado_em` e `atualizado_em` em todas as tabelas.
- **Produção:** migrações com Alembic, CORS restrito, rate limiting e health check.

## Stack

| Camada | Tecnologia |
|---|---|
| Linguagem | Python 3.10+ (testado em 3.14) |
| Framework | FastAPI 0.162 + Uvicorn |
| ORM / banco | SQLAlchemy 2.1 + PostgreSQL (psycopg 3) |
| Validação | Pydantic 2.14 + pydantic-settings |
| Migrações | Alembic 1.20 |
| Autenticação | PyJWT (HS256), pwdlib (Argon2), slowapi |
| Frontend | HTML5, CSS3, JavaScript (módulos ES) |
| Testes | pytest + TestClient sobre PostgreSQL real |
| Deploy | Render (API) + Neon (PostgreSQL) |

## Como rodar

Antes de começar, você precisa de Python 3.10+, PostgreSQL e Git.

```bash
git clone <url-do-repositorio>
cd controle_financeiro

python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
python -c "import secrets; print(secrets.token_hex(32))"
# cole o valor em SECRET_KEY no .env
```

Preencha `SECRET_KEY` com a chave gerada e ajuste `DATABASE_URL` para o seu PostgreSQL local (driver `psycopg` 3). Depois:

```bash
alembic upgrade head    # da raiz do projeto
cd src
uvicorn main:app --reload --port 8000
```

> [!TIP]
> O schema vem das migrações, não de `create_all`. Rode `alembic upgrade head` da raiz (onde está o `alembic.ini`). O Uvicorn roda de dentro de `src/`.
>
> No Windows: `set PYTHONPATH=.` (cmd) ou `$env:PYTHONPATH="."` (PowerShell) se precisar rodar o Alembic de outro local.

Documentação local: **http://localhost:8000/docs**.

<details>
<summary>Variáveis de ambiente e comandos do Alembic</summary>

| Variável | Padrão | Uso |
|---|---|---|
| `SECRET_KEY` | — | Assinatura do JWT (obrigatória) |
| `ALGORITHM` | `HS256` | Algoritmo do token |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Validade do access token |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Validade do refresh token |
| `DATABASE_URL` | — | Conexão PostgreSQL (obrigatória) |
| `TEST_DATABASE_URL` | — | Banco isolado para testes (opcional) |
| `CORS_ORIGINS` | `http://localhost:8800,https://moisesmayyer.github.io` | Origens permitidas, separadas por vírgula |

```bash
alembic upgrade head                              # aplica as migrações pendentes
alembic current                                   # revisão aplicada
alembic history                                   # histórico
alembic revision --autogenerate -m "descricao"    # nova revisão a partir dos models
alembic downgrade -1                              # desfaz a última
```

Para zerar o banco local: `DROP SCHEMA public CASCADE; CREATE SCHEMA public;` e rode `alembic upgrade head` de novo.

</details>

> [!WARNING]
> `.env` contém segredos e é ignorado pelo Git. Nunca faça commit da `SECRET_KEY`, da senha do banco ou de um `.env` real.

### Testes

A suíte usa **PostgreSQL real** e recria o schema a cada teste. Crie o banco uma vez:

```bash
createdb -h localhost -U postgres test_controle_financeiro
pip install -r requirements.txt  # já inclui pytest e httpx
pytest tests/test_routers
```

O `tests/conftest.py` deriva `test_controle_financeiro` a partir de `DATABASE_URL`, aceita `TEST_DATABASE_URL` e só roda se o nome do banco começar com `test_`.

## Deploy

**API — Render**

- **Root directory:** raiz do repositório.
- **Build:** `pip install -r requirements.txt`
- **Start:** `alembic upgrade head && cd src && uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Variáveis:** as mesmas do `.env` (incluindo `DATABASE_URL` do Neon).

> [!IMPORTANT]
> O plano gratuito do Render coloca a API para dormir. A primeira requisição depois de um tempo parada pode levar alguns segundos (**cold start**).

**Banco — Neon**

- PostgreSQL gerenciado, branch `main` para produção.
- `DATABASE_URL` no formato `postgresql+psycopg://user:pass@ep-xxx.region.aws.neon.tech/dbname?sslmode=require`.
- Migrações aplicadas no start do Render via `alembic upgrade head`.

**CORS**

Em produção, mantenha apenas a origem publicada:

```env
CORS_ORIGINS=https://seu-frontend.github.io
```

Para desenvolver localmente, adicione `http://localhost:8800` e `http://127.0.0.1:8800`.

## Como usar

Se o frontend estiver aberto, crie uma conta pela tela de cadastro — ele já entra em seguida. Para testar a API direto:

```bash
# 1. Criar conta
curl -X POST http://localhost:8000/usuarios/ \
  -H "Content-Type: application/json" \
  -d '{"nome": "Ana", "email": "ana@email.com", "senha": "senha123"}'

# 2. Login (form-urlencoded, padrão OAuth2)
curl -X POST http://localhost:8000/auth/login \
  -d "username=ana@email.com&password=senha123"

# 3. Guardar o access token e criar uma transação
TOKEN="cole-o-access-token-aqui"
curl -X POST http://localhost:8000/transacoes/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"descricao": "Salário", "valor": 3000, "tipo": "receita", "data": "2026-10-01"}'
```

<details>
<summary>Exemplos de refresh, categoria com limite, meta e relatórios</summary>

```bash
# Renova o par de tokens (rotação stateless: o refresh antigo expira naturalmente)
curl -X POST http://localhost:8000/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "cole-o-refresh-token"}'

# Categoria com limite de R$ 400 e saldo inicial de R$ 100
curl -X POST http://localhost:8000/categorias/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"nome": "Lazer", "valor_inicial": 100, "valor_limite": 400}'

# Meta com aporte
curl -X POST http://localhost:8000/metas/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"nome": "Viagem", "valor_inicial": 250, "valor_final": 1000, "data_inicio": "2026-10-01", "data_fim": "2026-12-31"}'

curl -X POST http://localhost:8000/metas/1/adicionar-valor \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"valor": 750}'

# Relatório mensal de despesas
curl "http://localhost:8000/relatorios/valor_despesas?ano=2026&mes=10" \
  -H "Authorization: Bearer $TOKEN"
```

</details>

Frontend local (módulos ES precisam de HTTP; `file://` não funciona):

```bash
python -m http.server 8800 --directory docs
```

Abra **http://localhost:8800**.

## Endpoints

As rotas protegidas pedem `Authorization: Bearer <token>`. "Dono" quer dizer que o registro pertence ao usuário logado; se não pertencer, a resposta é **404**.

| Grupo | Método | Rota | Acesso | Descrição |
|---|---|---|---|---|
| Auth | POST | `/auth/login` | público | Autentica e devolve access + refresh |
| Auth | POST | `/auth/refresh` | público | Renova o par de tokens (rotação stateless) |
| Auth | GET | `/auth/me` | autenticado | Usuário do token |
| Usuários | GET | `/usuarios/` | autenticado | Lista paginada: admin vê todos; comum, só a si |
| Usuários | GET | `/usuarios/{id}` | dono ou admin | Busca usuário |
| Usuários | POST | `/usuarios/` | público | Cria conta (`201`) |
| Usuários | PUT | `/usuarios/{id}` | dono ou admin | Edita nome, e-mail e senha; `ativo` só admin |
| Usuários | PATCH | `/usuarios/{id}/cancelar` | dono ou admin | Desativa a conta |
| Usuários | DELETE | `/usuarios/{id}` | dono ou admin | Remove conta e dados (`204`) |
| Transações | GET | `/transacoes/` | autenticado | Lista paginada com filtros |
| Transações | GET | `/transacoes/{id}` | dono | Busca |
| Transações | POST | `/transacoes/` | autenticado | Cria (`201`) |
| Transações | PUT | `/transacoes/{id}` | dono | Atualiza; `categoria_id: null` desvincula |
| Transações | DELETE | `/transacoes/{id}` | dono | Remove |
| Categorias | GET | `/categorias/` | autenticado | Lista paginada com agregados |
| Categorias | GET | `/categorias/{id}` | dono | Busca com agregados |
| Categorias | POST | `/categorias/` | autenticado | Cria (`201`) |
| Categorias | PUT | `/categorias/{id}` | dono | Atualiza |
| Categorias | DELETE | `/categorias/{id}` | dono | Remove se não houver transações |
| Metas | GET | `/metas/` | autenticado | Lista paginada com progresso |
| Metas | GET | `/metas/{id}` | dono | Busca |
| Metas | POST | `/metas/` | autenticado | Cria (`201`) |
| Metas | PUT | `/metas/{id}` | dono | Atualiza |
| Metas | DELETE | `/metas/{id}` | dono | Remove |
| Metas | POST | `/metas/{id}/adicionar-valor` | dono | Adiciona ao progresso |
| Relatórios | GET | `/relatorios/receitas` | autenticado | Lista receitas, com paginação e busca |
| Relatórios | GET | `/relatorios/despesas` | autenticado | Lista despesas, com paginação e busca |
| Relatórios | GET | `/relatorios/valor_receita` | autenticado | Soma das receitas do mês (`ano`, `mes`) |
| Relatórios | GET | `/relatorios/valor_despesas` | autenticado | Soma das despesas do mês (`ano`, `mes`) |
| Sistema | GET | `/` | público | Nome e versão da API |
| Sistema | GET | `/health` | público | Health check |

`GET /transacoes/`, `/categorias/`, `/metas/`, `/usuarios/` e `/relatorios/` aceitam `skip` (padrão `0`), `limit` (padrão `10`, máx `100`) e `busca`. Transações têm também `tipo`, `categoria_id`, `data_inicio`, `data_fim`. A resposta é `{ "items": [...], "total": 42, "skip": 0, "limit": 10 }`.

## Regras de negócio

| Recurso | Regra |
|---|---|
| Usuário | Nome 3–100 chars; e-mail válido e único; senha 6+ chars. Só admin altera `ativo`; `admin` não é editável pela API |
| Transação | `valor > 0`; `tipo` receita/despesa; `data` obrigatória; `descricao` 1–255 chars. Categoria deve existir e pertencer ao usuário |
| Categoria | Nome único por usuário; `valor_limite > valor_inicial > 0`; não removível com transações; `saldo = inicial + receitas − despesas`; teto de 100% no `% limite` |
| Meta | `valor_inicial >= 0`; `valor_final >= valor_inicial > 0`; `data_fim > data_inicio` quando ambas; aporte positivo limitado ao `valor_final`; teto de 100% no `%` |

> [!CAUTION]
> A exclusão da conta é definitiva e remove todas as transações, categorias, metas e sessões. A API não oferece recuperação nem lixeira.

## Modelo de dados

```text
usuarios (1) ──< categorias
               ──< transacoes
               ──< metas
categorias (1) ──< transacoes
```

| Tabela | Campos principais |
|---|---|
| `usuarios` | `id`, `nome`, `email` (único), `senha_hash`, `ativo`, `admin`, `criado_em`, `atualizado_em` |
| `categorias` | `id`, `nome`, `valor_inicial`, `valor_limite`, `usuario_id`, `criado_em`, `atualizado_em` |
| `transacoes` | `id`, `descricao`, `valor`, `tipo`, `data`, `categoria_id` (opcional), `usuario_id`, `criado_em`, `atualizado_em` |
| `metas` | `id`, `nome`, `valor_inicial`, `valor_final`, `data_inicio`, `data_fim`, `usuario_id`, `criado_em`, `atualizado_em` |

- `usuarios.email` é único e indexado; `categorias` tem `UNIQUE (usuario_id, nome)`.
- `usuario_id` é `NOT NULL` e indexado em `categorias`, `transacoes` e `metas`; remover um usuário apaga seus dados em cascata pelo ORM.
- `transacoes.categoria_id` é opcional e referencia `categorias.id`; transações sem categoria não entram nos agregados.
- O schema é versionado pelo Alembic; a revisão inicial (`ca0004d3e874`) cria as quatro tabelas, os índices e as constraints. A revisão `aff658fec782` adiciona timestamps de auditoria. Aplique com `alembic upgrade head`.

## Estrutura do projeto

```text
.
├── alembic.ini                  # Configuração do Alembic
├── migrations/                  # Migrações do banco
│   ├── env.py
│   └── versions/                # Revisões
├── src/
│   ├── main.py                  # App e routers
│   ├── dados/
│   │   ├── config.py            # Settings do .env
│   │   ├── database.py          # Engine, Base e SessionLocal
│   │   ├── dependencies.py      # get_db e verificar_token
│   │   ├── security.py          # Argon2 e JWT
│   │   ├── limiter.py           # Rate limiting
│   │   ├── models/              # Tabelas SQLAlchemy
│   │   │   ├── __init__.py
│   │   │   ├── mixins.py        # TimestampMixin
│   │   │   ├── usuario.py
│   │   │   ├── transacao.py
│   │   │   ├── categoria.py
│   │   │   └── meta.py
│   │   └── schemas/             # Schemas Pydantic
│   │       ├── usuario.py
│   │       ├── token.py
│   │       ├── transacao.py
│   │       ├── categoria.py
│   │       ├── meta.py
│   │       └── relatorio.py
│   └── rotas/
│       ├── auth/crud.py         # Login, refresh, /me
│       ├── usuarios/crud.py
│       ├── transacoes/crud.py
│       ├── categorias/crud.py   # Agregados
│       ├── metas/crud.py        # Aporte
│       └── relatorios/crud.py
├── tests/
│   ├── conftest.py              # Fixtures e banco de teste
│   └── test_routers/            # 249 testes: auth, usuários, categorias, transações, metas, relatórios
├── docs/                        # Frontend (HTML/CSS/JS)
├── pyproject.toml
├── requirements.txt
└── .env.example                 # Exemplo de variáveis de ambiente (criar manualmente)
```

## Frontend

> [!NOTE]
> O frontend foi feito com ajuda de inteligência artificial. Como o foco do projeto é o **backend**, a interface serve apenas como demonstração visual para testar a API.

## Decisões técnicas

**pwdlib/Argon2 em vez de passlib.** `passlib` depende do `crypt`, removido no Python 3.13; `pwdlib` mantém o Argon2 sem essa dependência.

**Validadores nos schemas `*Create`, não no `*Base`.** Os `*Response` herdam de `*Base`; validar ali rodaria após o `commit` — uma meta em 100% retornava `500` com o dado salvo.

**`response_model` nas rotas de retorno.** Sem ele, o FastAPI serializa o objeto SQLAlchemy inteiro; uma resposta chegou a expor `senha_hash`.

**Isolamento por `usuario_id` na query, com `404`.** Evita confirmar dados de outra conta; `/usuarios` usa `403`.

**Alembic em vez de `create_all`.** O schema é versionado por migrações; a aplicação não cria tabelas na inicialização.

**`float` em vez de `Decimal`.** Controle pessoal, não contabilidade; em produção, `Decimal` ou centavos evitariam arredondamentos.

**Refresh token rotativo (stateless).** A cada uso do `/auth/refresh`, novos tokens são emitidos; o refresh antigo expira pelo tempo (`exp`). Não há armazenamento nem revogação no servidor.

**TimestampMixin para auditoria.** `criado_em` e `atualizado_em` com `server_default=func.now()` e `onupdate=func.now()` em todas as tabelas.

## Qualidade

- **Tipagem:** `mypy --ignore-missing-imports --explicit-package-bases src` → *Success: no issues found in 29 source files*
- **Testes:** `pytest` + `TestClient` em PostgreSQL real, **249 testes** cobrindo auth, isolamento, limites, metas e relatórios
- **Cobertura:** Módulos de rotas com **100% de linhas e branches**; pacote `src` em **99%** (fora `/`, `/health` e ramo de `sub` não numérico)

## O que falta

Em ordem de prioridade:

**Essencial**

- [x] Suíte com `pytest` + `TestClient` (249 testes)
- [x] Paginação e filtros (`tipo`, `data_inicio`/`data_fim`, `categoria_id`, `skip`/`limit`)
- [x] Relatório mensal de receitas e despesas

**Qualidade**

- [x] Migrations com Alembic
- [x] `criado_em` / `atualizado_em` (auditoria)
- [x] `model_config = ConfigDict(from_attributes=True)` (Pydantic v2)

**Produção**

- [x] CORS configurado
- [x] Refresh token rotativo
- [x] Rate limiting
- [x] Deploy com link público (Render + Neon)
- [X] CI no GitHub Actions com pytest

## Status do projeto

O projeto está no ar: API no Render, banco no Neon e CRUD completo com JWT sobre PostgreSQL. Autenticação, isolamento por usuário, paginação, filtros, agregados de categorias, metas com progresso e relatórios mensais funcionando. A suíte tem 249 testes, mypy limpo e cobertura alta. Próximos passos: CI no GitHub Actions e versão do `.env.example`.