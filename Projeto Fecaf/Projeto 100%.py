# Gastronova - Sistema de Reservas com Banco de Dados
import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import re
from datetime import datetime

# ====== CONEXÃO COM O BANCO DE DADOS ======
def conectar_banco():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="1!Acesso#9",
            database="gastronova"
        )
    except mysql.connector.Error as err:
        messagebox.showerror("Erro de Banco de Dados", f"Erro ao conectar: {err}")
        return None

# ====== FUNÇÕES DO BANCO DE DADOS ======
def obter_clientes():
    conn = conectar_banco()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, nome, telefone, endereco, email FROM clientes")
        clientes = cursor.fetchall()
        conn.close()
        return clientes
    return []

def obter_restaurantes():
    conn = conectar_banco()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, nome, endereco, telefone, mesas FROM restaurantes")
        restaurantes = cursor.fetchall()
        conn.close()
        return restaurantes
    return []

def obter_cardapio_por_restaurante(restaurante_id):
    conn = conectar_banco()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM cardapios WHERE restaurante_id = %s", (restaurante_id,))
        cardapios = cursor.fetchall()
        conn.close()
        return cardapios
    return []

def cadastrar_cliente(nome, telefone, endereco, email=""):
    conn = conectar_banco()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO clientes (nome, telefone, endereco, email) VALUES (%s, %s, %s, %s)",
                (nome, telefone, endereco, email)
            )
            conn.commit()
            return True
        except mysql.connector.Error as err:
            messagebox.showerror("Erro", f"Falha ao cadastrar cliente: {err}")
            return False
        finally:
            conn.close()
    return False

def cadastrar_restaurante(nome, endereco, telefone, mesas):
    conn = conectar_banco()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO restaurantes (nome, endereco, telefone, mesas) VALUES (%s, %s, %s, %s)",
                (nome, endereco, telefone, mesas)
            )
            conn.commit()
            return True
        except mysql.connector.Error as err:
            messagebox.showerror("Erro", f"Falha ao cadastrar restaurante: {err}")
            return False
        finally:
            conn.close()
    return False

def cadastrar_item_cardapio(restaurante_id, nome, descricao, preco, vegetariano, vegano, carnivoro):
    conn = conectar_banco()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO cardapios 
                (restaurante_id, nome, descricao, preco, vegetariano, vegano, carnivoro) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (restaurante_id, nome, descricao, preco, vegetariano, vegano, carnivoro)
            )
            conn.commit()
            return True
        except mysql.connector.Error as err:
            messagebox.showerror("Erro", f"Falha ao cadastrar item: {err}")
            return False
        finally:
            conn.close()
    return False

def fazer_reserva(cliente_id, restaurante_id, data, hora, qtd_mesas):
    conn = conectar_banco()
    if conn:
        try:
            # Verificar disponibilidade
            cursor = conn.cursor()
            cursor.execute(
                "SELECT mesas FROM restaurantes WHERE id = %s", 
                (restaurante_id,)
            )
            total_mesas = cursor.fetchone()[0]
            
            cursor.execute(
                """SELECT SUM(qtd_mesas) FROM reservas 
                WHERE restaurante_id = %s AND data = %s""",
                (restaurante_id, data)
            )
            reservadas = cursor.fetchone()[0] or 0
            
            if (total_mesas - reservadas) < int(qtd_mesas):
                messagebox.showwarning(
                    "Mesas Insuficientes", 
                    f"Só há {total_mesas - reservadas} mesa(s) disponível(is)"
                )
                return False

            # Efetuar reserva
            cursor.execute(
                """INSERT INTO reservas 
                (cliente_id, restaurante_id, data, hora, qtd_mesas) 
                VALUES (%s, %s, %s, %s, %s)""",
                (cliente_id, restaurante_id, data, hora, qtd_mesas)
            )
            conn.commit()
            return True
        except mysql.connector.Error as err:
            messagebox.showerror("Erro", f"Falha na reserva: {err}")
            return False
        finally:
            conn.close()
    return False

