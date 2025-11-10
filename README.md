# 🏷️ Automatizador de Etiquetas

Um app simples e elegante feito em **Python** com **Tkinter** e **ReportLab**, criado para gerar folhas A4 com etiquetas personalizadas em PDF.  
Ideal para marcadores de móveis, peças, ou qualquer tipo de identificação rápida e precisa.

---

## 🚀 Funcionalidades

✅ Interface gráfica moderna e intuitiva  
✅ Geração automática de etiquetas no formato **3x6 por folha (18 por página)**  
✅ Margens calibradas com precisão para papel A4  
✅ Visualização em tempo real das etiquetas antes de gerar o PDF  
✅ Controle de fonte individual (Cômodo, Peça e Medida)  
✅ Paginação automática e nomes de arquivo sequenciais (`etiquetas001.pdf`, `etiquetas002.pdf`, …)  
✅ Atalho com tecla **Enter** para adicionar etiquetas rapidamente  

---

## 🧩 Tecnologias usadas

- **Python 3.10+**
- **Tkinter** — Interface gráfica  
- **ReportLab** — Geração de PDFs  
- **ttk.Style** — Estilização moderna dos componentes  

---

## ⚙️ Instalação

1. **Clone o repositório:**


git clone git@github.com:fesalvian/AutomatizadorDeEtiquetas.git
cd AutomatizadorDeEtiquetas
Crie e ative o ambiente virtual (recomendado):



python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
Instale as dependências:



pip install reportlab
O Tkinter já vem instalado por padrão com o Python.

🧠 Como usar
Execute o programa:



python main.py
Preencha os campos:

Cômodo: nome do local (ex: Sala, Cozinha, Quarto)

Peça: descrição do item (ex: Porta, Gaveta, Tampo)

Medida: formato 0000x0000 (ex: 0450x0800)

Quantidade: número de etiquetas iguais

Clique em ➕ Adicionar Etiqueta

Ou pressione Enter no campo “Quantidade” para adicionar automaticamente.

Visualize o preview da folha A4 no lado direito.

Gere o PDF clicando em 🖨️ Gerar PDF

O arquivo será salvo na pasta do projeto, com nome automático (etiquetas001.pdf, etiquetas002.pdf, etc.)

📐 Especificações técnicas
Layout: 3 colunas × 6 linhas (18 etiquetas por folha)

Margens calibradas para impressão real:

Topo: 10 mm

Base: 10 mm

Laterais: 6 mm

Centralização: Cada etiqueta é centralizada automaticamente no espaço da célula

Fontes: Personalizáveis diretamente na interface

💅 Personalização
Quer mudar o tema, cores ou fonte?

Abra o arquivo main.py e edite estas variáveis no início da interface:

python

PRIMARY = "#2563eb"  # Cor principal
ACCENT = "#1e40af"   # Cor de destaque
BG_MAIN = "#f8fafc"  # Fundo principal
TEXT = "#1e293b"     # Cor do texto
Você pode trocar por qualquer cor HEX, ou até usar um esquema dark.

🖨️ Dicas de impressão
Use folhas de etiquetas padrão A4 (3 colunas x 6 linhas).

Certifique-se de desativar redimensionamento automático na janela de impressão (escala 100%).

Caso o PDF fique um pouco deslocado, ajuste as margens diretamente no código:

python

MARGIN_TOP = 10 * mm
MARGIN_BOTTOM = 10 * mm
MARGIN_LEFT = 6 * mm
MARGIN_RIGHT = 6 * mm

👨‍💻 Autor
Felipe Salviano
Desenvolvedor de Software • Projeto para MASO Móveis Planejados
💼 GitHub @fesalvian