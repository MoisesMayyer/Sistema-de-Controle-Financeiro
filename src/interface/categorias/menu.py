from rich.panel import Panel
from rich.console import Console
from rich import box

from interface.categorias.painel import montar_categorias

from financeiro.categorias.crud import (
    nova_categoria, 
    remover_categoria, 
    editar_categoria, 
    obter_todas_categorias
)


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
            nome = console.input("Nome da categoria: ").strip()
            try:
                limite = float(console.input("Limite: "))
                if nova_categoria(nome, limite):
                    console.print("[green]Categoria criada![/green]")
            except ValueError:
                console.print("[red]Limite inválido.[/red]")
            
        elif opcao == 2:
            exibir_lista_simples()
            try:
                id_cat = int(console.input("ID para editar: "))
                nome = console.input("Novo nome: ")
                limite = float(console.input("Novo limite: "))
                if editar_categoria(id_cat, nome, limite):
                    console.print("[green]Alterado com sucesso![/green]")
                else:
                    console.print("[red]ID não encontrado.[/red]")
            except ValueError:
                console.print("[red]Entrada inválida.[/red]")

        elif opcao == 3:
            exibir_lista_simples()
            try:
                id_cat = int(console.input("ID para remover: "))
                if remover_categoria(id_cat):
                    console.print("[green]Removido![/green]")
                else:
                    console.print("[red]ID inexistente ou em uso. Voce nao pode apagar IDs em uso[/red]")
            except ValueError:
                console.print("[red]ID inválido.[/red]")

        elif opcao == 4:
            break
        else:
            console.print("[red]Opção inexistente![/red]")

def exibir_lista_simples():
    categorias = obter_todas_categorias()
    if not categorias:
        console.print("[yellow]Nenhuma categoria disponível.[/yellow]")
        return
    for c in categorias:
        console.print(f"ID: {c['id']} | Nome: {c['nome']}")