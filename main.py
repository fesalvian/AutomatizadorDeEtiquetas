import tkinter as tk
from tkinter import ttk, messagebox
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
import os

# ---- Configuração da folha ----
PAGE_WIDTH, PAGE_HEIGHT = A4
COLS = 3
ROWS = 6
LABELS_PER_PAGE = COLS * ROWS

# ---- Margens exatas ----
MARGIN_LEFT = 6 * mm
MARGIN_RIGHT = 6 * mm
MARGIN_TOP = 10 * mm
MARGIN_BOTTOM = 10 * mm

# Área útil
CONTENT_WIDTH = PAGE_WIDTH - (MARGIN_LEFT + MARGIN_RIGHT)
CONTENT_HEIGHT = PAGE_HEIGHT - (MARGIN_TOP + MARGIN_BOTTOM)
LABEL_WIDTH = CONTENT_WIDTH / COLS
LABEL_HEIGHT = CONTENT_HEIGHT / ROWS

# ---- Geração automática de nome sequencial ----
def next_filename(base="etiquetas", ext=".pdf"):
    i = 1
    while True:
        name = f"{base}{i:03d}{ext}"
        if not os.path.exists(name):
            return name
        i += 1


# ---- Função de desenho calibrada ----
def draw_label(c, x, y, comodo, peca, medida, font_sizes):
    c.saveState()

    comodo_size = font_sizes["comodo"]
    peca_size = font_sizes["peca"]
    medida_size = font_sizes["medida"]

    center_y = y + LABEL_HEIGHT / 2
    center_x = x + LABEL_WIDTH / 2

    # Cômodo (maior e negrito)
    c.setFont("Helvetica-Bold", comodo_size)
    c.drawCentredString(center_x, center_y + 15, comodo)

    # Peça (média e negrito)
    c.setFont("Helvetica-Bold", peca_size)
    c.drawCentredString(center_x, center_y - 5, peca)

    # Medida (normal)
    c.setFont("Helvetica", medida_size)
    c.drawCentredString(center_x, center_y - 25, medida)

    c.restoreState()


# ---- Geração do PDF calibrada ----
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
    return nome_arquivo


