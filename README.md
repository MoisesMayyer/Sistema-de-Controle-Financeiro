# Controle Financeiro API

API REST de controle financeiro pessoal **multi-usuário**, com autenticação JWT e isolamento de dados por usuário.

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.143-009688?logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.1-D71F00)
![Pydantic](https://img.shields.io/badge/Pydantic-2.14-E92063)
![mypy](https://img.shields.io/badge/mypy-passing-2A6DB0)
![testes](https://img.shields.io/badge/testes-automatizados%20em%20constru%C3%A7%C3%A3o-yellow)

> **Projeto de estudo e portfólio.** Este projeto nasceu como meu primeiro programa em Python (um controle financeiro de terminal, com JSON). Ele foi reescrito do zero para aprender **FastAPI**, **SQLAlchemy** e **Pydantic** — e o que está aqui é o resultado dessa segunda versão.

## Sumário

- [Sobre o projeto](#sobre-o-projeto)
- [Funcionalidades](#funcionalidades)
- [Stack](#stack)
- [Como rodar](#como-rodar)
- [Como usar](#como-usar)
- [Endpoints](#endpoints)
- [Regras de negócio](#regras-de-negócio)
- [Modelo de dados](#modelo-de-dados)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Decisões técnicas](#decisões-técnicas)
- [Qualidade](#qualidade)
- [O que falta](#o-que-falta)

## Sobre o projeto

O sistema permite registrar transações (receitas e despesas), organizá-las em categorias com limite de gastos e acompanhar metas financeiras com percentual de progresso.

O recorte principal é o **multi-usuário de verdade**: cada conta só enxerga os próprios dados. Toda consulta é filtrada pelo `usuario_id` extraído do token — não pelo que o cliente envia no corpo da requisição. Existe também um papel de **admin**, que pode listar usuários e gerenciar qualquer conta.

A API é servida com documentação interativa automática em `/docs` (Swagger UI) e `/redoc`.

## Funcionalidades

- Cadastro, login e consulta do próprio perfil (`/auth`, `/usuarios`)
- Senhas armazenadas com **Argon2** e autenticação via **JWT** (OAuth2 Password Flow)
- CRUD de **transações** com tipo (`receita`/`despesa`), valor e data
- CRUD de **categorias** com limite de gastos e agregados calculados na resposta (total de receitas, total de despesas, saldo e % do limite)
- CRUD de **metas** com aporte de valor e percentual de progresso
- Isolamento por usuário em todas as rotas de dados
- Papel de **admin**, com visibilidade sobre todos os usuários
- Desativação de conta (`PATCH /usuarios/{id}/cancelar`), que invalida o acesso imediatamente

## Stack

| Camada | Tecnologia |
|---|---|
| Linguagem | Python 3.10+ (testado em 3.14) |
| Framework | FastAPI 0.143 |
| ORM | SQLAlchemy 2.1 |
| Validação/serialização | Pydantic 2.14 + pydantic-settings |
| Banco | SQLite |
| Servidor | Uvicorn |
| Hash de senha | pwdlib (Argon2) |
| Token | PyJWT (HS256) |
| Qualidade | mypy |

## Como rodar

**Requisitos:** Python 3.10 ou superior e `git`.

```bash
# 1. Clone e entre no projeto
git clone <url-do-repositorio>
cd controle-financeiro

# 2. Crie e ative o ambiente virtual
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Instale as dependências (inclui as de desenvolvimento)
pip install -e ".[dev]"

# 4. Crie o arquivo de configuração
cp .env.example .env
python -c "import secrets; print(secrets.token_hex(32))"
# cole o valor gerado em SECRET_KEY, dentro do .env
```

O `.env` deve ficar assim:

```env
BANCODADOS=sqlite:///./financeiro.db
SECRET_KEY=<a chave gerada acima>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

```bash
# 5. Suba o servidor (de dentro de src/)
cd src
uvicorn main:app --reload
```

Acesse **http://localhost:8000/docs** para a documentação interativa.

> **Atenção ao diretório:** o caminho do banco é relativo (`./financeiro.db`). Rodando `uvicorn` de dentro de `src/`, o arquivo nasce em `src/financeiro.db`. Rodando da raiz, nasce outro banco na raiz — por isso o comando acima muda de diretório antes de subir o servidor.

O banco e as tabelas são criados automaticamente na primeira execução. Para **resetar** os dados, pare o servidor e apague `src/financeiro.db`; ele será recriado vazio no próximo start.

### Primeiro usuário admin

Nenhuma rota promove usuários a admin (para evitar autopromoção). O primeiro admin é definido direto no banco, após criar a conta pela API:

```bash
# a partir da raiz do projeto
sqlite3 src/financeiro.db "UPDATE usuarios SET admin = 1 WHERE id = 1;"
```

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

O login usa `application/x-www-form-urlencoded` (padrão OAuth2), não JSON:

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

No Swagger (`/docs`), clique em **Authorize**, informe e-mail e senha e o próprio Swagger passa a enviar o token em todas as chamadas.

### 4. Fluxo completo: categoria, transação e agregados

```bash
# Categoria de lazer com limite de R$ 400 e saldo inicial de R$ 100
curl -X POST http://localhost:8000/categorias/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"nome": "Lazer", "valor_inicial": 100, "valor_limite": 400}'

# Uma despesa de R$ 50 nessa categoria
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

Todas as rotas de dados exigem `Authorization: Bearer <token>`. "Dono" significa que o registro precisa pertencer ao usuário autenticado; caso contrário a API responde **404** (para não revelar a existência de dados de outra conta).

### Autenticação

| Método | Rota | Acesso | Descrição |
|---|---|---|---|
| POST | `/auth/login` | público | Recebe `username` (e-mail) e `password` via form e devolve o JWT |
| GET | `/auth/me` | autenticado | Dados do usuário do token |

### Usuários

| Método | Rota | Acesso | Descrição |
|---|---|---|---|
| GET | `/usuarios/` | autenticado | Admin vê todos; usuário comum vê apenas a si mesmo |
| GET | `/usuarios/{id}` | dono ou admin | Busca um usuário |
| POST | `/usuarios/` | público | Cria conta (`201`) |
| PUT | `/usuarios/{id}` | dono ou admin | Edita nome, e-mail e senha; `ativo` só admin altera |
| PATCH | `/usuarios/{id}/cancelar` | dono ou admin | Desativa a conta (`ativo = false`) |
| DELETE | `/usuarios/{id}` | dono ou admin | Remove a conta e seus dados (`204`) |

### Transações

| Método | Rota | Acesso | Descrição |
|---|---|---|---|
| GET | `/transacoes/` | autenticado | Lista as transações do usuário |
| GET | `/transacoes/{id}` | dono | Busca uma transação |
| POST | `/transacoes/` | autenticado | Cria transação (`201`) |
| PUT | `/transacoes/{id}` | dono | Atualiza (envie `"categoria_id": null` para desvincular) |
| DELETE | `/transacoes/{id}` | dono | Remove |

### Categorias

| Método | Rota | Acesso | Descrição |
|---|---|---|---|
| GET | `/categorias/` | autenticado | Lista com agregados |
| GET | `/categorias/{id}` | dono | Busca com agregados |
| POST | `/categorias/` | autenticado | Cria categoria (`201`) |
| PUT | `/categorias/{id}` | dono | Atualiza |
| DELETE | `/categorias/{id}` | dono | Remove, se não houver transações vinculadas |

### Metas

| Método | Rota | Acesso | Descrição |
|---|---|---|---|
| GET | `/metas/` | autenticado | Lista com percentual de progresso |
| GET | `/metas/{id}` | dono | Busca uma meta |
| POST | `/metas/` | autenticado | Cria meta (`201`) |
| PUT | `/metas/{id}` | dono | Atualiza |
| DELETE | `/metas/{id}` | dono | Remove |
| POST | `/metas/{id}/adicionar-valor` | dono | Adiciona valor ao progresso |

### Sistema

| Método | Rota | Acesso | Descrição |
|---|---|---|---|
| GET | `/` | público | Nome e versão da API |
| GET | `/health` | público | Health check |

## Regras de negócio

| Recurso | Regra |
|---|---|
| Usuário | Nome entre 3 e 100 caracteres; e-mail válido e único; senha com no mínimo 6 caracteres |
| Usuário | Só admin altera `ativo`; `admin` nunca é editável pela API |
| Transação | `valor > 0`; `tipo` em `receita`/`despesa`; `data` obrigatória; `descricao` de 1 a 255 caracteres |
| Transação | A categoria informada precisa existir **e pertencer ao mesmo usuário** |
| Categoria | Nome único **por usuário** (dois usuários podem ter "Lazer") |
| Categoria | `valor_limite > valor_inicial` e `valor_limite > 0` |
| Categoria | Não pode ser removida enquanto tiver transações vinculadas |
| Categoria | `saldo = valor_inicial + receitas − despesas`; `porcentagem_limite` tem teto de 100% |
| Meta | `valor_inicial >= 0`; `valor_final >= valor_inicial` e `valor_final > 0` |
| Meta | `data_fim` precisa ser posterior a `data_inicio` (quando ambas informadas) |
| Meta | Aporte deve ser positivo e não pode ultrapassar o `valor_final` |
| Meta | `porcentagem` tem teto de 100% |

## Códigos de status

| Código | Quando acontece |
|---|---|
| `200` | Leitura, edição, remoção de transação/categoria/meta e aporte em meta |
| `201` | Criação de usuário, transação, categoria ou meta |
| `204` | Remoção de usuário (sem corpo) |
| `400` | Regra de negócio: e-mail ou nome de categoria duplicado, categoria inexistente/de outro dono, categoria com transações, limites inválidos |
| `401` | Sem token, token inválido/expirado, usuário inativo ou credenciais incorretas |
| `403` | Autenticado, mas sem permissão (dado de outro usuário, alterar `ativo` sem ser admin) |
| `404` | Recurso inexistente ou pertencente a outro usuário |
| `422` | Corpo da requisição inválido (validação do Pydantic) |

## Modelo de dados

```
usuarios (1) ──< categorias (1) ──< transacoes
    │                                  ▲
    └──────────────< transacoes ───────┘
    └──────────────< metas
```

| Tabela | Campos |
|---|---|
| `usuarios` | `id`, `nome`, `email` (único), `senha_hash`, `ativo`, `admin` |
| `categorias` | `id`, `nome`, `valor_inicial`, `valor_limite`, `usuario_id` |
| `transacoes` | `id`, `descricao`, `valor`, `tipo`, `data`, `categoria_id` (opcional), `usuario_id` |
| `metas` | `id`, `nome`, `valor_inicial`, `valor_final`, `data_inicio`, `data_fim`, `usuario_id` |

- `categorias` tem `UNIQUE (usuario_id, nome)` — unicidade por dono, não global.
- `usuario_id` é obrigatório nas três tabelas de dados e indexado.
- Ao remover um usuário, suas categorias, transações e metas são removidas em cascata (configurado no ORM).
- `categoria_id` é opcional: uma transação pode existir sem categoria.

## Estrutura do projeto

```
src/
├── main.py                      # App FastAPI, criação das tabelas e registro dos routers
├── financeiro.db                # Banco SQLite (gerado automaticamente, não versionado)
├── dados/
│   ├── config.py                # Settings carregadas do .env (pydantic-settings)
│   ├── database.py              # Engine, Base e SessionLocal
│   ├── dependencies.py          # get_db e verificar_token
│   ├── security.py              # Hash Argon2 e criação de JWT
│   ├── models/                  # Tabelas SQLAlchemy
│   │   ├── usuario.py
│   │   ├── transacao.py         # Transacao + enum TipoTransacao
│   │   ├── categoria.py
│   │   └── meta.py
│   └── schemas/                 # Schemas Pydantic (Create / Update / Response)
│       ├── usuario.py
│       ├── token.py
│       ├── transacao.py
│       ├── categoria.py
│       └── meta.py
└── rotas/
    ├── auth/crud.py             # Login e /me
    ├── usuarios/crud.py
    ├── transacoes/crud.py
    ├── categorias/crud.py       # Inclui os agregados da categoria
    └── metas/crud.py            # Inclui adicionar-valor
```

## Decisões técnicas

**pwdlib/Argon2 em vez de passlib.** A biblioteca `passlib` depende do módulo `crypt` da stdlib, que foi removido no Python 3.13, e não tem manutenção recente. A troca por `pwdlib` manteve o Argon2 (estado da arte para senhas) e eliminou a dependência problemática.

**Validadores de entrada ficam nos schemas `*Create`, não no `*Base`.** Como os `*Response` herdam do `*Base`, um validador colocado lá também roda na hora de serializar a resposta — e isso acontece **depois** do `commit`. O sintoma era uma meta que, ao atingir 100% (`valor_inicial == valor_final`), retornava `500` com o dado já salvo. A regra de entrada pertence à entrada; a resposta apenas reflete o estado.

**`response_model` em todas as rotas.** Sem ele, o FastAPI serializa o objeto do SQLAlchemy inteiro. Foi assim que uma rota chegou a devolver o `senha_hash` do usuário: o schema de resposta é a fronteira que impede campos internos de vazarem.

**Isolamento por `usuario_id` na query, com `404`.** O padrão é filtrar por dono na própria consulta (`WHERE id = ? AND usuario_id = ?`) e responder `404` quando não encontra, em vez de `403`. Assim a API não confirma a existência de registros de outra conta.

**`create_all` em vez de Alembic.** Decisão de escopo: é um projeto pessoal e o banco pode ser recriado a qualquer momento. Em um cenário de produção, a evolução do schema seria feita com migrations versionadas.

**`float` em vez de `Decimal`.** O projeto é de estudo e os valores são valores de controle pessoal, não contabilidade. Em um sistema financeiro real, `Decimal` (ou inteiros em centavos) evitaria erros de arredondamento.

## Qualidade

Verificação de tipos com mypy:

```bash
mypy --ignore-missing-imports --explicit-package-bases src
# Success: no issues found in 29 source files
```

> **Testes automatizados:** ainda não há suíte no repositório. É o próximo item do roadmap abaixo — as rotas foram validadas manualmente com `TestClient` durante o desenvolvimento.

## O que falta

Itens conhecidos, em ordem de prioridade:

**Essencial**

- [ ] Suíte de testes com `pytest` + `TestClient` (autenticação, isolamento entre usuários, regras de limite e meta)
- [ ] Paginação e filtros nas listagens (`tipo`, `data_inicio`/`data_fim`, `categoria_id`, `skip`/`limit`)
- [ ] Relatório mensal de receitas e despesas (o agregado que o domínio pede)

**Qualidade**

- [ ] Migrations com Alembic
- [ ] `criado_em` / `atualizado_em` nas tabelas (auditoria)
- [ ] `model_config = ConfigDict(from_attributes=True)` no lugar do `class Config` (depreciado no Pydantic v2)
- [ ] `selectinload` no cálculo dos agregados de categoria (evitar N+1)
- [ ] Tratamento global de exceções e logging
- [ ] Prefixo de versão `/v1`

**Produção**

- [ ] CI no GitHub Actions rodando mypy e pytest
- [ ] Dockerfile e docker-compose
- [ ] CORS configurado
- [ ] Refresh token e revogação de access token
- [ ] Rate limiting no login
- [ ] Deploy com link público
