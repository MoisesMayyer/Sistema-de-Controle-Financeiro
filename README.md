
# Sistema de Controle Financeiro

Aplicação de terminal em Python para controle pessoal de despesas, receitas, categorias e metas. A interface foi construída com a biblioteca Rich para proporcionar telas e painéis amigáveis no terminal. O armazenamento atual é feito usando arquivos JSON na pasta `src/dados`.

Visão rápida:

- Projeto modular: separação entre camada de dados (`dados`), regras de negócio (`financeiro`) e interface (`interface`).
- Interface interativa no terminal (menus, formulários e painéis) construída com `rich`.
- Operações suportadas: adicionar/editar/remover transações, gerenciar categorias, gerenciar metas e visualizar um dashboard com resumo e últimas transações.

## Estrutura principal do projeto

- `src/` - código fonte do pacote
  - `__main__.py` - ponto de entrada (executar com `python -m src`)
  - `dados/` - armazenamento JSON e helpers (`gastos.json`, `categorias.json`)
  - `financeiro/` - regras de negócio:
	- `transacoes/` (CRUD e cálculos de totais/saldo)
	- `categorias/` (CRUD de categorias)
	- `metas/` (CRUD e atualização de progresso das metas)
  - `interface/` - telas, inputs e painéis construídos com `rich`
  - `utils/` - utilitários (ex.: criação de IDs)

## Funcionalidades implementadas

- Adicionar, editar e remover transações (despesa/receita) com data e categoria opcional
- Listar últimas transações em tabela com formatação de cores
- Calcular totais de receitas, despesas e saldo atual
- Gerenciar categorias (criar, editar limite, remover — com proteção contra remoção de categorias em uso)
- Gerenciar metas (criar meta, editar, adicionar valor e exibir progresso com barra)
- Persistência simples usando JSON (carregar/salvar)
- Interface de terminal baseada em menus com validação robusta de entradas

## Requisitos

- Python 3.10+ (código usa typing e recursos modernos)
- Dependências declaradas em `pyproject.toml`:
  - `rich`

Instalação (modo desenvolvimento):

```bash
python -m pip install -e .
```

Ou apenas instalar a dependência para executar sem instalar o pacote:

```bash
python -m pip install rich
```

## Como executar

Para iniciar a aplicação em modo terminal (ponto de entrada já implementado):

```bash
python -m src
```

Observação: os arquivos de dados ficam em `src/dados/`. Se os arquivos JSON (por exemplo `metas.json`) não existirem, o sistema os trata como listas vazias e cria/usa quando necessário.

## Testes

O projeto possui testes unitários com `pytest` (pasta `tests/`). Para executá-los:

```bash
python -m pip install pytest
pytest
```

Nota: há testes em andamento (por exemplo `tests/test_financeiro/test_transacoes.py` está vazio atualmente). Uma tarefa próxima é finalizar a cobertura dos testes e ajustar fixtures conforme necessário.

## Comandos úteis de desenvolvimento

- Executar apenas um teste específico:

```bash
pytest tests/test_financeiro/test_calculos.py -q
```

- Rodar o package diretamente (útil em desenvolvimento):

```bash
python -m src
```

## Observações sobre o código

- O projeto trata arquivos JSON de forma defensiva: se um arquivo não existir ou estiver corrompido, a função `carregar_json` retorna uma lista vazia.
- O gerador de IDs (`utils/id.py`) cria IDs incrementais a partir do maior ID presente na lista.
- A camada `financeiro` contém a lógica (CRUD e cálculos) e a `interface` se responsabiliza apenas pela interação com o usuário.

## Próximas atualizações

As próximas tasks planejadas (priorizadas):

1. Finalizar e complementar os testes com `pytest` (cobertura para CRUD de transações, categorias e metas).
2. Implementar uma API REST com FastAPI para expor as operações (CRUD/relatórios) — permitindo uso futuro por frontend e integração com clientes HTTP.
3. Desenvolver um frontend (web ou desktop) que consuma a API (ou a camada local) para uma experiência gráfica.

Para preparar o repositório para essas etapas, já foi feita a organização modular para isolar regras de negócio (facilitando a extração para uma API) e já existem testes iniciais para as funções de cálculo.

## Contribuição

Contribuições são bem-vindas. Recomendações:

- Abra issues para discutir features/bugs.
- Crie branches com nomes descritivos (`feature/tests-transacoes`, `feature/fastapi-api`).
- Adicione testes para qualquer nova funcionalidade.

## Licença

Escolha uma licença apropriada (por exemplo MIT) e adicione um arquivo `LICENSE` se desejar abrir o projeto publicamente.