# ---- Interface Tkinter ----
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Automatizador de Etiquetas")
        self.root.geometry("1080x740")
        self.root.minsize(1000, 700)

        # ---- Tema visual moderno ----
        style = ttk.Style()
        style.theme_use("clam")

        BG_MAIN = "#f8fafc"
        BG_FRAME = "#ffffff"
        PRIMARY = "#2563eb"  # Azul moderno
        ACCENT = "#1e40af"
        TEXT = "#1e293b"

        self.root.configure(bg=BG_MAIN)
        style.configure("TFrame", background=BG_MAIN)
        style.configure("Card.TFrame", background=BG_FRAME, relief="flat")
        style.configure("TLabel", background=BG_MAIN, foreground=TEXT, font=("Segoe UI", 10))
        style.configure("Title.TLabel", background=BG_MAIN, foreground=PRIMARY, font=("Segoe UI Semibold", 13))
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=(8, 6), background=PRIMARY, foreground="white")
        style.map("TButton", background=[("active", ACCENT)], foreground=[("active", "white")])
        style.configure("TEntry", fieldbackground="white", relief="flat", font=("Segoe UI", 10))

        # ---- Estrutura base ----
        self.dados = []
        self.current_page = 0

        main_frame = ttk.Frame(root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # ----- Lado esquerdo -----
        left = ttk.Frame(main_frame, style="Card.TFrame", padding=15)
        left.pack(side="left", fill="y", padx=(0, 20))

        ttk.Label(left, text="Automatizador de Etiquetas", style="Title.TLabel").pack(pady=(0, 15))

        ttk.Label(left, text="Cômodo:").pack(anchor="w")
        self.entry_comodo = ttk.Entry(left, width=40)
        self.entry_comodo.pack(pady=(0, 8))

        ttk.Label(left, text="Peça:").pack(anchor="w")
        self.entry_peca = ttk.Entry(left, width=40)
        self.entry_peca.pack(pady=(0, 8))

        ttk.Label(left, text="Medida (8 dígitos → 0000x0000):").pack(anchor="w")
        self.entry_medida = ttk.Entry(left, width=40)
        self.entry_medida.pack(pady=(0, 8))
        self.entry_medida.bind("<KeyRelease>", self.formatar_medida)

        ttk.Label(left, text="Quantidade:").pack(anchor="w")
        self.entry_quantidade = ttk.Entry(left, width=20)
        self.entry_quantidade.pack(pady=(0, 10))

        ttk.Separator(left, orient="horizontal").pack(fill="x", pady=8)

        # ---- Fonte configurável ----
        ttk.Label(left, text="Tamanho da Fonte:", style="Title.TLabel").pack(pady=(5, 5), anchor="w")
        self.font_comodo = tk.IntVar(value=16)
        self.font_peca = tk.IntVar(value=13)
        self.font_medida = tk.IntVar(value=16)

        ttk.Label(left, text="Cômodo:").pack(anchor="w")
        ttk.Spinbox(left, from_=8, to=30, textvariable=self.font_comodo, width=5).pack(anchor="w")
        ttk.Label(left, text="Peça:").pack(anchor="w")
        ttk.Spinbox(left, from_=8, to=30, textvariable=self.font_peca, width=5).pack(anchor="w")
        ttk.Label(left, text="Medida:").pack(anchor="w")
        ttk.Spinbox(left, from_=8, to=30, textvariable=self.font_medida, width=5).pack(anchor="w")

        ttk.Separator(left, orient="horizontal").pack(fill="x", pady=10)

        # ---- Botões ----
        ttk.Button(left, text="➕ Adicionar Etiqueta", command=self.adicionar).pack(pady=5, fill="x")
        ttk.Button(left, text="❌ Excluir Selecionado", command=self.excluir).pack(pady=5, fill="x")
        ttk.Button(left, text="🖨️ Gerar PDF", command=self.gerar_pdf).pack(pady=5, fill="x")
        ttk.Button(left, text="🗑️ Limpar Tudo", command=self.limpar).pack(pady=5, fill="x")

        ttk.Label(left, text="Lista de etiquetas:").pack(pady=(15, 5), anchor="w")
        self.lista = tk.Listbox(left, width=55, height=15, relief="flat", font=("Segoe UI", 9))
        self.lista.pack(pady=(0, 10))
        self.lista.config(selectbackground=PRIMARY, selectforeground="white", bg="white", borderwidth=1)

        # ---- Enter para adicionar ----
        self.entry_quantidade.bind("<Return>", lambda e: self.adicionar())

        # ---- Lado direito (preview + navegação) ----
        right = ttk.Frame(main_frame, style="Card.TFrame", padding=15)
        right.pack(side="right", fill="both", expand=True)

        ttk.Label(right, text="Preview da Folha A4 (3x6)", style="Title.TLabel").pack()
        self.canvas_preview = tk.Canvas(
            right, width=500, height=680, bg="white", highlightthickness=1, highlightbackground="#ccc"
        )
        self.canvas_preview.pack(pady=15)

        nav_frame = ttk.Frame(right)
        nav_frame.pack(pady=5)
        ttk.Button(nav_frame, text="⬅️ Página anterior", command=self.prev_page).pack(side="left", padx=10)
        ttk.Button(nav_frame, text="➡️ Próxima página", command=self.next_page).pack(side="left", padx=10)
        self.page_label = ttk.Label(nav_frame, text="Página 1")
        self.page_label.pack(side="left", padx=10)

        self.draw_grid()

    # ---- Formata o campo medida ----
    def formatar_medida(self, event=None):
        texto = self.entry_medida.get().replace("x", "").replace(" ", "")
        if len(texto) >= 8:
            medida = f"{texto[:4]} x {texto[4:8]}"
            self.entry_medida.delete(0, tk.END)
            self.entry_medida.insert(0, medida)

    # ---- Desenhar preview ----
    def draw_grid(self):
        self.canvas_preview.delete("all")
        w, h = 480, 680
        col_w = w / COLS
        row_h = h / ROWS
        margin_top, margin_bottom, margin_side = 15, 15, 8

        usable_height = h - margin_top - margin_bottom
        usable_width = w - (2 * margin_side)
        col_w = usable_width / COLS
        row_h = usable_height / ROWS

        for i in range(COLS + 1):
            x = margin_side + i * col_w
            self.canvas_preview.create_line(x, margin_top, x, h - margin_bottom, fill="#ccc")

        for j in range(ROWS + 1):
            y = margin_top + j * row_h
            self.canvas_preview.create_line(margin_side, y, w - margin_side, y, fill="#ccc")

        start = self.current_page * LABELS_PER_PAGE
        end = start + LABELS_PER_PAGE
        etiquetas_pagina = []
        for item in self.dados:
            for _ in range(item["quantidade"]):
                etiquetas_pagina.append(item)

        subset = etiquetas_pagina[start:end]
        i = 0
        for item in subset:
            col = i % COLS
            row = (i // COLS) % ROWS
            x = margin_side + col * col_w + col_w / 2
            y = margin_top + row * row_h + row_h / 2
            self.canvas_preview.create_text(x, y - 20, text=item["comodo"], font=("Helvetica", self.font_comodo.get(), "bold"))
            self.canvas_preview.create_text(x, y, text=item["peca"], font=("Helvetica", self.font_peca.get(), "bold"))
            self.canvas_preview.create_text(x, y + 20, text=item["medida"], font=("Helvetica", self.font_medida.get()))
            i += 1

        total_pages = max(1, ((len(etiquetas_pagina) - 1) // LABELS_PER_PAGE) + 1)
        self.page_label.config(text=f"Página {self.current_page + 1} / {total_pages}")

    # ---- Adicionar ----
    def adicionar(self):
        comodo = self.entry_comodo.get().strip()
        peca = self.entry_peca.get().strip()
        medida = self.entry_medida.get().strip()
        try:
            quantidade = int(self.entry_quantidade.get())
        except ValueError:
            messagebox.showerror("Erro", "Quantidade inválida!")
            return
        if not comodo or not peca or not medida:
            messagebox.showwarning("Atenção", "Preencha todos os campos!")
            return
        item = {"comodo": comodo, "peca": peca, "medida": medida, "quantidade": quantidade}
        self.dados.append(item)
        self.lista.insert(tk.END, f"{comodo} | {peca} | {medida} | x{quantidade}")
        self.draw_grid()

        self.entry_comodo.delete(0, tk.END)
        self.entry_peca.delete(0, tk.END)
        self.entry_medida.delete(0, tk.END)
        self.entry_quantidade.delete(0, tk.END)
        self.entry_comodo.focus()

    # ---- Excluir item selecionado ----
    def excluir(self):
        sel = self.lista.curselection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um item para excluir.")
            return
        idx = sel[0]
        del self.dados[idx]
        self.lista.delete(idx)
        self.draw_grid()

    # ---- Paginação ----
    def next_page(self):
        total_labels = sum(item["quantidade"] for item in self.dados)
        total_pages = max(1, ((total_labels - 1) // LABELS_PER_PAGE) + 1)
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self.draw_grid()

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.draw_grid()

    # ---- Limpar tudo ----
    def limpar(self):
        self.dados.clear()
        self.lista.delete(0, tk.END)
        self.current_page = 0
        self.draw_grid()

    # ---- Gerar PDF ----
    def gerar_pdf(self):
        if not self.dados:
            messagebox.showwarning("Aviso", "Nenhuma etiqueta adicionada!")
            return

        font_sizes = {
            "comodo": self.font_comodo.get(),
            "peca": self.font_peca.get(),
            "medida": self.font_medida.get(),
        }

        nome = gerar_etiquetas(self.dados, font_sizes)
        messagebox.showinfo("Sucesso", f"PDF gerado com sucesso:\n{nome}")


# ---- Rodar App ----
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
