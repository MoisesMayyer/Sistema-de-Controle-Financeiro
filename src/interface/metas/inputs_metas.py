from rich import print

def input_metas(precisa_id: bool):

    while True:
        try:
            nome_metas = input("Digite o nome de meta: ").strip()

            if nome_metas == "":
                print("[red]digite um nome valido[/red]")
                raise ValueError

            valor_metas = int(input("digite o valor da meta: "))

            if valor_metas < 0:
                print(f"[red]digite um valor valido[/red]")
                raise ValueError

            if precisa_id:
                while True:
                    try:
                        valor_id = int(input("digite o id da meta: "))

                        if valor_id < 0:
                            raise ValueError

                        return nome_metas, valor_metas, valor_id

                    except ValueError:
                        print("[red]digite um ID valido[/red]")

            return nome_metas, valor_metas, None

        except ValueError:
            print(f"[red]Tente novamente[/red]")