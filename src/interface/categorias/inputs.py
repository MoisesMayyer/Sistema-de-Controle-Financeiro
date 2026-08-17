from rich.prompt import Prompt, IntPrompt, FloatPrompt

def id_categoria():
    while True:
        try:
            valor_id = IntPrompt.ask(
                "[cyan]Digite o ID da categoria[/cyan]"
            )

            if valor_id < 0:
                raise ValueError

            return valor_id

        except ValueError:
            print("[red]ID inválido[/red]")


def nome_categoria():
    while True:
        nome = Prompt.ask(
            "[cyan]Digite o nome da categoria[/cyan]"
        ).strip().lower()

        if nome == "":
            print("[red]O nome da categoria não pode ser vazio.[/red]")
            continue

        return nome


def limite_categoria():
    while True:
        try:
            limite = FloatPrompt.ask(
                "[cyan]Digite o limite da categoria[/cyan]"
            )

            if limite < 0:
                raise ValueError

            return limite

        except ValueError:
            print("[red]O limite da categoria não pode ser negativo.[/red]")