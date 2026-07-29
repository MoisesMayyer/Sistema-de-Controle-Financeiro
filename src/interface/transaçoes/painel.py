from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich import box
from dados.dados import carregar_json, CAMINHO_TRANSACOES
from financeiro.transaçoes.calculos import obter_resumo
from rich.console import Console
from financeiro.transaçoes.crud import buscar_nome_categoria

console = Console()


def montar_cards_resumo() -> Table:
    tabela = Table.grid(expand=True)
    tabela.add_column(ratio=1)
    tabela.add_column(ratio=1)
    tabela.add_column(ratio=1)

    resumo = obter_resumo()

    card_saldo = Panel(
        Align.center(Text(f"R$ {resumo['saldo']:.2f}", style="bold green")),
        title="💼 Saldo Atual", border_style="green", box=box.ROUNDED,
    )
    card_receitas = Panel(
        Align.center(Text(f"R$ {resumo['receitas']:.2f}", style="bold cyan")),
        title="⬆️  Receitas", border_style="cyan", box=box.ROUNDED,
    )
    card_despesas = Panel(
        Align.center(Text(f"R$ {resumo['despesas']:.2f}", style="bold red")),
        title="⬇️  Despesas", border_style="red", box=box.ROUNDED,
    )
    tabela.add_row(card_saldo, card_receitas, card_despesas)
    return tabela


def montar_tabela_transacoes() -> Panel:
    tabela = Table(box=box.SIMPLE_HEAVY, expand=True, show_lines=False)

    tabela.add_column("ID", justify="center")
    tabela.add_column("Data", style="dim", width=10)
    tabela.add_column("Descrição", style="white")
    tabela.add_column("Categoria", style="magenta")
    tabela.add_column("Tipo", justify="center")
    tabela.add_column("Valor", justify="right")

    transacoes = carregar_json(CAMINHO_TRANSACOES)

    for t in transacoes:
        cor_valor = "green" if t["tipo"] == "receita" else "red"
        sinal = "+" if t["tipo"] == "receita" else "-"

        tabela.add_row(str(t["id"]),
            t["data"],
            t["descricao"],
            buscar_nome_categoria(t["categoria_id"]),
            f"[{cor_valor}]{t['tipo']}[/]",
            f"[{cor_valor}]{sinal} R$ {t['valor']:.2f}[/]",
        )

    return Panel(
        tabela,
        title="🧾 Últimas Transações",
        border_style="blue",
        box=box.ROUNDED
    )


def tela_dashboard():
    console.print(montar_cards_resumo())
    console.print()
    console.print()
    console.print(montar_tabela_transacoes())