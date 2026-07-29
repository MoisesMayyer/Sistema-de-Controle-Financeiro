from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich import box
from datetime import datetime


def montar_cabecalho() -> Panel:

    titulo = Text(
        "💰 CONTROLE DE GASTOS",
        style="bold white on dark_green",
        justify="center"
    )

    subtitulo = Text(
        f"Bem-vindo(a), Usuário • {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        style="dim",
        justify="center"
    )

    conteudo = Text.assemble(
        titulo,
        "\n",
        subtitulo
    )

    return Panel(
        Align.center(conteudo),
        box=box.DOUBLE
    )


def montar_menu_lateral(opcao_ativa, menu_opcoes):

    texto = Text()

    for chave, nome in menu_opcoes:

        if chave == opcao_ativa:
            texto.append(
                f" ➤ [{chave}] {nome}\n",
                style="bold black on green"
            )

        else:
            texto.append(
                f"   [{chave}] {nome}\n",
                style="white"
            )

    return Panel(
        texto,
        title="MENU",
        border_style="green"
    )


def montar_rodape(mensagem=""):

    texto = Text(
        mensagem or "Digite uma opção",
        justify="center"
    )

    return Panel(
        texto,
        box=box.MINIMAL
    )