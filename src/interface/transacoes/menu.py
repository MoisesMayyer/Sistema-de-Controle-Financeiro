from rich.console import Console
from rich.panel import Panel
from rich import box
from rich import print

from financeiro.transacoes.crud import (
    adicionar_transacao,
    editar_transacao,
    remover_transacao,
    buscar_transacao
)

from interface.transacoes.inputs import(
    id_transacao,
    descricao_transacao,
    valor_transacao,
    data_transacao,
    tipo_transacao,
    categoria_transacao
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
            print("[red]Opção inválida![/red]")
            continue

        if opcao == 1:
            descricao = descricao_transacao()
            valor = valor_transacao()
            tipo = tipo_transacao()
            categoria_id = categoria_transacao()
            data = data_transacao()

            sucesso = adicionar_transacao(descricao,valor,tipo,categoria_id,data)

            if sucesso:
                print("[green]Transação adicionada com sucesso![/green]")
                break
            else:
                print("[red]Não foi possível adicionar a transação.[/red]")

        elif opcao == 2:
            transacao_id = id_transacao()

            transacao = buscar_transacao(transacao_id)

            if transacao is None:
                print("[red]ID não encontrado.[/red]")
            else:
                descricao = descricao_transacao()
                valor = valor_transacao()
                tipo = tipo_transacao()
                categoria_id = categoria_transacao()
                data = data_transacao()

                sucesso = editar_transacao(transacao_id, descricao, valor, tipo, categoria_id, data)

                if sucesso:
                    print("[green]Transação editada com sucesso![/green]")
                    break
                else:
                    print("[red]Não foi possível editar a transação.[/red]")

        elif opcao == 3:
            id_remover = id_transacao()

            sucesso = remover_transacao(id_remover)

            if sucesso:
                print("[green]Transação removida com sucesso![/green]")
                break
            else:
                print("[red]ID não encontrado.[/red]")

        elif opcao == 4:
            break

        else:
            print("[red]Opção inexistente![/red]")