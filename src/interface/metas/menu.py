from rich.console import Console, Group
from rich.table import Table
from rich.panel import Panel
from rich.progress_bar import ProgressBar
from rich.align import Align
from rich.text import Text
from rich.prompt import Prompt
from rich import box

from dados.dados import (
    carregar_json,
    CAMINHO_METAS,
    )

from financeiro.metas.crud import (
    adicionar_meta,
    editar_meta,
    remover_meta,
    calcular_porcentagem_meta, adicionar_valor_meta
)


console = Console()

metas_opcoes = [
    ("1", "➕ Adicionar Meta"),
    ("2", "➕ Adicionar valor"),
    ("3", "✏️  Editar Meta"),
    ("4", "🗑️  Remover Meta"),
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


def mostrar_menu_metas() -> str:

    texto = Text()

    for codigo, rotulo in metas_opcoes:
        texto.append(f"   [{codigo}] {rotulo}\n", style="white")

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
    porcentagem: float,
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
        Text(f"{porcentagem:.0f}%", style=cor_destaque),
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
            porcentagem=calcular_porcentagem_meta(
                meta["valor_atual"],
                meta["valor_meta"]
            )
        )
        for meta in metas
    ]

    console.print(_organizar_em_pares(paineis))
    console.print()


def tela_metas() -> None:

    while True:
        console.clear()
        mostrar_cabecalho_metas()

        metas = carregar_json(CAMINHO_METAS)
        mostrar_metas(metas)

        escolha = mostrar_menu_metas()

        console.clear()
        mostrar_cabecalho_metas()

        if escolha == "1":
            adicionar_meta()

        elif escolha == "2":
            adicionar_valor_meta()

        elif escolha == "3":
            editar_meta()

        elif escolha == "4":
            remover_meta()

        elif escolha == "0":
            console.print()
            console.print(
                Panel(
                    Align.center(
                        Text("Retornando ao menu principal...", style="bold green")
                    ),
                    box=box.DOUBLE,
                    border_style="green",
                    padding=(1, 2),
                )
            )
            break

        if escolha != "0":
            Prompt.ask("\n[dim]Pressione Enter para continuar[/dim]", default="")