from rich import print
from rich.prompt import Prompt, FloatPrompt, IntPrompt
from datetime import datetime


def id_transacao() -> int:

    while True:
        try:
            valor_id = IntPrompt.ask("[cyan]Digite o ID que deseja alterar[/cyan]")

            if valor_id < 0:
                raise ValueError

            return valor_id

        except ValueError:
            print("[red]ID inválido[/red]")


def descricao_trancsacao() -> str:
    while True:
        try:
            descricao = Prompt.ask(
                "[cyan]Digite a descrição da transação[/cyan]"
            ).strip().lower()

            if descricao == "":
                raise ValueError(
                    "[red]A descrição não pode estar vazia![/red]"
                )

            if descricao.isdigit():
                raise ValueError(
                    "[red]A descrição não pode conter apenas números.[/red]"
                )

            return descricao

        except ValueError as erro:
            print(erro)


def valor_transacao() -> float:
    while True:
        try:
            valor = FloatPrompt.ask(
                "[cyan]Digite o valor da transação[/cyan]"
            )

            if valor <= 0:
                raise ValueError(
                    "[red]O valor deve ser maior que zero![/red]"
                )

            return valor

        except ValueError as erro:
            print(erro)


def tipo_transacao():
    while True:
        try:
            print("\n[bold cyan]━━━ Tipo da Transação ━━━[/bold cyan]")
            print("[green]1[/green] → Despesa")
            print("[blue]2[/blue] → Receita")

            tipo = Prompt.ask(
                "[cyan]Escolha uma opção[/cyan]"
            )

            if tipo == "1":
                tipo = "despesa"
            elif tipo == "2":
                tipo = "receita"
            else:
                raise ValueError(
                    "[red]Escolha 1 para despesa ou 2 para receita.[/red]"
                )

            return tipo

        except ValueError as erro:
            print(erro)


def categoria_tranascao():
    pass


def data_transacao():
    while True:
        data = input("Digite a data da transação (DD/MM/AAAA): ")

        try:
            data_validada = datetime.strptime(data, "%d/%m/%Y")
            return data_validada.strftime("%d/%m/%Y")

        except ValueError:
            print("Data inválida. Digite no formato DD/MM/AAAA.")
