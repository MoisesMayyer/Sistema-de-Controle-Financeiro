# Controle Financeiro API

API REST de controle financeiro pessoal **multi-usuário**, com autenticação JWT e isolamento de dados por usuário.

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.162-009688?logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.1-D71F00)
![Pydantic](https://img.shields.io/badge/Pydantic-2.14-E92063)
![PyJWT](https://img.shields.io/badge/PyJWT-2.15-000000?logo=jsonwebtokens&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-4169E1?logo=postgresql&logoColor=white)
![Alembic](https://img.shields.io/badge/Alembic-1.20-6BA81E)
![mypy](https://img.shields.io/badge/mypy-passing-2A6DB0)
![testes](https://img.shields.io/badge/testes-241%20passando-brightgreen)

> **Projeto de estudo e portfólio.** Nasceu como um controle financeiro de terminal em JSON e foi reescrito para aprender **FastAPI**, **SQLAlchemy**, **Pydantic**, **PostgreSQL** e **Alembic**.

## Sumário

- [Sobre o projeto](#sobre-o-projeto)
- [Funcionalidades](#funcionalidades)
- [Stack](#stack)
- [Como rodar](#como-rodar)
- [Como usar](#como-usar)
- [Endpoints](#endpoints)
- [Regras de negócio](#regras-de-negócio)
- [Códigos de status](#códigos-de-status)
- [Modelo de dados](#modelo-de-dados)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Decisões técnicas](#decisões-técnicas)
- [Qualidade](#qualidade)
- [O que falta](#o-que-falta)
- [Status do projeto](#status-do-projeto)

## Sobre o projeto

O sistema registra transações (receitas e despesas), organiza-as em categorias com limite de gastos e acompanha metas com percentual de progresso.

O diferencial é o **multi-usuário**: cada conta vê apenas os próprios dados, filtrados pelo `usuario_id` do token — nunca pelo corpo da requisição. Um **admin** lista usuários e gerencia qualquer conta.

## Funcionalidades

- Cadastro, login e perfil (`/auth`, `/usuarios`)
- Senhas em **Argon2** e autenticação **JWT** (OAuth2 Password Flow)
- CRUD de **transações**, **categorias** (agregados e limite) e **metas** (aporte e progresso)
- Isolamento por usuário e papel de **admin**
- Desativação de conta, com invalidação imediata do token

## Stack

| Camada | Tecnologia |
|---|---|
| Linguagem | Python 3.10+ (testado em 3.14) |
| Framework | FastAPI 0.162 |
| ORM | SQLAlchemy 2.1 |
| Validação/serialização | Pydantic 2.14 + pydantic-settings |
| Banco | PostgreSQL 18 |
| Migrações | Alembic 1.20 |
| Servidor | Uvicorn |
| Hash de senha | pwdlib (Argon2) |
| Token | PyJWT (HS256) |
| Qualidade | mypy + pytest/TestClient (PostgreSQL) |

## Como rodar

**Requisitos:** Python 3.10 ou superior, PostgreSQL 18 e `git`.

```bash
# 1. Clone
git clone <url-do-repositorio>
cd controle-financeiro

# 2. Ambiente virtual
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Dependências
pip install -r requirements.txt

# 4. Configuração
cp .env.example .env
python -c "import secrets; print(secrets.token_hex(32))"
# cole o valor em SECRET_KEY no .env
```

O `.env` deve ficar assim:

```env
DATABASE_URL=postgresql+psycopg://postgres:senha@localhost:5432/controle_financeiro
SECRET_KEY=<a chave gerada acima>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

```bash
# 5. Banco e migrações (a partir da raiz do projeto)
createdb -h localhost -U postgres controle_financeiro  # se ainda não existir
alembic upgrade head

# 6. Servidor (de dentro de src/)
cd src
uvicorn main:app --reload
```

Acesse **http://localhost:8000/docs** para a documentação interativa.

> **Banco:** PostgreSQL. O schema é criado e versionado pelas migrações do Alembic (`alembic upgrade head`); a aplicação não executa `create_all`.

### Primeiro usuário admin

Nenhuma rota promove usuários a admin. Defina o primeiro direto no banco, após criar a conta pela API:

```bash
# a partir da raiz do projeto (use as credenciais do DATABASE_URL)
psql -h localhost -U postgres -d controle_financeiro -c "UPDATE usuarios SET admin = 1 WHERE id = 1;"
```

### Testes

A suíte usa **PostgreSQL real** e recria as tabelas a cada teste (`drop_all`/`create_all`), sem tocar no banco de desenvolvimento. Crie o banco de teste uma vez:

```bash
createdb -h localhost -U postgres test_controle_financeiro
```

Com o `.env` configurado e as dependências instaladas:

```bash
pytest tests/test_routers
```

O `tests/conftest.py` deriva `test_controle_financeiro` a partir de `DATABASE_URL` e aceita `TEST_DATABASE_URL` para sobrescrever. Por segurança, a suíte só roda se o nome do banco começar com `test_`.

> A suíte oficial tem **241 testes** em `tests/test_routers/`: autenticação (15), usuários (55), categorias (47), transações (52), metas (46) e relatórios (26). O arquivo local `tests/test_exemplos_fixtures.py` é um rascunho didático de fixtures não versionado; se existir, `pytest` o inclui (253 no total).

## Como usar

### 1. Criar uma conta

```bash
curl -X POST http://localhost:8000/usuarios/ \
  -H "Content-Type: application/json" \
  -d '{"nome": "Ana", "email": "ana@email.com", "senha": "senha123"}'
```

```json
{"id": 1, "nome": "Ana", "email": "ana@email.com", "ativo": true, "admin": false}
```

### 2. Fazer login e obter o token

O login usa `application/x-www-form-urlencoded` (OAuth2), não JSON:

```bash
curl -X POST http://localhost:8000/auth/login \
  -d "username=ana@email.com&password=senha123"
```

```json
{"access_token": "eyJhbGciOiJIUzI1NiIs...", "token_type": "bearer"}
```

### 3. Usar o token nas rotas protegidas

```bash
TOKEN="cole-o-access-token-aqui"

curl http://localhost:8000/transacoes/ \
  -H "Authorization: Bearer $TOKEN"
```

No Swagger, use **Authorize** com e-mail e senha.

### 4. Fluxo completo: categoria, transação e agregados

```bash
# Categoria com limite de R$ 400 e saldo inicial de R$ 100
curl -X POST http://localhost:8000/categorias/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"nome": "Lazer", "valor_inicial": 100, "valor_limite": 400}'

# Despesa de R$ 50 nessa categoria
curl -X POST http://localhost:8000/transacoes/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"descricao": "Cinema", "valor": 50, "tipo": "despesa", "data": "2026-10-19", "categoria_id": 1}'
```

Ao buscar a categoria, os agregados vêm calculados:

```bash
curl http://localhost:8000/categorias/1 -H "Authorization: Bearer $TOKEN"
```

```json
{
  "nome": "Lazer",
  "valor_inicial": 100.0,
  "valor_limite": 400.0,
  "id": 1,
  "usuario_id": 1,
  "total_despesas": 50.0,
  "total_receitas": 0.0,
  "saldo": 50.0,
  "porcentagem_limite": 12.5
}
```

### 5. Meta com aporte

```bash
curl -X POST http://localhost:8000/metas/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"nome": "Viagem", "valor_inicial": 250, "valor_final": 1000, "data_inicio": "2026-10-01", "data_fim": "2026-12-31"}'

curl -X POST http://localhost:8000/metas/1/adicionar-valor \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"valor": 750}'
```

A resposta traz `"porcentagem": 100.0`.

## Endpoints

Transações, categorias, metas e as rotas protegidas de usuários exigem `Authorization: Bearer <token>`. Nas três primeiras, registro de outro dono responde **404**; em `/usuarios`, **403**.

### Autenticação

| Método | Rota | Acesso | Descrição |
|---|---|---|---|
| POST | `/auth/login` | público | Login via form; devolve o JWT |
| GET | `/auth/me` | autenticado | Usuário do token |

### Usuários

| Método | Rota | Acesso | Descrição |
|---|---|---|---|
| GET | `/usuarios/` | autenticado | Lista paginada: admin vê todos; comum, só a si |
| GET | `/usuarios/{id}` | dono ou admin | Busca usuário |
| POST | `/usuarios/` | público | Cria conta (`201`) |
| PUT | `/usuarios/{id}` | dono ou admin | Edita nome, e-mail e senha; `ativo` só admin |
| PATCH | `/usuarios/{id}/cancelar` | dono ou admin | Desativa (`ativo = false`) |
| DELETE | `/usuarios/{id}` | dono ou admin | Remove conta e dados (`204`) |

### Transações

| Método | Rota | Acesso | Descrição |
|---|---|---|---|
| GET | `/transacoes/` | autenticado | Lista paginada com filtros |
| GET | `/transacoes/{id}` | dono | Busca |
| POST | `/transacoes/` | autenticado | Cria (`201`) |
| PUT | `/transacoes/{id}` | dono | Atualiza; `categoria_id: null` desvincula |
| DELETE | `/transacoes/{id}` | dono | Remove |

### Categorias

| Método | Rota | Acesso | Descrição |
|---|---|---|---|
| GET | `/categorias/` | autenticado | Lista paginada com agregados |
| GET | `/categorias/{id}` | dono | Busca com agregados |
| POST | `/categorias/` | autenticado | Cria (`201`) |
| PUT | `/categorias/{id}` | dono | Atualiza |
| DELETE | `/categorias/{id}` | dono | Remove se não houver transações |

### Metas

| Método | Rota | Acesso | Descrição |
|---|---|---|---|
| GET | `/metas/` | autenticado | Lista paginada com progresso |
| GET | `/metas/{id}` | dono | Busca |
| POST | `/metas/` | autenticado | Cria (`201`) |
| PUT | `/metas/{id}` | dono | Atualiza |
| DELETE | `/metas/{id}` | dono | Remove |
| POST | `/metas/{id}/adicionar-valor` | dono | Adiciona ao progresso |

### Relatórios

| Método | Rota | Acesso | Descrição |
|---|---|---|---|
| GET | `/relatorios/receitas` | autenticado | Lista receitas, com paginação e busca |
| GET | `/relatorios/despesas` | autenticado | Lista despesas, com paginação e busca |
| GET | `/relatorios/valor_receita` | autenticado | Soma das receitas do mês (`ano`, `mes`) |
| GET | `/relatorios/valor_despesas` | autenticado | Soma das despesas do mês (`ano`, `mes`) |

### Sistema

| Método | Rota | Acesso | Descrição |
|---|---|---|---|
| GET | `/` | público | Nome e versão da API |
| GET | `/health` | público | Health check |

### Paginação e filtros

Todas as listagens (`/usuarios/`, `/transacoes/`, `/categorias/`, `/metas/`, `/relatorios/receitas` e `/relatorios/despesas`) retornam um envelope:

```json
{"items": [], "total": 42, "skip": 0, "limit": 10}
```

| Parâmetro | Onde | Descrição |
|---|---|---|
| `skip` | todas | Quantos registros pular (padrão `0`) |
| `limit` | todas | Tamanho da página (padrão `10`, máximo `100`) |
| `busca` | todas | Trecho de nome, descrição ou e-mail, sem diferenciar maiúsculas |
| `tipo` | transações | `receita` ou `despesa` |
| `categoria_id` | transações | Filtra por categoria |
| `data_inicio` / `data_fim` | transações | Período inclusivo (`AAAA-MM-DD`) |

`skip` negativo ou `limit` fora de `1..100` retornam `422`; `data_inicio` maior que `data_fim` retorna `400`.

```bash
curl "http://localhost:8000/transacoes/?tipo=despesa&data_inicio=2026-10-01&data_fim=2026-10-31&skip=0&limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

### Relatórios mensais

`/relatorios/valor_receita` e `/relatorios/valor_despesas` exigem `ano` (`2000..2100`) e `mes` (`1..12`) e retornam apenas o total do período:

```json
{"valor_total": 1500.5}
```

```bash
curl "http://localhost:8000/relatorios/valor_despesas?ano=2026&mes=10" \
  -H "Authorization: Bearer $TOKEN"
```

Mês sem lançamentos retorna `{"valor_total": 0.0}`.

## Regras de negócio

| Recurso | Regra |
|---|---|
| Usuário | Nome de 3 a 100 caracteres; e-mail válido e único; senha com 6+ caracteres. Só admin altera `ativo`; `admin` não é editável pela API |
| Transação | `valor > 0`; `tipo` `receita`/`despesa`; `data` obrigatória; `descricao` de 1 a 255 caracteres. Categoria, quando informada, deve existir e pertencer ao usuário |
| Categoria | Nome único por usuário; `valor_limite > valor_inicial` e `> 0`; não removível com transações; `saldo = inicial + receitas − despesas`; teto de 100% no `porcentagem_limite` |
| Meta | `valor_inicial >= 0`; `valor_final >= valor_inicial` e `> 0`; `data_fim` posterior a `data_inicio` quando ambas forem informadas; aporte positivo e limitado ao `valor_final`; teto de 100% na `porcentagem` |

## Códigos de status

| Código | Quando acontece |
|---|---|
| `200` | Leitura, edição e remoção de transação/categoria/meta, cancelamento e aporte |
| `201` | Criação de usuário, transação, categoria ou meta |
| `204` | Remoção de usuário (sem corpo) |
| `400` | E-mail/categoria duplicados, categoria inexistente ou de outro dono, categoria com transações, limites/datas inválidos na edição, período invertido nos filtros, aporte acima do `valor_final` |
| `401` | Sem token, token inválido/expirado, usuário inativo ou credenciais incorretas |
| `403` | `/usuarios` de outro dono ou alteração de `ativo` sem ser admin |
| `404` | Recurso inexistente ou de outro usuário em transações, categorias e metas |
| `422` | Payload inválido pelo Pydantic, incluindo limites inválidos na criação |

## Modelo de dados

```
usuarios (1) ──< categorias
             ──< transacoes
             ──< metas
categorias (1) ──< transacoes
```

| Tabela | Campos |
|---|---|
| `usuarios` | `id`, `nome`, `email` (único), `senha_hash`, `ativo`, `admin` |
| `categorias` | `id`, `nome`, `valor_inicial`, `valor_limite`, `usuario_id` |
| `transacoes` | `id`, `descricao`, `valor`, `tipo`, `data`, `categoria_id` (opcional), `usuario_id` |
| `metas` | `id`, `nome`, `valor_inicial`, `valor_final`, `data_inicio`, `data_fim`, `usuario_id` |

- `usuarios.email` é único e indexado; `categorias` tem `UNIQUE (usuario_id, nome)`.
- `usuario_id` é `NOT NULL` e indexado em `categorias`, `transacoes` e `metas`; remover um usuário apaga seus dados em cascata pelo ORM.
- `transacoes.categoria_id` é opcional e referencia `categorias.id`; transações sem categoria não entram nos agregados.
- O schema é versionado pelo Alembic; a revisão inicial (`ca0004d3e874`) cria as quatro tabelas, os índices e as constraints. Aplique com `alembic upgrade head`.

## Estrutura do projeto

```
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
│   │   ├── models/              # Tabelas SQLAlchemy
│   │   │   ├── usuario.py
│   │   │   ├── transacao.py
│   │   │   ├── categoria.py
│   │   │   └── meta.py
│   │   └── schemas/             # Schemas Pydantic
│   │       ├── usuario.py
│   │       ├── token.py
│   │       ├── transacao.py
│   │       ├── categoria.py
│   │       └── meta.py
│   └── rotas/
│       ├── auth/crud.py         # Login e /me
│       ├── usuarios/crud.py
│       ├── transacoes/crud.py
│       ├── categorias/crud.py   # Agregados
│       └── metas/crud.py        # Aporte
├── tests/
│   ├── conftest.py              # Fixtures e banco de teste
│   └── test_routers/
│       ├── test_auth.py
│       ├── test_usuarios.py
│       ├── test_categorias.py
│       ├── test_transacoes.py
│       └── test_metas.py
├── pyproject.toml               # Configuração do pytest
├── requirements.txt
└── .env.example
```

## Decisões técnicas

**pwdlib/Argon2 em vez de passlib.** `passlib` depende do `crypt`, removido no Python 3.13; `pwdlib` mantém o Argon2 sem essa dependência.

**Validadores nos schemas `*Create`, não no `*Base`.** Os `*Response` herdam de `*Base`; validar ali rodaria após o `commit` — uma meta em 100% retornava `500` com o dado salvo.

**`response_model` nas rotas de retorno.** Sem ele, o FastAPI serializa o objeto SQLAlchemy inteiro; uma resposta chegou a expor `senha_hash`.

**Isolamento por `usuario_id` na query, com `404`.** Evita confirmar dados de outra conta; `/usuarios` usa `403`.

**Alembic em vez de `create_all`.** O schema é versionado por migrações; a aplicação não cria tabelas na inicialização.

**`float` em vez de `Decimal`.** Controle pessoal, não contabilidade; em produção, `Decimal` ou centavos evitariam arredondamentos.

## Qualidade

Verificação de tipos com mypy:

```bash
mypy --ignore-missing-imports --explicit-package-bases src
# Success: no issues found in 29 source files
```

A suíte oficial tem **241 testes** com `pytest` + `TestClient` sobre PostgreSQL:

- **autenticação (15):** login válido/inválido, conta desativada, token ausente/inválido/expirado/sem `sub` e usuário inexistente ou inativo;
- **usuários (55):** criação e validação, e-mail duplicado, isolamento por dono, admin, listagem paginada e busca, atualização parcial e de senha, cancelamento, exclusão e cascade dos dados;
- **categorias (47):** CRUD, nome único por usuário, validação dos limites, listagem paginada e busca, agregados de receitas/despesas, saldo e teto de 100%;
- **transações (52):** CRUD, tipos válidos, validações de valor/data, listagem paginada com busca e filtros de tipo, categoria e período, categoria do próprio usuário e desvinculação;
- **metas (46):** CRUD, validação de valores/datas, listagem paginada e busca, aporte limitado ao `valor_final` e progresso com teto de 100%;
- **relatórios (26):** listagem de receitas/despesas por tipo com busca, soma mensal de receitas e despesas, mês vazio, isolamento por usuário, virada de dezembro e parâmetros inválidos.

Os módulos de rotas (`auth`, `usuarios`, `categorias`, `transacoes` e `metas`) têm **100% de cobertura de linhas e branches**; no pacote `src`, a cobertura total é **99%** (ficam de fora `/`, `/health` e o ramo de `sub` não numérico em `dependencies.py`).

## O que falta

Itens conhecidos, em ordem de prioridade:

**Essencial**

- [X] Suíte com `pytest` + `TestClient` (241 testes: autenticação, isolamento, limites e metas)
- [X] Paginação e filtros (`tipo`, `data_inicio`/`data_fim`, `categoria_id`, `skip`/`limit`)
- [X] Relatório mensal de receitas e despesas

**Qualidade**
- [X] Migrations com Alembic
- [X] `criado_em` / `atualizado_em` (auditoria)
- [X] `model_config = ConfigDict(from_attributes=True)` no lugar do `class Config` (depreciado no Pydantic v2)

**Produção**

- [ ] CI no GitHub Actions com mypy e pytest
- [X] CORS configurado
- [ ] Refresh token e revogação de access token
- [ ] Rate limiting no login
- [ ] Deploy com link público

## Status do projeto

Em desenvolvimento, com autenticação JWT, isolamento por usuário, paginação e filtros, CRUD completo de transações, categorias e metas e relatórios mensais sobre PostgreSQL. A suíte oficial tem 241 testes e os módulos de rotas estão cobertos em 100% de linhas e branches; CI e melhorias de produção são os próximos passos.
