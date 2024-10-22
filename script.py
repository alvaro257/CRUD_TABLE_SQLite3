from flet import *
import flet as ft
import sqlite3

def main(page: Page):
    
    page.title = "CRUD TABLE"
    page.window.width = 780
    page.window.height = 520
    page.window.always_on_top = True
    
    # Funcoes

    # Funcao que cria o BD se o mesmo ainda não existir
    def criar_bd():
        try:
            # Criando a conexao com o banco de dados SQLite3 (e o BD em si, caso nao exista)
            conexao = sqlite3.connect("basededadoscrud.db")
            
            # Criando cursor para executar comandos SQL
            cursor = conexao.cursor()
            
            # Criando a tabela caso ainda nao exista
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tabeladeprodutos (
                    id INTEGER PRIMARY KEY,
                    produto TEXT NOT NULL,
                    estoque INTEGER NOT NULL,
                    preco REAL NOT NULL
                );
            ''')
            
            # Confirmando a operacao
            conexao.commit()
            
        # Aviso de erro
        except sqlite3.Error as err:
            page.snack_bar = ft.SnackBar(
                content= ft.Text(f"Erro ao criar banco de dados: {err}", color= colors.WHITE),
                duration= ft.Duration(seconds=2),
                bgcolor= ft.colors.RED
            )
            page.snack_bar.open = True
        # Fecha a conexao
        finally:
            conexao.close()
    
    # Funcao para adicionar produtos a tabela
    def create(e):
        # Funcao que troca "," por "." no campo do preco para evitar erros com numeros float
        def replace(e):
            preco.value = preco.value.replace(",",".")
            page.update()
        
        # Funcao que salva os dados na tabela somente depois de acionar o botao "Salvar"
        def salvar(e):
            try:
                conexao = sqlite3.connect("basededadoscrud.db")
                cursor = conexao.cursor()
                
                # Adiciona o produto na tabela
                cursor.execute("INSERT INTO tabeladeprodutos (produto, estoque, preco) VALUES (?,?,?);",(produto.value, estoque.value, preco.value))
                conexao.commit()
                
                # Atualiza a tabela na tela
                atualizar_page(1)
                
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("Produto cadastrado com sucesso!", color=ft.colors.WHITE),
                    bgcolor=ft.colors.GREEN,
                    duration=ft.Duration(seconds=2)
                )
                page.snack_bar.open = True
            except sqlite3.Error as err:
                page.snack_bar = ft.SnackBar(
                    content= ft.Text(f"Erro ao adicionar produto: {err}", color= colors.WHITE),
                    duration= ft.Duration(seconds=2),
                    bgcolor= ft.colors.RED
                )
                page.snack_bar.open= True
            except ValueError:
                page.snack_bar = ft.SnackBar(
                    content= ft.Text("Erro ao cadastrar produto, verifique se as informações estão preenchidas corretamente!", color= colors.WHITE),
                    duration= ft.Duration(seconds=2),
                    bgcolor= ft.colors.RED
                )
                page.snack_bar.open= True
            finally:
                conexao.close()
                setattr(tela, "open", False)
                page.update()
        
        # Campos de entrada
        produto = ft.TextField(label="Nome do produto", autofocus=True)
        estoque = ft.TextField(label="Estoque")
        preco = ft.TextField(label="Preço", on_change=replace)
        
        # Tela de dialogo para adiconar os dados do produto novo
        tela = ft.AlertDialog(
            title = ft.Text("Cadastrar novo produto"),
            content= ft.Column([
                ft.Text("Preencha as informações do novo produto:"),
                produto,
                estoque,
                preco
            ]),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e:[setattr(tela, "open", False), page.update()]),
                ft.TextButton("Salvar", on_click= salvar)
            ],
            open=True
        )
        page.overlay.append(tela)
        page.update()
          
    # Funcao para excluir produtos da tabela
    def delete(e):
        # Funcao que exclui o produto da tabela somente depois de acionar o botao "Excluir" e "Confirmar"
        def excluir(e):
            try:
                conexao = sqlite3.connect("basededadoscrud.db")
                
                # Executa o comando de excluir
                cursor = conexao.cursor()
                cursor.execute("DELETE FROM tabeladeprodutos WHERE id = ?;", (id.value,))
                
                # Verifica se houve de fato alteracao na tabela (se alguma linha foi excluida)
                if cursor.rowcount == 0:
                    # Aviso de erro caso o ID nao exista ou nao haja alteracao em alguma linha
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text("Erro ao apagar produto, verifique se o ID está correto!", color=ft.colors.WHITE),
                        bgcolor=ft.colors.RED,
                        duration=ft.Duration(seconds=2)
                    )
                    page.snack_bar.open = True
                # Se houve alteracao confirma a exclusao
                else:
                    conexao.commit()
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text("Produto excluido com sucesso!", color=ft.colors.WHITE),
                        bgcolor=ft.colors.GREEN,
                        duration=ft.Duration(seconds=2)
                    )
                page.snack_bar.open = True
                atualizar_page(1)   
            except sqlite3.Error as err:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Erro ao excluir produto: {err}", color=ft.colors.WHITE),
                    bgcolor=ft.colors.RED,
                    duration=ft.Duration(seconds=2)
                )
                page.snack_bar.open = True
            except ValueError:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("Erro ao apagar produto, verifique se o ID está correto!", color=ft.colors.WHITE),
                    bgcolor=ft.colors.RED,
                    duration=ft.Duration(seconds=2)
                )
                page.snack_bar.open = True
            finally:
                conexao.close()
                setattr(confirmacao, "open", False)
                page.update()
        
        # Campo de entrada para o ID
        id = TextField(label="ID:", autofocus=True)
        
        # Tela de dialogo para excluir produtos
        tela = ft.AlertDialog(
            title= ft.Text("Excluir produto"),
            content= ft.Column([
                ft.Text("Insira o ID do produto que deseja apagar:"),
                id
            ]),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e:[setattr(tela, "open", False), page.update()]),
                ft.TextButton("Excluir", on_click= lambda e: [setattr(tela, "open", False), setattr(confirmacao, "open", True), page.update()])
            ],
            open=True
        )
        page.overlay.append(tela)
        
        # Tela de dialogo para confirmar exclusao
        confirmacao = ft.AlertDialog(
                title= ft.Text("Tem certeza que deseja excluir esse produto?"),
                content= ft.Text("Essa ação resultará na exclusão definitiva do produto!"),
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda e:[setattr(confirmacao, "open", False), page.update()]),
                    ft.TextButton("Sim", on_click=excluir)
                ],
                open=False
            )
        page.overlay.append(confirmacao)
        page.update()

        
    # Funcao para atualizar produtos da tabela
    def update(e):
        def replace(e):
            preco.value = preco.value.replace(",",".")
            page.update()

        # Funcao que busca os dados de um produto conforme seu ID
        def buscar_produto(e):
            try:
                conexao = sqlite3.connect("basededadoscrud.db")
                
                # Busca o produto conforme o ID fornecido
                cursor = conexao.cursor()
                cursor.execute("SELECT produto, estoque, preco FROM tabeladeprodutos WHERE id = ?;",(id.value,))
                
                # Retorna o primeiro resultado da busca
                resultado = cursor.fetchone()
                
                # Se a busca for sucedida prenche os campos de entrada (produto, estoque e preco) com os dados da busca
                if resultado:
                    produto.value = resultado[0]
                    estoque.value = resultado[1]
                    preco.value = str(resultado[2])
                # Aviso de erro caso a busca nao encontre um resultado
                else:
                    setattr(tela, "open", False)
                    page.update()
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text("Produto não encontrado. Verifique o ID!", color=ft.colors.WHITE),
                        bgcolor=ft.colors.RED,
                        duration=ft.Duration(seconds=2)
                    )
                    page.snack_bar.open = True
                page.update()
            except sqlite3.Error as err:
                setattr(tela, "open", False)
                page.update()
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Erro ao buscar produto: {err}", color=ft.colors.WHITE),
                    bgcolor=ft.colors.RED,
                    duration=ft.Duration(seconds=2)
                )
                page.snack_bar.open = True
            finally:
                conexao.close()
        
        # Funcao que atualiza o produto na tabela somente depois de acionar o botao "Atualizar"
        def atualizar_produto(e):
            try:
                conexao = sqlite3.connect("basededadoscrud.db")
                
                # Atualiza o produto
                cursor = conexao.cursor()
                cursor.execute("UPDATE tabeladeprodutos SET produto = ?, estoque = ?, preco = ? WHERE id = ?;",(produto.value, estoque.value, preco.value, id.value))
                conexao.commit()
                
                if cursor.rowcount == 0:
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text("Erro ao atualizar produto. Verifique se o ID fornecido está correto!", color=ft.colors.WHITE),
                        bgcolor=ft.colors.RED,
                        duration=ft.Duration(seconds=2)
                    )
                else:
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text("Produto atualizado com sucesso!", color=ft.colors.WHITE),
                        bgcolor=ft.colors.GREEN,
                        duration=ft.Duration(seconds=2)
                    )
                page.snack_bar.open = True
                atualizar_page(1)
            except sqlite3.Error as err:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Erro ao atualizar produto: {err}", color=ft.colors.WHITE),
                    bgcolor=ft.colors.RED,
                    duration=ft.Duration(seconds=2)
                )
                page.snack_bar.open = True
            finally:
                conexao.close()
                setattr(tela, "open", False)
                page.update()
        
        id = ft.TextField(label="ID", autofocus=True, width=100)
        produto = ft.TextField(label="Nome do produto")
        estoque = ft.TextField(label="Estoque")
        preco = ft.TextField(label="Preço", on_change=replace)
        tela = ft.AlertDialog(
            title = ft.Text("Atualizar produto"),
            content= ft.Column([
                ft.Text("Insira o id e clique em Buscar:"),
                ft.Row([id,ft.TextButton("Buscar", on_click=buscar_produto)]),
                ft.Column([produto, estoque, preco])
            ]),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e:[setattr(tela, "open", False), page.update()]),
                ft.TextButton("Salvar", on_click=atualizar_produto)
            ],
            open=True
        )
        page.overlay.append(tela)
        page.update()
     
    # Funcao que le os dados da tabela
    def read():
        try:
            conexao = sqlite3.connect("basededadoscrud.db")
            
            # Seleciona todos dados da tabela de produtos
            cursor = conexao.cursor()
            cursor.execute("SELECT  id, produto, estoque, preco FROM tabeladeprodutos;")
            
            # Armazena todas as linhas da consulta em uma lista de tuplas
            resultados = cursor.fetchall()
            return resultados
        except sqlite3.Error as err:
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Erro ao ler banco de dados: {err}", color=ft.colors.WHITE),
                bgcolor=ft.colors.RED,
                duration=ft.Duration(seconds=2)
            )
            page.snack_bar.open = True
            return[]
        finally:
            conexao.close()
    
    # Funcao que apaga todos os dados da tabela
    def truncate(e):
        def excluir_tabela(e):
            try:
                conexao = sqlite3.connect("basededadoscrud.db")
                
                # Apaga todos os produtos da tabela
                cursor = conexao.cursor()
                cursor.execute("DELETE FROM tabeladeprodutos;")
                conexao.commit()

                atualizar_page(1)
            except sqlite3.Error as err:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Erro ao excluir tabela: {err}", color=ft.colors.WHITE),
                    bgcolor=ft.colors.RED,
                    duration=ft.Duration(seconds=2)
                )
                page.snack_bar.open = True
            finally:
                conexao.close()
                setattr(confirmacao, "open", False)
                page.update()

        # Tela de confirmacao      
        confirmacao = ft.AlertDialog(
            title= ft.Text("Tem certeza que deseja excluir os dados da tabela?"),
            content= ft.Text("Essa ação resultará na exclusão definitiva de todos os produto cadastrados na tabela!"),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e:[setattr(confirmacao, "open", False), page.update()]),
                ft.TextButton("Sim", on_click=excluir_tabela)
            ],
            open=True
        )
        page.overlay.append(confirmacao)
        page.update()

    # Funcao que atualiza os elementos da tela
    def atualizar_page(selected_index):

        paginas.controls.clear()
        if selected_index == 0:
            paginas.controls.extend([
                ft.Column([
                    ft.Text("Descrição do software", size=25, font_family='Verdana', weight=ft.FontWeight.BOLD),
                    ft.Text("Este software permite ao usuário realizar operações CRUD em uma tabela SQLite (pré-definida) com as seguintes colunas:"),
                    ft.Text('   • ID - O ID (integer, primary key) é preenchido automaticamente;', size=18, font_family='Times New Roman'),
                    ft.Text('   • Produto - O nome (text) do produto é fornecido pelo usuário;', size=18, font_family='Times New Roman'),
                    ft.Text('   • Estoque - A quantidade (integer) em estoque do produto é fornecida pelo usuário;', size=18, font_family='Times New Roman'),
                    ft.Text('   • Preço - O preço (real) do produto é fornecido pelo usuário;', size=18, font_family='Times New Roman'),
                    ft.Text("Assim, o usuário pode realizar ações simples como: cadastrar um produto (Create), visualizar os produtos cadastrados (Read), atualizar as informações de um produto (Update) e apagar produtos da tabela (Delete). O principal objetivo deste software é demonstrar o uso das operações CRUD."),
                ])
            ])
        elif selected_index == 1:
            # Le os dados do BD
            dados = read()
            
            # Tabela para exibir os dados do BD
            tabela = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("ID")),
                    ft.DataColumn(ft.Text("Produto")),
                    ft.DataColumn(ft.Text("Estoque")),
                    ft.DataColumn(ft.Text("Preço")),
                ],
                rows=[
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(str(linha[0]))),
                            ft.DataCell(ft.Text(linha[1])),
                            ft.DataCell(ft.Text(str(linha[2]))),
                            ft.DataCell(ft.Text(f"R$ {linha[3]:.2f}")),
                        ]
                    ) for linha in dados # Adiciona todos os produtos retornados por read() na tabela
                ]
            )
            
            # Adiciona a tabela em um container com rolagem
            tabela_scroll = ft.Container(
                content=ft.Column(
                    controls=[tabela],
                    scroll=ft.ScrollMode.ALWAYS,
                ),
                    height=415,
            )
            
            # Adiciona a tabela (com rolagem) e os botoes na tela
            paginas.controls.extend([
                tabela_scroll,
                Row([
                    ft.TextButton("Adicionar produto", on_click=create),
                    ft.TextButton("Atualizar produto", on_click=update),
                    ft.TextButton("Remover produto", on_click=delete),
                    ft.TextButton("Limpar tabela", on_click=truncate, style=ft.ButtonStyle(bgcolor=ft.colors.RED, color=ft.colors.WHITE)),
                ])
            ])
        
        page.update()
    
    # Funcao para fechar o software
    def fechar_app(e):
        setattr(aviso, "open", False)
        page.update()
        page.window_close()
    
    # Tela de aviso inicial
    aviso = ft.AlertDialog(
        title= ft.Text("Criar BD SQLite3"),
        content=ft.Container(
            content=ft.Column([
                ft.Text("Clique em continuar para criar o banco de dados local (caso ele não exista)!", size=15),
            ]),
            width=90,
            height=45,
            alignment=ft.alignment.center,
        ),
        actions=[
            ft.TextButton(
                "Cancelar",
                on_click= fechar_app
            ),
            ft.TextButton(
                "Continuar", 
                on_click=lambda e: [
                    setattr(aviso, "open", False),
                    criar_bd(),
                    page.update()
                ]
            ),
        ],
        actions_alignment="end",
        open=True
    )
    page.overlay.append(aviso)
    
    # Menu de opcoes
    lateral = NavigationRail(
        selected_index=0,
        destinations=[
            NavigationRailDestination(
                icon= icons.HOME, selected_icon=icons.HOME, label= "Home"
            ),
            NavigationRailDestination(
                icon= icons.TABLE_ROWS_ROUNDED, selected_icon=icons.TABLE_ROWS_ROUNDED, label= "Tabela"
            ),
        ],
        on_change=lambda e: atualizar_page(e.control.selected_index),
        ) 
    
    # Coluna para exibir o conteudo das paginas
    paginas = Column(expand=True)
    
    
    # Adiciona os elementos a pagina
    page.add(
        Row(
            [
                lateral,
                VerticalDivider(width=1),
                paginas,
            ],
            expand= True
        )
    )
    atualizar_page(0)

app(target=main)