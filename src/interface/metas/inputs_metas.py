from rich import print


def input_id() -> int:

    while True:
        try:
            valor_id = int(input("Digite o ID da meta: "))

            if valor_id < 0:
                raise ValueError

            return valor_id

        except ValueError:
            print("[red]ID inválido[/red]")


def input_nome() -> str:

    while True:
        try:
            nome = input("Digite o nome da meta: ").strip()

            if nome == "":
                raise ValueError

            return nome

        except ValueError:
            print("[red]Nome inválido[/red]")


def input_valor(mensagem: str) -> float:

    while True:
        try:
            valor = float(input(mensagem))

            if valor <= 0:
                raise ValueError

            return valor

        except ValueError:
            print("[red]Valor inválido[/red]")