from rich.console import Console
from rich.panel import Panel
from rich import box

from financeiro.transaçoes.transacoes import (
    adicionar_transacao,
    editar_transacao,
    remover_transacao
)


console = Console()


def tela_transacoes():

    console.print(
        Panel(
            "[dim][1] Adicionar nova transação   [2] Editar   [3] Excluir   [4] Sair[/dim]\n"
        "[bold yellow]Gerencie seus gastos [/bold yellow]",
        title="Ações", border_style="grey50", box=box.ROUNDED,
        )
    )


    submenu_transacoes()



def submenu_transacoes():

    while True:

        try:
            opcao = int(input("Digite sua opção: "))

        except ValueError:
            print("Opção inválida!")
            continue


        if opcao == 1:
            adicionar_transacao()
            break

        elif opcao == 2:
            editar_transacao()
            break

        elif opcao == 3:
            remover_transacao()
            break

        elif opcao == 4:
            break

        else:
            print("Opção inexistente!")