from rich.console import Console
from rich.prompt import Prompt
from rich.text import Text
from rich.panel import Panel
from rich.align import Align
from rich import box
from interface.componentes_menu import (
    montar_cabecalho,
    montar_menu_lateral,
)

from interface.dashboard_menu import tela_dashboard
from interface.interface_transacoes import tela_transacoes
from interface.interface_categorias import tela_categorias
from interface.interfaces_meta import tela_metas

console = Console()


menu_opcoes = [
    ("1", "📊 Dashboard"),
    ("2", "💸 Transações"),
    ("3", "📈 Categorias"),
    ("4", "🎯 Metas"),
    ("0", "🚪 Sair"),
]


TELAS = {
    "1": tela_dashboard,
    "2": tela_transacoes,
    "3": tela_categorias,
    "4": tela_metas
}


def iniciar_menu():

    opcao_ativa = "1"

    while True:

        console.clear()

        console.print(
            montar_cabecalho()
        )

        console.print(
            montar_menu_lateral(
                opcao_ativa,
                menu_opcoes
            )
        )

        console.print()

        tela = TELAS.get(opcao_ativa)

        if tela:
            tela()


        escolha = Prompt.ask(
            "[bold cyan]Escolha uma opção[/bold cyan]",
            choices=[c for c, _ in menu_opcoes],
            show_choices=True,
        )


        if escolha == "0":
            console.print(Panel(
                Align.center(Text("Até logo! 👋", style="bold green")),
                box=box.DOUBLE, border_style="green",
            ))
            break


        opcao_ativa = escolha