def obter_todas_reservas():
    conn = conectar_banco()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT r.id, c.nome AS cliente_nome, res.nome AS restaurante_nome, 
                   r.data, r.hora, r.qtd_mesas
            FROM reservas r
            JOIN clientes c ON r.cliente_id = c.id
            JOIN restaurantes res ON r.restaurante_id = res.id
            ORDER BY r.data, r.hora
        """)
        reservas = cursor.fetchall()
        conn.close()
        return reservas
    return []

# ====== INTERFACE GRÁFICA ======
root = tk.Tk()
root.title("Gastronova - Sistema de Reservas")
root.geometry("700x550")
root.configure(bg="#f0f0f0")

style = ttk.Style()
style.theme_use('clam')
style.configure('TNotebook.Tab', padding=[10, 5], font=('Arial', 11, 'bold'))
style.configure('TButton', font=('Arial', 10), padding=5)
style.configure('TLabel', font=('Arial', 10))

notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True, padx=10, pady=10)

# ====== VALIDAÇÕES ======
def validar_telefone(telefone):
    return telefone.isdigit()

def validar_endereco(endereco):
    return bool(re.search(r"[a-zA-Z]", endereco)) and bool(re.search(r"\d", endereco))

def validar_numero(valor):
    return valor.isdigit()

def validar_data(data_str):
    try:
        datetime.strptime(data_str, "%d/%m/%Y")
        return True
    except ValueError:
        return False

def validar_horario(hora_str):
    try:
        datetime.strptime(hora_str, "%H:%M")
        return True
    except ValueError:
        return False

# ====== ABA CLIENTE ======
aba_cliente = ttk.Frame(notebook)
notebook.add(aba_cliente, text="Cliente")

def abrir_cadastro_cliente():
    janela = tk.Toplevel(root)
    janela.title("Cadastro de Cliente")
    janela.geometry("400x400")

    ttk.Label(janela, text="Nome:").pack(pady=2)
    nome_entry = ttk.Entry(janela)
    nome_entry.pack()

    ttk.Label(janela, text="Telefone (apenas números):").pack(pady=2)
    telefone_entry = ttk.Entry(janela)
    telefone_entry.pack()

    ttk.Label(janela, text="Endereço (rua e número):").pack(pady=2)
    endereco_entry = ttk.Entry(janela)
    endereco_entry.pack()

    ttk.Label(janela, text="E-mail (opcional):").pack(pady=2)
    email_entry = ttk.Entry(janela)
    email_entry.pack()

    def salvar():
        nome = nome_entry.get().strip()
        telefone = telefone_entry.get().strip()
        endereco = endereco_entry.get().strip()
        email = email_entry.get().strip()

        if not nome or not telefone or not endereco:
            messagebox.showerror("Erro", "Preencha todos os campos obrigatórios.")
            return
        if not validar_telefone(telefone):
            messagebox.showerror("Erro", "Telefone inválido.")
            return
        if not validar_endereco(endereco):
            messagebox.showerror("Erro", "Endereço inválido.")
            return

        if cadastrar_cliente(nome, telefone, endereco, email):
            messagebox.showinfo("Sucesso", "Cliente cadastrado!")
            janela.destroy()

    ttk.Button(janela, text="Cadastrar", command=salvar).pack(pady=10)

def abrir_reserva():
    clientes_db = obter_clientes()
    restaurantes_db = obter_restaurantes()
    
    if not clientes_db or not restaurantes_db:
        messagebox.showwarning("Aviso", "Cadastre cliente e restaurante antes de reservar.")
        return

    janela = tk.Toplevel(root)
    janela.title("Reserva de Mesa")
    janela.geometry("450x650")

    # Widgets para seleção
    ttk.Label(janela, text="Cliente:").pack()
    cliente_var = tk.StringVar()
    cliente_opcoes = [f"{c['id']} - {c['nome']}" for c in clientes_db]
    cliente_var.set(cliente_opcoes[0])
    ttk.OptionMenu(janela, cliente_var, cliente_opcoes[0], *cliente_opcoes).pack()

    ttk.Label(janela, text="Restaurante:").pack()
    restaurante_var = tk.StringVar()
    restaurante_opcoes = [f"{r['id']} - {r['nome']}" for r in restaurantes_db]
    restaurante_var.set(restaurante_opcoes[0])
    ttk.OptionMenu(janela, restaurante_var, restaurante_opcoes[0], *restaurante_opcoes).pack()

    # Campos de entrada
    campos = [
        ("Data (DD/MM/AAAA):", ttk.Entry(janela)),
        ("Horário (HH:MM):", ttk.Entry(janela)),
        ("Quantidade de Mesas:", ttk.Entry(janela))
    ]
    
    for texto, entrada in campos:
        ttk.Label(janela, text=texto).pack()
        entrada.pack()

    data_entry, horario_entry, mesas_entry = [entrada for _, entrada in campos]

    # Cardápio
    ttk.Label(janela, text="Cardápio:").pack(pady=(10, 0))
    lista_cardapio = tk.Listbox(janela, width=50, height=6)
    lista_cardapio.pack()

    def atualizar_cardapio(*args):
        lista_cardapio.delete(0, tk.END)
        restaurante_id = int(restaurante_var.get().split(" - ")[0])
        cardapios = obter_cardapio_por_restaurante(restaurante_id)
        
        for item in cardapios:
            tags = []
            if item['vegetariano']: tags.append("Vegetariano")
            if item['vegano']: tags.append("Vegano")
            if item['carnivoro']: tags.append("Carnívoro")
            desc = f"{item['nome']} - R${item['preco']:.2f} - {item['descricao']} ({', '.join(tags)})"
            lista_cardapio.insert(tk.END, desc)

    restaurante_var.trace("w", atualizar_cardapio)
    atualizar_cardapio()

    def reservar():
        cliente_id = int(cliente_var.get().split(" - ")[0])
        restaurante_id = int(restaurante_var.get().split(" - ")[0])
    
        data_str = data_entry.get().strip()
        try:
            data = datetime.strptime(data_str, "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Erro", "Data inválida. Use o formato DD/MM/AAAA.")
            return

        hora = horario_entry.get().strip()
        qtd_mesas = mesas_entry.get().strip()

        if not validar_horario(hora):
            messagebox.showerror("Erro", "Horário inválido. Use HH:MM.")
            return
        if not validar_numero(qtd_mesas):
            messagebox.showerror("Erro", "Número de mesas inválido.")
            return

        if fazer_reserva(cliente_id, restaurante_id, data, hora, int(qtd_mesas)):
            messagebox.showinfo("Sucesso", "Reserva feita!")
            janela.destroy()


    ttk.Button(janela, text="Reservar", command=reservar).pack(pady=10)

# Botões da aba Cliente
ttk.Button(aba_cliente, text="Cadastro de Cliente", command=abrir_cadastro_cliente).pack(pady=10)
ttk.Button(aba_cliente, text="Fazer Reserva", command=abrir_reserva).pack(pady=10)

# ====== ABA RESTAURANTE ======
aba_restaurante = ttk.Frame(notebook)
notebook.add(aba_restaurante, text="Restaurante")

def abrir_cadastro_restaurante():
    janela = tk.Toplevel(root)
    janela.title("Cadastro de Restaurante")
    janela.geometry("400x350")

    campos = [
        ("Nome:", ttk.Entry(janela)),
        ("Endereço:", ttk.Entry(janela)),
        ("Telefone:", ttk.Entry(janela)),
        ("Quantidade de Mesas:", ttk.Entry(janela))
    ]
    
    for texto, entrada in campos:
        ttk.Label(janela, text=texto).pack()
        entrada.pack()

    nome_entry, endereco_entry, telefone_entry, mesas_entry = [entrada for _, entrada in campos]

    def salvar():
        nome = nome_entry.get().strip()
        endereco = endereco_entry.get().strip()
        telefone = telefone_entry.get().strip()
        mesas = mesas_entry.get().strip()

        if not all([nome, endereco, telefone, mesas]):
            messagebox.showerror("Erro", "Preencha todos os campos.")
            return
        if not validar_telefone(telefone) or not validar_numero(mesas):
            messagebox.showerror("Erro", "Telefone ou quantidade inválidos.")
            return

        if cadastrar_restaurante(nome, endereco, telefone, int(mesas)):
            messagebox.showinfo("Sucesso", "Restaurante cadastrado!")
            janela.destroy()

    ttk.Button(janela, text="Cadastrar", command=salvar).pack(pady=10)

def abrir_cadastro_cardapio():
    restaurantes_db = obter_restaurantes()
    if not restaurantes_db:
        messagebox.showwarning("Aviso", "Cadastre um restaurante primeiro.")
        return

    janela = tk.Toplevel(root)
    janela.title("Cadastro de Cardápio")
    janela.geometry("400x550")

    # Seleção de restaurante
    ttk.Label(janela, text="Restaurante:").pack()
    rest_var = tk.StringVar()
    opcoes_restaurantes = [f"{r['id']} - {r['nome']}" for r in restaurantes_db]
    rest_var.set(opcoes_restaurantes[0])
    ttk.OptionMenu(janela, rest_var, opcoes_restaurantes[0], *opcoes_restaurantes).pack()

    # Campos do prato
    campos_prato = [
        ("Nome do prato:", ttk.Entry(janela)),
        ("Descrição:", ttk.Entry(janela)),
        ("Preço (R$):", ttk.Entry(janela))
    ]
    
    for texto, entrada in campos_prato:
        ttk.Label(janela, text=texto).pack()
        entrada.pack()

    nome_prato, desc_prato, preco_prato = [entrada for _, entrada in campos_prato]

    # Checkboxes
    vegetariano = tk.BooleanVar()
    vegano = tk.BooleanVar()
    carnivoro = tk.BooleanVar()

    ttk.Checkbutton(janela, text="Vegetariano", variable=vegetariano).pack()
    ttk.Checkbutton(janela, text="Vegano", variable=vegano).pack()
    ttk.Checkbutton(janela, text="Carnívoro", variable=carnivoro).pack()

    def salvar():
        restaurante_id = int(rest_var.get().split(" - ")[0])
        nome = nome_prato.get().strip()
        descricao = desc_prato.get().strip()
        preco = preco_prato.get().strip()

        if not nome or not descricao or not preco:
            messagebox.showerror("Erro", "Nome, descrição e preço são obrigatórios.")
            return

        try:
            preco_float = float(preco)
        except ValueError:
            messagebox.showerror("Erro", "Preço inválido.")
            return

        if cadastrar_item_cardapio(
            restaurante_id, nome, descricao, preco_float,
            vegetariano.get(), vegano.get(), carnivoro.get()
        ):
            messagebox.showinfo("Sucesso", "Prato adicionado ao cardápio!")
            janela.destroy()

    ttk.Button(janela, text="Cadastrar Prato", command=salvar).pack(pady=10)

def ver_reservas():
    reservas = obter_todas_reservas()
    if not reservas:
        messagebox.showinfo("Informação", "Nenhuma reserva registrada.")
        return

    janela = tk.Toplevel(root)
    janela.title("Lista de Reservas")
    janela.geometry("600x400")

    # Criando um Treeview para exibir os dados
    tree = ttk.Treeview(janela, columns=("Data", "Hora", "Cliente", "Restaurante", "Mesas"), show="headings")
    tree.heading("Data", text="Data")
    tree.heading("Hora", text="Hora")
    tree.heading("Cliente", text="Cliente")
    tree.heading("Restaurante", text="Restaurante")
    tree.heading("Mesas", text="Mesas")
    
    # Ajustando as colunas
    tree.column("Data", width=80)
    tree.column("Hora", width=60)
    tree.column("Cliente", width=120)
    tree.column("Restaurante", width=120)
    tree.column("Mesas", width=60)
    
    tree.pack(fill="both", expand=True, padx=10, pady=10)

    for reserva in reservas:
        tree.insert("", "end", values=(
            reserva['data'],
            reserva['hora'],
            reserva['cliente_nome'],
            reserva['restaurante_nome'],
            reserva['qtd_mesas']
        ))

def editar_restaurante():
    conn = conectar_banco()
    if conn:
        cursor = conn.cursor()

        def selecionar_restaurante():
            restaurante_id = combo_restaurantes.get().split(" - ")[0]
            cursor.execute("SELECT nome, endereco, telefone, mesas FROM restaurantes WHERE id = %s", (restaurante_id,))
            dados = cursor.fetchone()

            if dados:
                entry_nome.delete(0, tk.END)
                entry_nome.insert(0, dados[0])
                entry_endereco.delete(0, tk.END)
                entry_endereco.insert(0, dados[1])
                entry_telefone.delete(0, tk.END)
                entry_telefone.insert(0, dados[2])
                entry_mesas.delete(0, tk.END)
                entry_mesas.insert(0, str(dados[3]))

        def salvar_edicao():
            restaurante_id = combo_restaurantes.get().split(" - ")[0]
            nome = entry_nome.get()
            endereco = entry_endereco.get()
            telefone = entry_telefone.get()
            numero_mesas = entry_mesas.get()

            if not nome or not endereco or not telefone or not numero_mesas:
                messagebox.showwarning("Atenção", "Todos os campos são obrigatórios!")
                return

            try:
                cursor.execute("""
                    UPDATE restaurantes
                    SET nome=%s, endereco=%s, telefone=%s, mesas=%s
                    WHERE id=%s
                """, (nome, endereco, telefone, numero_mesas, restaurante_id))
                conn.commit()
                messagebox.showinfo("Sucesso", "Restaurante atualizado com sucesso!")
                janela.destroy()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao atualizar restaurante: {e}")
            finally:
                conn.close()

        janela = tk.Toplevel(root)
        janela.title("Editar Restaurante")

        tk.Label(janela, text="Selecione o Restaurante:").grid(row=0, column=0)
        cursor.execute("SELECT id, nome FROM restaurantes")
        restaurantes = [f"{id} - {nome}" for id, nome in cursor.fetchall()]
        combo_restaurantes = ttk.Combobox(janela, values=restaurantes, state="readonly")
        combo_restaurantes.grid(row=0, column=1)
        tk.Button(janela, text="Carregar", command=selecionar_restaurante).grid(row=0, column=2)

        tk.Label(janela, text="Nome:").grid(row=1, column=0)
        entry_nome = tk.Entry(janela)
        entry_nome.grid(row=1, column=1)

        tk.Label(janela, text="Endereço:").grid(row=2, column=0)
        entry_endereco = tk.Entry(janela)
        entry_endereco.grid(row=2, column=1)

        tk.Label(janela, text="Telefone:").grid(row=3, column=0)
        entry_telefone = tk.Entry(janela)
        entry_telefone.grid(row=3, column=1)

        tk.Label(janela, text="Número de Mesas:").grid(row=4, column=0)
        entry_mesas = tk.Entry(janela)
        entry_mesas.grid(row=4, column=1)

        tk.Button(janela, text="Salvar", command=salvar_edicao).grid(row=5, column=0, columnspan=2)



def editar_cardapio():
    conn = conectar_banco()
    if conn:
        cursor = conn.cursor()

        def carregar_cardapio():
            restaurante_id = combo_restaurantes.get().split(" - ")[0]
            cursor.execute("SELECT id, nome FROM cardapios WHERE restaurante_id = %s", (restaurante_id,))
            pratos = [f"{id} - {nome}" for id, nome in cursor.fetchall()]
            combo_pratos.config(values=pratos)

        def carregar_dados_prato():
            prato_id = combo_pratos.get().split(" - ")[0]
            cursor.execute("SELECT nome, descricao, preco, vegetariano, vegano, carnivoro FROM cardapios WHERE id = %s", (prato_id,))
            dados = cursor.fetchone()
            if dados:
                entry_nome.delete(0, tk.END)
                entry_nome.insert(0, dados[0])
                entry_desc.delete(0, tk.END)
                entry_desc.insert(0, dados[1])
                entry_preco.delete(0, tk.END)
                entry_preco.insert(0, str(dados[2]))
                var_veg.set(bool(dados[3]))
                var_vgn.set(bool(dados[4]))
                var_car.set(bool(dados[5]))

        def salvar_cardapio():
            prato_id = combo_pratos.get().split(" - ")[0]
            nome = entry_nome.get()
            descricao = entry_desc.get()
            preco = entry_preco.get()
            vegetariano = var_veg.get()
            vegano = var_vgn.get()
            carnivoro = var_car.get()

            try:
                cursor.execute("""
                    UPDATE cardapios SET nome=%s, descricao=%s, preco=%s,
                    vegetariano=%s, vegano=%s, carnivoro=%s WHERE id=%s
                """, (nome, descricao, preco, vegetariano, vegano, carnivoro, prato_id))
                conn.commit()
                messagebox.showinfo("Sucesso", "Prato atualizado com sucesso!")
                janela.destroy()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao atualizar prato: {e}")
            finally:
                conn.close()

        janela = tk.Toplevel(root)
        janela.title("Editar Cardápio")

        tk.Label(janela, text="Restaurante:").grid(row=0, column=0)
        cursor.execute("SELECT id, nome FROM restaurantes")
        restaurantes = [f"{id} - {nome}" for id, nome in cursor.fetchall()]
        combo_restaurantes = ttk.Combobox(janela, values=restaurantes, state="readonly")
        combo_restaurantes.grid(row=0, column=1)
        tk.Button(janela, text="Carregar Pratos", command=carregar_cardapio).grid(row=0, column=2)

        tk.Label(janela, text="Prato:").grid(row=1, column=0)
        combo_pratos = ttk.Combobox(janela, state="readonly")
        combo_pratos.grid(row=1, column=1)
        tk.Button(janela, text="Carregar Dados", command=carregar_dados_prato).grid(row=1, column=2)

        tk.Label(janela, text="Nome:").grid(row=2, column=0)
        entry_nome = tk.Entry(janela)
        entry_nome.grid(row=2, column=1)

        tk.Label(janela, text="Descrição:").grid(row=3, column=0)
        entry_desc = tk.Entry(janela)
        entry_desc.grid(row=3, column=1)

        tk.Label(janela, text="Preço:").grid(row=4, column=0)
        entry_preco = tk.Entry(janela)
        entry_preco.grid(row=4, column=1)

        var_veg = tk.BooleanVar()
        var_vgn = tk.BooleanVar()
        var_car = tk.BooleanVar()

        tk.Checkbutton(janela, text="Vegetariano", variable=var_veg).grid(row=5, column=0)
        tk.Checkbutton(janela, text="Vegano", variable=var_vgn).grid(row=5, column=1)
        tk.Checkbutton(janela, text="Carnívoro", variable=var_car).grid(row=5, column=2)

        tk.Button(janela, text="Salvar", command=salvar_cardapio).grid(row=6, column=0, columnspan=3)


def editar_reserva():
    reservas = obter_todas_reservas()
    clientes = obter_clientes()
    restaurantes = obter_restaurantes()
    
    if not reservas:
        messagebox.showinfo("Informação", "Nenhuma reserva registrada.")
        return

    janela = tk.Toplevel(root)
    janela.title("Editar Reserva")
    janela.geometry("500x500")

    tk.Label(janela, text="Selecione a Reserva:").pack()
    reservas_var = tk.StringVar()
    opcoes_reservas = [
        f"{r['id']} - {r['cliente_nome']} em {r['restaurante_nome']} ({r['data']} às {r['hora']})"
        for r in reservas
    ]
    reservas_var.set(opcoes_reservas[0])
    ttk.OptionMenu(janela, reservas_var, opcoes_reservas[0], *opcoes_reservas).pack(pady=5)

    # Campos para edição
    cliente_var = tk.StringVar()
    cliente_opcoes = [f"{c['id']} - {c['nome']}" for c in clientes]
    restaurante_var = tk.StringVar()
    restaurante_opcoes = [f"{r['id']} - {r['nome']}" for r in restaurantes]

    data_entry = ttk.Entry(janela)
    hora_entry = ttk.Entry(janela)
    mesas_entry = ttk.Entry(janela)

    def carregar_dados():
        reserva_id = int(reservas_var.get().split(" - ")[0])
        reserva = next(r for r in reservas if r['id'] == reserva_id)

        cliente_match = next((c for c in cliente_opcoes if f" - {reserva['cliente_nome']}" in c), "")
        restaurante_match = next((r for r in restaurante_opcoes if f" - {reserva['restaurante_nome']}" in r), "")

        cliente_var.set(cliente_match)
        restaurante_var.set(restaurante_match)
        data_entry.delete(0, tk.END)
        data_entry.insert(0, reserva['data'])
        hora_entry.delete(0, tk.END)
        hora_entry.insert(0, reserva['hora'])
        mesas_entry.delete(0, tk.END)
        mesas_entry.insert(0, str(reserva['qtd_mesas']))

    ttk.Button(janela, text="Carregar Dados", command=carregar_dados).pack(pady=5)

    ttk.Label(janela, text="Cliente:").pack()
    cliente_menu = ttk.Combobox(janela, textvariable=cliente_var, values=cliente_opcoes, state="readonly")
    cliente_menu.pack()

    ttk.Label(janela, text="Restaurante:").pack()
    restaurante_menu = ttk.Combobox(janela, textvariable=restaurante_var, values=restaurante_opcoes, state="readonly")
    restaurante_menu.pack()

    ttk.Label(janela, text="Data (DD/MM/AAAA):").pack()
    data_entry.pack()
    ttk.Label(janela, text="Horário (HH:MM):").pack()
    hora_entry.pack()
    ttk.Label(janela, text="Quantidade de Mesas:").pack()
    mesas_entry.pack()

    def salvar_alteracao():
        reserva_id = int(reservas_var.get().split(" - ")[0])

        try:
            cliente_id = int(cliente_menu.get().split(" - ")[0])
            restaurante_id = int(restaurante_menu.get().split(" - ")[0])
        except (IndexError, ValueError):
            messagebox.showerror("Erro", "Selecione cliente e restaurante válidos.")
            return

        data_str = data_entry.get().strip()
        try:
            data = datetime.strptime(data_str, "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Erro", "Data inválida. Use o formato DD/MM/AAAA.")
            return

        hora = hora_entry.get().strip()
        qtd_mesas = mesas_entry.get().strip()

        if not validar_horario(hora) or not validar_numero(qtd_mesas):
            messagebox.showerror("Erro", "Dados inválidos. Verifique os campos.")
            return

        conn = conectar_banco()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT mesas FROM restaurantes WHERE id = %s", (restaurante_id,))
                total_mesas = cursor.fetchone()[0]
                cursor.execute("""
                    SELECT SUM(qtd_mesas) FROM reservas
                    WHERE restaurante_id = %s AND data = %s AND id != %s
                """, (restaurante_id, data, reserva_id))
                reservadas = cursor.fetchone()[0] or 0

                if total_mesas - reservadas < int(qtd_mesas):
                    messagebox.showwarning("Mesas Insuficientes", f"Só há {total_mesas - reservadas} mesa(s) disponível(is).")
                    return

                cursor.execute("""
                    UPDATE reservas SET cliente_id=%s, restaurante_id=%s, data=%s, hora=%s, qtd_mesas=%s
                    WHERE id=%s
                """, (cliente_id, restaurante_id, data, hora, int(qtd_mesas), reserva_id))
                conn.commit()
                messagebox.showinfo("Sucesso", "Reserva atualizada com sucesso!")
                janela.destroy()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao atualizar reserva: {e}")
            finally:
                conn.close()

    ttk.Button(janela, text="Salvar Alterações", command=salvar_alteracao).pack(pady=10)


# Botões da aba Restaurante
ttk.Button(aba_restaurante, text="Cadastro de Restaurante", command=abrir_cadastro_restaurante).pack(pady=10)
ttk.Button(aba_restaurante, text="Editar Restaurante", command=editar_restaurante).pack(pady=5)
ttk.Button(aba_restaurante, text="Cadastro de Cardápio", command=abrir_cadastro_cardapio).pack(pady=10)
ttk.Button(aba_restaurante, text="Editar Cardápio", command=editar_cardapio).pack(pady=5)
ttk.Button(aba_restaurante, text="Ver Reservas", command=ver_reservas).pack(pady=10)
ttk.Button(aba_restaurante, text="Editar Reserva", command=lambda: editar_reserva()).pack(pady=5)

# ====== ABA CADASTRO DE CLIENTE ======
aba_cadastro_cliente = ttk.Frame(notebook)
notebook.add(aba_cadastro_cliente, text="Cadastro de Cliente")

tree_clientes = ttk.Treeview(aba_cadastro_cliente, columns=("ID", "Nome", "Telefone", "Endereço", "Email"), show="headings")
tree_clientes.heading("ID", text="ID")
tree_clientes.heading("Nome", text="Nome")
tree_clientes.heading("Telefone", text="Telefone")
tree_clientes.heading("Endereço", text="Endereço")
tree_clientes.heading("Email", text="Email")

tree_clientes.column("ID", width=40)
tree_clientes.column("Nome", width=150)
tree_clientes.column("Telefone", width=100)
tree_clientes.column("Endereço", width=200)
tree_clientes.column("Email", width=150)

tree_clientes.pack(fill="both", expand=True, padx=10, pady=10)

def carregar_clientes():
    tree_clientes.delete(*tree_clientes.get_children())
    for c in obter_clientes():
        tree_clientes.insert("", "end", values=(c['id'], c['nome'], c['telefone'], c['endereco'], c['email']))

def editar_cliente():
    item = tree_clientes.selection()
    if not item:
        messagebox.showwarning("Aviso", "Selecione um cliente para editar.")
        return
    valores = tree_clientes.item(item[0], "values")
    cliente_id, nome, telefone, endereco, email = valores

    janela = tk.Toplevel(root)
    janela.title("Editar Cliente")
    janela.geometry("400x300")

    ttk.Label(janela, text="Nome:").pack(pady=2)
    nome_entry = ttk.Entry(janela)
    nome_entry.insert(0, nome)
    nome_entry.pack()

    ttk.Label(janela, text="Telefone:").pack(pady=2)
    telefone_entry = ttk.Entry(janela)
    telefone_entry.insert(0, telefone)
    telefone_entry.pack()

    ttk.Label(janela, text="Endereço:").pack(pady=2)
    endereco_entry = ttk.Entry(janela)
    endereco_entry.insert(0, endereco)
    endereco_entry.pack()

    ttk.Label(janela, text="Email:").pack(pady=2)
    email_entry = ttk.Entry(janela)
    email_entry.insert(0, email)
    email_entry.pack()

    def salvar():
        novo_nome = nome_entry.get().strip()
        novo_telefone = telefone_entry.get().strip()
        novo_endereco = endereco_entry.get().strip()
        novo_email = email_entry.get().strip()

        if not novo_nome or not novo_telefone or not novo_endereco:
            messagebox.showerror("Erro", "Preencha todos os campos obrigatórios.")
            return

        conn = conectar_banco()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE clientes SET nome=%s, telefone=%s, endereco=%s, email=%s
                    WHERE id=%s
                """, (novo_nome, novo_telefone, novo_endereco, novo_email, cliente_id))
                conn.commit()
                messagebox.showinfo("Sucesso", "Cliente atualizado!")
                carregar_clientes()
                janela.destroy()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao atualizar cliente: {e}")
            finally:
                conn.close()

    ttk.Button(janela, text="Salvar", command=salvar).pack(pady=10)

ttk.Button(aba_cadastro_cliente, text="Editar Cadastro", command=editar_cliente).pack(pady=5)
carregar_clientes()



root.mainloop()