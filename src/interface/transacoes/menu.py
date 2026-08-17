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
from interface.transacoes.inputs import id_transacao,descricao_trancsacao, valor_transacao, data_transacao, tipo_transacao

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
            print(f"[red]Opção inválida![/red]")
            continue

        if opcao == 1:

            descricao = descricao_trancsacao()
            valor = valor_transacao()
            tipo = tipo_transacao()
            data = data_transacao()

            adicionar_transacao(descricao, valor, tipo, data)

        elif opcao == 2:
            transacao_id = id_transacao()

            transacao = buscar_transacao(transacao_id)

            if transacao is None:
                print("ID não encontrado.")
            else:
                descricao = descricao_trancsacao()
                valor = valor_transacao()
                tipo = tipo_transacao()
                data = data_transacao()

                sucesso = editar_transacao(transacao_id, descricao, valor, tipo, data)

                if sucesso:
                    print("Transação editada com sucesso!")

        elif opcao == 3:
            id_remover = id_transacao()

            sucesso = remover_transacao(id_remover)

            if sucesso:
                print("Transação removida com sucesso!")
            else:
                print("ID não encontrado.")

        elif opcao == 4:
            break

        else:
            print("Opção inexistente!")