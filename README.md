# Controle Financeiro API

> 📚 **Projeto de estudo** — Meu primeiro projeto de programação, refatorado para **FastAPI**.

Este projeto nasceu quando comecei a aprender programação (versão original em Python com JSON/terminal). Agora foi completamente reescrito para aprender **FastAPI**, **SQLAlchemy** e **Pydantic**.

API REST para controle pessoal de finanças construída com **FastAPI**, **SQLAlchemy** e **SQLite**.

## Tecnologias

- **FastAPI** - Framework web moderno e rápido
- **SQLAlchemy 2.0** - ORM com tipagem estática
- **Pydantic v2** - Validação e serialização de dados
- **SQLite** - Banco de dados leve (arquivo único)
- **Uvicorn** - Servidor ASGI

## Estrutura do Projeto

```
src/
├── main.py                    # App FastAPI + criação de tabelas
├── dados/                     # Camada de dados
│   ├── __init__.py
│   ├── database.py           # Engine, Base, SessionLocal
│   ├── dependencies.py       # Dependency get_db()
│   ├── models/               # Models SQLAlchemy (tabelas)
│   │   ├── __init__.py
│   │   ├── transacao.py      # Transacao + TipoTransacao (enum)
│   │   ├── categoria.py      # Categoria
│   │   └── meta.py           # Meta
│   └── schemas/              # Schemas Pydantic (validação)
│       ├── __init__.py
│       ├── transacao.py      # Create/Update/Response
│       ├── categoria.py      # Create/Update/Response
│       └── meta.py           # Create/Update/Response
└── rotas/                    # Endpoints da API
    ├── __init__.py
    ├── transacoes/
    │   ├── __init__.py
    │   └── crud.py           # CRUD completo
    ├── categorias/
    │   ├── __init__.py
    │   └── crud.py           # CRUD completo
    └── metas/
        ├── __init__.py
        └── crud.py           # CRUD + adicionar_valor
```

## Endpoints

### Transações (`/transacoes`)
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/` | Lista todas |
| GET | `/{id}` | Busca por ID |
| POST | `/` | Cria nova |
| PUT | `/{id}` | Atualiza |
| DELETE | `/{id}` | Remove |

### Categorias (`/categorias`)
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/` | Lista todas |
| GET | `/{id}` | Busca por ID |
| POST | `/` | Cria nova |
| PUT | `/{id}` | Atualiza |
| DELETE | `/{id}` | Remove (bloqueia se tiver transações) |

### Metas (`/metas`)
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/` | Lista todas (com % progresso) |
| GET | `/{id}` | Busca por ID |
| POST | `/` | Cria nova |
| PUT | `/{id}` | Atualiza |
| DELETE | `/{id}` | Remove |
| POST | `/{id}/adicionar-valor` | Adiciona valor à meta |

## Validações

- **Transação**: valor > 0, tipo = `receita` ou `despesa`, data obrigatória
- **Categoria**: nome único, limite > valor_inicial
- **Meta**: valor_final > valor_inicial, data_fim > data_inicio
- **Integridade**: não remove categoria com transações associadas

## Como Executar

```bash
# Instalar dependências
pip install fastapi uvicorn sqlalchemy pydantic

# Rodar servidor
cd src
python -m uvicorn main:app --reload

# Acessar documentação
# http://localhost:8000/docs  (Swagger UI)
# http://localhost:8000/redoc  (ReDoc)
```

## Banco de Dados

O arquivo `financeiro.db` é criado automaticamente na pasta `src/` na primeira execução.

Tabelas:
- `transacoes` - id, descricao, valor, tipo, data, categoria_id (FK)
- `categorias` - id, nome, valor_inicial, valor_limite
- `metas` - id, nome, valor_inicial, valor_final, data_inicio, data_fim

## Qualidade de Código

```bash
# Verificação de tipos (mypy)
python -m mypy --ignore-missing-imports --explicit-package-bases src
# Success: no issues found in 20 source files
```