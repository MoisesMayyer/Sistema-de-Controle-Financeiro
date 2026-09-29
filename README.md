# Sistema de Controle Financeiro

> ⚠️ **Projeto pausado** — Estou aprendendo FastAPI e vou retomar este projeto quando souber criar boas APIs.

---

Aplicação de terminal em Python para controle pessoal de despesas, receitas, categorias e metas. Interface construída com Rich para telas amigáveis no terminal. Armazenamento via JSON em `src/dados`.

## Estrutura principal

```
src/
├── __main__.py          # Ponto de entrada (python -m src)
├── dados/               # JSON storage (gastos.json, categorias.json, metas.json)
├── financeiro/          # Regras de negócio
│   ├── transacoes/      # CRUD + cálculos
│   ├── categorias/      # CRUD categorias
│   └── metas/           # CRUD + progresso
├── interface/           # Telas e painéis com Rich
└── utils/               # Utilitários (IDs, etc.)
```

## Funcionalidades

- CRUD de transações (despesa/receita) com data e categoria
- Listagem colorida de últimas transações
- Totais de receitas, despesas e saldo
- CRUD de categorias (com proteção contra remoção de categorias em uso)
- CRUD de metas com barras de progresso
- Persistência JSON defensiva
- Interface de terminal baseada em menus

## Como executar

```bash
python -m pip install rich
python -m src
```

## Próximos passos (quando retomar)

1. Finalizar testes com pytest
2. Implementar API REST com FastAPI
3. Desenvolver frontend consumindo a API

---

*Projeto deixado de lado temporariamente para focar no aprendizado de FastAPI. Volto quando dominar criação de APIs bem estruturadas.*