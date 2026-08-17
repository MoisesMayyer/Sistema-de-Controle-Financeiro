from rich.panel import Panel
from rich.console import Console
from rich import box
from rich.table import Table

from interface.categorias.painel import montar_categorias

from financeiro.categorias.crud import (
    nova_categoria,
    remover_categoria,
    editar_categoria,
    obter_todas_categorias, buscar_categoria
)

from interface.categorias.inputs import limite_categoria, nome_categoria, id_categoria

console = Console()


def tela_categorias():
    console.print(montar_categorias())
    console.print()
    console.print(Panel(
        "[dim][1] Nova categoria   [2] Editar limite   [3] Remover categoria   [4] Sair[/dim]\n"
        "[bold yellow]gerencie suas categorias[/bold yellow]",
        title="Ações", border_style="grey50", box=box.ROUNDED,
    ))
    submenu_categorias()


def submenu_categorias():
    while True:
        try:

            opcao = int(console.input("[bold]Digite sua opção: [/bold]"))

        except ValueError:

            console.print("[red]Opção inválida![/red]")

            continue

        if opcao == 1:

            while True:

                nome = nome_categoria()
                limite = limite_categoria()

                if nova_categoria(nome, limite):
                    console.print("[green]Categoria criada![/green]")
                    break
                else:
                    console.print("[red]Erro ao criar categoria![/red]")


        elif opcao == 2:

            exibir_lista_simples()

            id_cat = id_categoria()
            categoria = buscar_categoria(id_cat)

            if categoria:
                nome = nome_categoria()
                limite = limite_categoria()

                if editar_categoria(id_cat, nome, limite):
                    console.print("[green]Alterado com sucesso![/green]")

                else:
                    console.print("[red]Não foi possível editar.[/red]")

            else:
                console.print("[red]ID não encontrado.[/red]")


        elif opcao == 3:

            exibir_lista_simples()

            id_cat = id_categoria()
            categoria = buscar_categoria(id_cat)

            if categoria:

                if remover_categoria(id_cat):
                    console.print("[green]Removido![/green]")

                else:
                    console.print(
                        "[red]ID inexistente ou em uso. "
                        "Você não pode apagar IDs em uso.[/red]"
                    )

            else:

                console.print("[red]ID não encontrado.[/red]")

        elif opcao == 4:
            break

        else:
            console.print("[red]Opção inexistente![/red]")



def exibir_lista_simples():

    categorias = obter_todas_categorias()

    if not categorias:
        console.print("[yellow]Nenhuma categoria disponível.[/yellow]")
        return

    tabela = Table(
        title="Categorias",
        show_header=True,
        header_style="bold cyan"
    )

    tabela.add_column("ID", justify="center")
    tabela.add_column("Nome")
    tabela.add_column("Limite", justify="right")

    for categoria in categorias:
        tabela.add_row(
            str(categoria["id"]),
            categoria["nome"],
            f"R$ {categoria['limite']:.2f}"
        )

    console.print(tabela)