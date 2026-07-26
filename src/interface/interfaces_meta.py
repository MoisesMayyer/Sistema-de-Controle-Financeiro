from rich.console import Console, Group
from rich.table import Table
from rich.panel import Panel
from rich.progress_bar import ProgressBar
from rich.align import Align
from rich.text import Text
from rich.prompt import Prompt
from rich import box

from financeiro.metas import (
    adicionar_meta,
    editar_meta,
    remover_meta,
)


console = Console()


metas_opcoes = [
    ("1", "➕ Adicionar Meta"),
    ("2", "✏️  Editar Meta"),
    ("3", "🗑️  Remover Meta"),
    ("0", "↩️  Voltar"),
]


def mostrar_cabecalho_metas() -> None:

    titulo = Text(
        "🎯  CONTROLE FINANCEIRO",
        style="bold white",
        justify="center",
    )
    subtitulo = Text(
        "Metas Financeiras",
        style="cyan",
        justify="center",
    )

    conteudo = Group(titulo, subtitulo)

    console.print(
        Panel(
            conteudo,
            box=box.DOUBLE,
            border_style="cyan",
            padding=(1, 2),
        )
    )


def mostrar_menu_metas(opcao_ativa: str) -> str:

    texto = Text()

    for codigo, rotulo in metas_opcoes:
        if codigo == opcao_ativa:
            texto.append(
                f" ➤ [{codigo}] {rotulo}\n",
                style="bold black on green",
            )
        else:
            texto.append(
                f"   [{codigo}] {rotulo}\n",
                style="white",
            )

    console.print(
        Panel(
            texto,
            title="MENU",
            border_style="green",
        )
    )

    return Prompt.ask(
        "[bold cyan]Escolha uma opção[/bold cyan]",
        choices=[codigo for codigo, _ in metas_opcoes],
        show_choices=True,
    )


def painel_meta(
    *,
    id_meta: int,
    nome: str,
    porcentagem: int,
) -> Panel:

    concluida = porcentagem >= 100
    cor_destaque = "bold green" if concluida else "bold cyan"
    cor_barra = "green" if concluida else "cyan"
    icone = "✅" if concluida else "🎯"

    cabecalho = Table.grid(expand=True)
    cabecalho.add_column(justify="left", ratio=1)
    cabecalho.add_column(justify="right")
    cabecalho.add_row(
        Text(f"#{id_meta}", style="dim white") + Text(f"  {nome}", style="bold white"),
        Text(f"{porcentagem}%", style=cor_destaque),
    )

    barra = ProgressBar(
        total=100,
        completed=porcentagem,
        complete_style=cor_barra,
        finished_style="green",
    )

    conteudo = Table.grid(expand=True)
    conteudo.add_row(cabecalho)
    conteudo.add_row(barra)

    return Panel(
        conteudo,
        title=icone,
        title_align="left",
        border_style=cor_barra,
        box=box.ROUNDED,
        padding=(1, 1),
    )


def _organizar_em_pares(paineis: list[Panel]) -> Table:

    grid = Table.grid(expand=True, padding=(0, 1, 1, 0))
    grid.add_column(ratio=1)
    grid.add_column(ratio=1)

    for indice in range(0, len(paineis), 2):
        par = paineis[indice:indice + 2]

        if len(par) == 2:
            grid.add_row(par[0], par[1])
        else:
            grid.add_row(par[0], "")

    return grid


def mostrar_metas(metas: list[dict]) -> None:

    console.print()

    if not metas:
        console.print(
            Panel(
                Align.center("[yellow]Nenhuma meta cadastrada.[/yellow]"),
                border_style="yellow",
                box=box.ROUNDED,
                padding=(1, 2),
            )
        )
        console.print()
        return

    paineis = [
        painel_meta(
            id_meta=meta["id"],
            nome=meta["nome"],
            porcentagem=meta["porcentagem"],
        )
        for meta in metas
    ]

    console.print(_organizar_em_pares(paineis))
    console.print()


def _pausar() -> None:

    console.print()
    Prompt.ask(
        "[dim]Pressione Enter para continuar[/dim]",
        default="",
        show_default=False,
    )


def tela_metas() -> None:
    metas = [
        {
            "id": 1,
            "nome": "Notebook Novo",
            "porcentagem": 100,
        },
        {
            "id": 2,
            "nome": "Reserva de Emergência",
            "porcentagem": 40,
        },
    ]

    opcao_ativa = "1"

    while True:

        console.clear()

        mostrar_metas(metas)

        escolha = mostrar_menu_metas(opcao_ativa)

        opcao_ativa = escolha

        if escolha == "1":
            adicionar_meta()
            _pausar()

        elif escolha == "2":
            editar_meta()
            _pausar()

        elif escolha == "3":
            remover_meta()
            _pausar()

        elif escolha == "0":

            console.print()
            console.print(
                Panel(
                    Align.center(
                        Text(
                            "Retornando ao menu principal...",
                            style="bold green",
                        )
                    ),
                    box=box.DOUBLE,
                    border_style="green",
                    padding=(1, 2),
                )
            )

            break