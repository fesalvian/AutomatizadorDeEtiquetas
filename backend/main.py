# backend/main.py

import tkinter as tk
from tkinter import ttk, messagebox
import requests
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
import os
import subprocess
import sys
import time



# ---- Configuração da folha ----
PAGE_WIDTH, PAGE_HEIGHT = A4
COLS = 3
ROWS = 6
LABELS_PER_PAGE = COLS * ROWS

# Margens
MARGIN_LEFT = 6 * mm
MARGIN_RIGHT = 6 * mm
MARGIN_TOP = 10 * mm
MARGIN_BOTTOM = 10 * mm

CONTENT_WIDTH = PAGE_WIDTH - (MARGIN_LEFT + MARGIN_RIGHT)
CONTENT_HEIGHT = PAGE_HEIGHT - (MARGIN_TOP + MARGIN_BOTTOM)
LABEL_WIDTH = CONTENT_WIDTH / COLS
LABEL_HEIGHT = CONTENT_HEIGHT / ROWS

def iniciar_backend():
    # ===== BLOQUEIO CONTRA MULTIPLAS INSTANCIAS =====
    # Caminho do .exe (dist)
    base_path = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.getcwd()
    lock_file = os.path.join(base_path, "server.lock")

    # Se já existe lock → backend já foi iniciado → não inicia de novo
    if os.path.exists(lock_file):
        return

    # Cria o lock para impedir criar outro backend
    with open(lock_file, "w") as f:
        f.write("running")

    # ===== INICIA O BACKEND =====
    if getattr(sys, 'frozen', False):
        # Executável gerado
        server_path = os.path.join(base_path, "run_server.exe")
        subprocess.Popen(
            [server_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
    else:
        # Rodando via Python normal
        python = sys.executable
        subprocess.Popen(
            [python, "run_server.py"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

    time.sleep(1.2)


def next_filename(base="etiquetas", ext=".pdf"):
    i = 1
    while True:
        name = f"{base}{i:03d}{ext}"
        if not os.path.exists(name):
            return name
        i += 1


def draw_label(c, x, y, comodo, peca, medida, font_sizes):
    c.saveState()
    center_y = y + LABEL_HEIGHT / 2
    center_x = x + LABEL_WIDTH / 2

    c.setFont("Helvetica-Bold", font_sizes["comodo"])
    c.drawCentredString(center_x, center_y + 15, comodo)

    c.setFont("Helvetica-Bold", font_sizes["peca"])
    c.drawCentredString(center_x, center_y - 5, peca)

    c.setFont("Helvetica", font_sizes["medida"])
    c.drawCentredString(center_x, center_y - 25, medida)

    c.restoreState()


def gerar_etiquetas(dados, font_sizes):
    nome_arquivo = next_filename()
    c = canvas.Canvas(nome_arquivo, pagesize=A4)

    x_positions = [MARGIN_LEFT + i * LABEL_WIDTH for i in range(COLS)]
    y_positions = [MARGIN_BOTTOM + j * LABEL_HEIGHT for j in range(ROWS)]

    i = 0
    for item in dados:
        for _ in range(item["quantidade"]):
            col = i % COLS
            row = (i // COLS) % ROWS
            row_inverted = ROWS - 1 - row

            if i > 0 and i % LABELS_PER_PAGE == 0:
                c.showPage()

            draw_label(
                c,
                x_positions[col],
                y_positions[row_inverted],
                item["comodo"],
                item["peca"],
                item["medida"],
                font_sizes,
            )
            i += 1

    c.save()
    return os.path.abspath(nome_arquivo)

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Automatizador de Etiquetas")
        self.root.geometry("1080x740")

        self.dados = []
        self.current_page = 0
        self.editing_id = None  # <-- modo edição

        # --- UI ---
        style = ttk.Style()
        style.theme_use("clam")

        BG_MAIN = "#f8fafc"
        BG_FRAME = "#ffffff"
        PRIMARY = "#2563eb"

        self.root.configure(bg=BG_MAIN)

        main_frame = ttk.Frame(root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # ESQUERDA
        left = ttk.Frame(main_frame, padding=15)
        left.pack(side="left", fill="y", padx=(0, 20))

        ttk.Label(left, text="Automatizador de Etiquetas").pack(pady=(0, 15))

        ttk.Label(left, text="Cômodo:").pack(anchor="w")
        self.entry_comodo = ttk.Entry(left, width=40)
        self.entry_comodo.pack(pady=5)

        ttk.Label(left, text="Peça:").pack(anchor="w")
        self.entry_peca = ttk.Entry(left, width=40)
        self.entry_peca.pack(pady=5)

        ttk.Label(left, text="Medida (0000 x 0000):").pack(anchor="w")
        medida_frame = ttk.Frame(left)
        medida_frame.pack(pady=5)

        self.entry_medida1 = ttk.Entry(medida_frame, width=8)
        self.entry_medida1.pack(side="left")
        ttk.Label(medida_frame, text=" x ").pack(side="left", padx=5)
        self.entry_medida2 = ttk.Entry(medida_frame, width=8)
        self.entry_medida2.pack(side="left")

        ttk.Label(left, text="Quantidade:").pack(anchor="w")
        self.entry_quantidade = ttk.Entry(left, width=15)
        self.entry_quantidade.pack(pady=5)
        self.entry_quantidade.bind("<Return>", self.salvar)

        ttk.Button(left, text="➕ Adicionar Etiqueta", command=self.adicionar).pack(fill="x", pady=5)
        ttk.Button(left, text="✏️ Editar Selecionado", command=self.editar).pack(fill="x", pady=5)
        ttk.Button(left, text="❌ Excluir Selecionado", command=self.excluir).pack(fill="x", pady=5)
        ttk.Button(left, text="🖨️ Gerar PDF", command=self.gerar_pdf).pack(fill="x", pady=5)
        ttk.Button(left, text="🗑️ Limpar Tudo", command=self.limpar).pack(fill="x", pady=5)

        ttk.Label(left, text="Lista de etiquetas:").pack(anchor="w", pady=(15, 5))
        self.lista = tk.Listbox(left, width=55, height=15)
        self.lista.pack()

        # DIREITA
        right = ttk.Frame(main_frame, padding=15)
        right.pack(side="right", fill="both", expand=True)

        ttk.Label(right, text="Preview da Folha A4 (3x6)").pack()
        self.canvas_preview = tk.Canvas(right, width=500, height=680, bg="white")
        self.canvas_preview.pack(pady=10)

        nav = ttk.Frame(right)
        nav.pack()
        ttk.Button(nav, text="⬅️ Página anterior", command=self.prev_page).pack(side="left", padx=10)
        ttk.Button(nav, text="➡️ Próxima página", command=self.next_page).pack(side="left", padx=10)
        self.page_label = ttk.Label(nav, text="Página 1")
        self.page_label.pack(side="left", padx=10)

        self.draw_grid()
        self.root.after(800, self.sync_with_server)

    # -----------------------
    # ADICIONAR
    # -----------------------
    def adicionar(self):
        if self.editing_id is not None:
            return self.salvar()

        comodo = self.entry_comodo.get().strip()
        peca = self.entry_peca.get().strip()
        m1 = self.entry_medida1.get().strip()
        m2 = self.entry_medida2.get().strip()

        try:
            qtd = int(self.entry_quantidade.get())
        except:
            return messagebox.showerror("Erro", "Quantidade inválida!")

        if not comodo or not peca or not m1 or not m2:
            return messagebox.showwarning("Aviso", "Preencha todos os campos!")

        item = {
            "comodo": comodo,
            "peca": peca,
            "medida1": m1,
            "medida2": m2,
            "quantidade": qtd,
        }

        requests.post("http://127.0.0.1:8000/add-label", json=item)
        self.limpar_inputs()
        self.sync_with_server()

    # -----------------------
    # INICIAR EDIÇÃO
    # -----------------------
    def editar(self):
        sel = self.lista.curselection()
        if not sel:
            return messagebox.showwarning("Aviso", "Selecione um item para editar.")

        idx = sel[0]
        item = self.dados[idx]

        self.editing_id = item["id"]

        self.entry_comodo.delete(0, tk.END)
        self.entry_comodo.insert(0, item["comodo"])

        self.entry_peca.delete(0, tk.END)
        self.entry_peca.insert(0, item["peca"])

        m1, m2 = item["medida"].split(" x ")
        self.entry_medida1.delete(0, tk.END)
        self.entry_medida1.insert(0, m1)

        self.entry_medida2.delete(0, tk.END)
        self.entry_medida2.insert(0, m2)

        self.entry_quantidade.delete(0, tk.END)
        self.entry_quantidade.insert(0, item["quantidade"])

        messagebox.showinfo("Edição", "Altere os campos e pressione ENTER para salvar.")

    # -----------------------
    # SALVAR EDIÇÃO
    # -----------------------
    def salvar(self, event=None):
        if self.editing_id is None:
            return self.adicionar()

        comodo = self.entry_comodo.get().strip()
        peca = self.entry_peca.get().strip()
        m1 = self.entry_medida1.get().strip()
        m2 = self.entry_medida2.get().strip()

        try:
            qtd = int(self.entry_quantidade.get())
        except:
            return messagebox.showerror("Erro", "Quantidade inválida!")

        payload = {
            "comodo": comodo,
            "peca": peca,
            "medida1": m1,
            "medida2": m2,
            "quantidade": qtd,
        }

        requests.put(f"http://127.0.0.1:8000/edit/{self.editing_id}", json=payload)
        self.editing_id = None

        self.limpar_inputs()
        self.sync_with_server()

        messagebox.showinfo("OK", "Etiqueta editada com sucesso!")

    # -----------------------
    def excluir(self):
        sel = self.lista.curselection()
        if not sel:
            return messagebox.showwarning("Aviso", "Selecione um item para excluir.")

        idx = sel[0]
        item_id = self.dados[idx]["id"]

        requests.delete(f"http://127.0.0.1:8000/delete/{item_id}")
        self.sync_with_server()

    def limpar_inputs(self):
        self.entry_comodo.delete(0, tk.END)
        self.entry_peca.delete(0, tk.END)
        self.entry_medida1.delete(0, tk.END)
        self.entry_medida2.delete(0, tk.END)
        self.entry_quantidade.delete(0, tk.END)
        self.lista.selection_clear(0, tk.END)

    # -----------------------
    def sync_with_server(self):
        try:
            data = requests.get("http://127.0.0.1:8000/labels").json()

            # salva ID selecionado antes de atualizar
            sel = self.lista.curselection()
            selected_id = None
            if sel:
                selected_id = self.dados[sel[0]]["id"]

            # transforma dados
            self.dados = [
                {
                    "id": item["id"],
                    "comodo": item["comodo"],
                    "peca": item["peca"],
                    "medida": f"{item['medida1']} x {item['medida2']}",
                    "quantidade": int(item["quantidade"]),
                }
                for item in data
            ]

            # recria lista
            self.lista.delete(0, tk.END)
            for item in self.dados:
                self.lista.insert(
                    tk.END,
                    f"[{item['id']}] {item['comodo']} | {item['peca']} | {item['medida']} | x{item['quantidade']}"
                )

            # restaura seleção
            if selected_id is not None:
                for i, item in enumerate(self.dados):
                    if item["id"] == selected_id:
                        self.lista.selection_set(i)
                        break

            self.draw_grid()

        except Exception as e:
            print("Sync error:", e)

        self.root.after(1000, self.sync_with_server)


    # -----------------------
    def next_page(self):
        total_labels = sum(i["quantidade"] for i in self.dados)
        total_pages = max(1, ((total_labels - 1) // LABELS_PER_PAGE) + 1)

        if self.current_page < total_pages - 1:
            self.current_page += 1
            self.draw_grid()

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.draw_grid()

    # -----------------------
    def limpar(self):
        requests.delete("http://127.0.0.1:8000/clear")
        self.sync_with_server()

    # -----------------------
    def draw_grid(self):
        self.canvas_preview.delete("all")
        w, h = 480, 680

        col_w = (w - 16) / COLS
        row_h = (h - 30) / ROWS

        for i in range(COLS + 1):
            x = 8 + i * col_w
            self.canvas_preview.create_line(x, 15, x, h - 15, fill="#ccc")

        for j in range(ROWS + 1):
            y = 15 + j * row_h
            self.canvas_preview.create_line(8, y, w - 8, y, fill="#ccc")

        labels_flat = []
        for item in self.dados:
            for _ in range(item["quantidade"]):
                labels_flat.append(item)

        start = self.current_page * LABELS_PER_PAGE
        end = start + LABELS_PER_PAGE
        subset = labels_flat[start:end]

        for i, item in enumerate(subset):
            col = i % COLS
            row = i // COLS

            x = 8 + col * col_w + col_w / 2
            y = 15 + row * row_h + row_h / 2

            self.canvas_preview.create_text(x, y - 20, text=item["comodo"], font=("Helvetica", 16, "bold"))
            self.canvas_preview.create_text(x, y, text=item["peca"], font=("Helvetica", 13, "bold"))
            self.canvas_preview.create_text(x, y + 20, text=item["medida"], font=("Helvetica", 16))

        total_pages = max(1, ((len(labels_flat) - 1) // LABELS_PER_PAGE) + 1)
        self.page_label.config(text=f"Página {self.current_page + 1} / {total_pages}")

    # -----------------------
    def gerar_pdf(self):
        if not self.dados:
            return messagebox.showwarning("Aviso", "Nenhuma etiqueta adicionada!")

        font_sizes = {
            "comodo": 16,
            "peca": 13,
            "medida": 16,
        }

        nome = gerar_etiquetas(self.dados, font_sizes)

        messagebox.showinfo("Sucesso", f"PDF gerado:\n{nome}")

        # Tenta abrir usando o método padrão do Windows
        try:
            os.startfile(nome)
            return
        except:
            pass

        # Tenta abrir usando o comando 'start'
        try:
            os.system(f'start "" "{nome}"')
            return
        except:
            pass

        # Último fallback
        messagebox.showerror("Erro", f"O PDF foi gerado, mas não pôde ser aberto:\n{nome}")


# --- Entry point ---
if __name__ == "__main__":
    # Inicia o servidor FastAPI em thread separada
    iniciar_backend()

    # Tempo para o servidor levantar antes da GUI conectar
    import time
    time.sleep(1.2)

    # Inicia a interface
    root = tk.Tk()
    App(root)
    root.mainloop()

