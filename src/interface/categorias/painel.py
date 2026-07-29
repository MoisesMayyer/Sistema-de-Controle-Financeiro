from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn
from rich import box
from rich.console import Console

from dados.dados import carregar_json, CAMINHO_CATEGORIAS
from financeiro.transacoes.calculos import calcular_gasto_categoria

console = Console()



def montar_categorias() -> Panel:

    categorias = carregar_json(CAMINHO_CATEGORIAS)

    progress = Progress(
        TextColumn("[bold]ID: {task.fields[id]}"),
        TextColumn("[bold]{task.fields[nome]:<14}"),
        BarColumn(bar_width=30),
        TextColumn("R$ {task.fields[gasto]:.2f} / R$ {task.fields[limite]:.2f}"),
        expand=True,
    )

    if categorias:
        for c in categorias:
            gasto = calcular_gasto_categoria(c["id"])
            progress.add_task(
                "",
                total=c["limite"],
                completed=gasto,
                id=c["id"],
                nome=c["nome"],
                gasto=gasto,
                limite=c["limite"]
            )

        return Panel(progress, title="🗂️  Gastos por Categoria", border_style="yellow", box=box.ROUNDED)

    else:
        return Panel(
            "Nenhuma categoria cadastrada.",
            title="🗂️ Gastos por Categoria",
            border_style="yellow",
            box=box.ROUNDED,
        )


