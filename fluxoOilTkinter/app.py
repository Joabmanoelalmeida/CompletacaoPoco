import math
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

class FluxoOilCalculator:
    def __init__(self, ko: float, h: float, pr: float, pw: float, Bo: float, uo: float,
                 re: float, rw: float, L: float, A: float, rd: float, kd: float):
        self.ko = ko
        self.h = h
        self.pr = pr
        self.pw = pw
        self.Bo = Bo
        self.uo = uo
        self.re = re
        self.rw = rw
        self.L = L
        self.A = A
        self.rd = rd
        self.kd = kd

    def calcular_qo(self) -> float:
        denominador = self.uo * self.Bo * math.log(0.472 * self.re / self.rw)
        if denominador == 0:
            raise ValueError("Denominador igual a zero, verifique os valores inseridos.")
        return (0.00708 * self.ko * self.h * (self.pr - self.pw)) / denominador

    def calcular_skin(self) -> float:
        if self.kd == 0:
            raise ValueError("kd não pode ser zero para o cálculo do Skin Factor.")
        return ((self.ko / self.kd) - 1) * math.log(self.rd / self.rw)
    
    def calcular_qo_alternativo(self) -> float:
        S = self.calcular_skin()
        denominador = self.uo * self.Bo * (math.log(0.472 * self.re / self.rw) + S)
        if denominador == 0:
            raise ValueError("Denominador é zero, verifique os valores inseridos.")
        return (0.00708 * self.ko * self.h * (self.pr - self.pw)) / denominador

    def calcular_deltaP(self) -> float:
        qo = self.calcular_qo()        
        denominador = 0.00127 * self.A * self.ko
        if denominador == 0:
            raise ValueError("Denominador é zero, verifique os valores inseridos.")
        return (qo * self.Bo * self.uo * self.L) / denominador

    def calcular_eficiencia(self) -> float:
        ln_part = math.log(0.472 * self.re / self.rw)
        S = self.calcular_skin()
        if ln_part + S == 0:
            raise ValueError("Divisor igual a zero, verifique os valores inseridos.")
        return ln_part / (ln_part + S)

# Lista global para armazenar resultados dos poços
poços = []

def adicionar_poco():
    try:
        nome = entry_nome.get()
        ko = float(entry_ko.get())
        h = float(entry_h.get())
        pr = float(entry_pr.get())
        pw = float(entry_pw.get())
        uo = float(entry_uo.get())
        Bo = float(entry_Bo.get())
        re = float(entry_re.get())
        rw = float(entry_rw.get())
        L = float(entry_L.get())
        A = float(entry_A.get())
        rd = float(entry_rd.get())
        kd = float(entry_k.get())

        calculadora = FluxoOilCalculator(ko, h, pr, pw, Bo, uo, re, rw, L, A, rd, kd)
        resultado = calculadora.calcular_qo()
        skin_result = calculadora.calcular_skin()
        resultado_S = calculadora.calcular_qo_alternativo()
        delta_p = calculadora.calcular_deltaP()
        poços.append({
            "nome": nome,
            "fluxo": resultado,
            "skin": skin_result,
            "fluxo_S": resultado_S,
            "deltaP": delta_p,
            "ko": ko,
            "h": h,
            "pr": pr,
            "pw": pw,
            "uo": uo,
            "Bo (Fator de volume de formação)": Bo,
            "re": re,
            "rw": rw,
            "L": L,
            "A": A,
            "rd": rd,
            "k": kd
        })
        label_result.config(text=f"Poço '{nome}': Fluxo = {resultado:.4f} | Fluxo usando S = {resultado_S:.4f} | Skin = {skin_result:.4f} | Queda de pressão = {delta_p:.4f}")
        limpar_entradas()
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao calcular o fluxo drenado do poço: {e}")

def exibir_ranking():
    if not poços:
        messagebox.showinfo("Ranking", "Nenhum poço foi adicionado.")
        return
    ranking = sorted(poços, key=lambda p: p["fluxo"], reverse=True)
    texto = "Ranking dos poços (maior fluxo primeiro):\n"
    for idx, poco in enumerate(ranking, start=1):
        texto += (f"{idx}º: Poço '{poco['nome']}' - Fluxo = {poco['fluxo']:.4f} | "
                  f"Fluxo usando S = {poco['fluxo_S']:.4f} | Skin = {poco['skin']:.4f} | "
                  f"Queda de pressão = {poco['deltaP']:.4f}\n")
    messagebox.showinfo("Ranking", texto)

def limpar_entradas():
    entry_nome.delete(0, tk.END)
    for entrada in entries:
        entrada.delete(0, tk.END)

app = tk.Tk()
app.title("Calculadora para completação de poços de petróleo")
app.state("zoomed")

# Cabeçalho moderno com títulos, autor e professor
style = ttk.Style(app)
style.configure("Header.TFrame", background="#f0f4f8")
style.configure("Header.TLabel", background="#f0f4f8", foreground="#264653")

header_frame = ttk.Frame(app, padding="3", style="Header.TFrame")
header_frame.pack(side="top", fill="x", pady=(2, 4))

lbl_title1 = ttk.Label(
    header_frame,
    text="Plano de Desenvolvimento de um Campo de Petróleo",
    font=("Segoe UI", 18, "bold"),
    foreground="#000000",
    anchor="center",
    style="Header.TLabel"
)
lbl_title1.pack(pady=(0, 1))

lbl_title2 = ttk.Label(
    header_frame,
    text="Calculadora para fase de completação de poços",
    font=("Segoe UI", 14),
    foreground="#000000",
    anchor="center",
    style="Header.TLabel"
)
lbl_title2.pack(pady=(0, 1))

label_autor = ttk.Label(
    header_frame,
    text="Aluno: Joab Manoel Almeida Santos (UFAL) (LCCV) | Professor: Dr. João Paulo",
    font=("Segoe UI", 10),
    foreground="#e76f51",
    anchor="center",
    style="Header.TLabel"
)
label_autor.pack(pady=(0, 1))

# Notebook para as abas
notebook = ttk.Notebook(app)
notebook.pack(expand=True, fill="both")

# Aba de Eficiência de Fluxo e Queda de pressão
tab_efficiencia = ttk.Frame(notebook, padding="20")
notebook.add(tab_efficiencia, text="Eficiência de Fluxo e Queda de pressão")

# Aba de Índice de Produtividade e Injetividade
tab_prod_inj = ttk.Frame(notebook, padding="20")
notebook.add(tab_prod_inj, text="Índice de Produtividade e Injetividade")

# Aplicando tema moderno usando ttk nos widgets dentro da aba
style = ttk.Style(app)
style.theme_use('clam')
style.configure('TLabel', font=("Segoe UI", 10))
style.configure('TEntry', padding=5)
style.configure('TButton', font=("Segoe UI", 10, "bold"), padding=5)

# Mainframe que contém os campos e o ranking, agora dentro da aba
mainframe = tab_efficiencia
mainframe.columnconfigure(0, weight=1)
mainframe.columnconfigure(1, weight=1)

lbl_info = ttk.Label(mainframe, text="Informe os valores:")
lbl_info.grid(row=0, column=0, columnspan=2, pady=(10, 10), sticky="w")

# Campo para o nome do poço
label_nome = ttk.Label(mainframe, text="Nome do poço:")
label_nome.grid(row=1, column=0, padx=10, pady=5, sticky="w")
entry_nome = ttk.Entry(mainframe)
entry_nome.grid(row=1, column=1, padx=10, pady=5, sticky="w")

labels_text = [
    "ko (Fator de permeabilidade do óleo):",
    "h (Altura):",
    "pr (pressão média do reservatório):",
    "pw (pressão de fluxo do poço):",
    "uo (Viscosidade do óleo):",
    "Bo (Fator de volume de formação):",
    "re (Área de drenagem efetiva do poço):",
    "rw (Raio do poço):",
    "L (Comprimento da secção):",
    "A (Área em corte transversal):",
    "rd (adicionando ft):",
    "kd (Permeabilidade da zona danificada até uma distância rd):"
]
entries = []
for i, text in enumerate(labels_text):
    label = ttk.Label(mainframe, text=text)
    label.grid(row=i+2, column=0, padx=10, pady=5, sticky="w")
    entry = ttk.Entry(mainframe)
    entry.grid(row=i+2, column=1, padx=10, pady=5, sticky="w")
    entries.append(entry)

(entry_ko, entry_h, entry_pr, entry_pw, entry_uo,
 entry_Bo, entry_re, entry_rw, entry_L, entry_A,
 entry_rd, entry_k) = entries

tooltip = None
def show_tooltip(event, text):
    global tooltip
    if tooltip:
        return
    tooltip = tk.Toplevel()
    tooltip.wm_overrideredirect(True)
    x = event.x_root + 10
    y = event.y_root + 10
    tooltip.wm_geometry(f"+{x}+{y}")
    label_tip = tk.Label(tooltip, text=text, background="yellow", relief="solid", borderwidth=1)
    label_tip.pack()

def hide_tooltip(event):
    global tooltip
    if tooltip:
        tooltip.destroy()
        tooltip = None

entry_ko.bind("<Enter>", lambda e: show_tooltip(e, "md"))
entry_ko.bind("<Leave>", hide_tooltip)

entry_h.bind("<Enter>", lambda e: show_tooltip(e, "ft"))
entry_h.bind("<Leave>", hide_tooltip)

entry_uo.bind("<Enter>", lambda e: show_tooltip(e, "cp"))
entry_uo.bind("<Leave>", hide_tooltip)

entry_pw.bind("<Enter>", lambda e: show_tooltip(e, "psi"))
entry_pw.bind("<Leave>", hide_tooltip)

entry_pr.bind("<Enter>", lambda e: show_tooltip(e, "psi"))
entry_pr.bind("<Leave>", hide_tooltip)

entry_re.bind("<Enter>", lambda e: show_tooltip(e, "ft"))
entry_re.bind("<Leave>", hide_tooltip)

entry_rw.bind("<Enter>", lambda e: show_tooltip(e, "ft"))
entry_rw.bind("<Leave>", hide_tooltip)

entry_Bo.bind("<Enter>", lambda e: show_tooltip(e, "SSP"))
entry_Bo.bind("<Leave>", hide_tooltip)

entry_L.bind("<Enter>", lambda e: show_tooltip(e, "ft"))
entry_L.bind("<Leave>", hide_tooltip)

entry_A.bind("<Enter>", lambda e: show_tooltip(e, "ft²"))
entry_A.bind("<Leave>", hide_tooltip)

entry_rd.bind("<Enter>", lambda e: show_tooltip(e, "ft"))
entry_rd.bind("<Leave>", hide_tooltip)

entry_k.bind("<Enter>", lambda e: show_tooltip(e, "md"))
entry_k.bind("<Leave>", hide_tooltip)

btn_adicionar = ttk.Button(mainframe, text="Adicionar resultado do Poço", command=adicionar_poco)
btn_adicionar.grid(row=len(labels_text)+2, column=0, columnspan=2, pady=5)

btn_ranking = ttk.Button(mainframe, text="Exibir Ranking", command=lambda: atualizar_ranking())
btn_ranking.grid(row=len(labels_text)+3, column=0, columnspan=2, pady=5)

label_result = ttk.Label(mainframe, text="", font=("Segoe UI", 10, "bold"))
label_result.grid(row=len(labels_text)+4, column=0, columnspan=2, pady=(5, 10), sticky="w")

# Frame para exibir o ranking dentro da aba
ranking_frame = ttk.Frame(mainframe, padding="20", relief="sunken")
ranking_frame.grid(row=0, column=2, rowspan=10, padx=20, pady=5, sticky="nw")

ranking_title = ttk.Label(ranking_frame, text="Ranking dos Poços", font=("Segoe UI", 12, "bold"))
ranking_title.grid(row=0, column=0, columnspan=3, pady=(0,10), sticky="w")

ranking_tree = ttk.Treeview(
    ranking_frame,
    columns=("pos", "nome", "fluxo", "skin", "fluxo_S", "deltaP", "Eficiência(FE)"),
    show="headings",
    height=10
)
ranking_tree.heading("pos", text="Posição", anchor="w")
ranking_tree.heading("nome", text="Nome do Poço", anchor="w")
ranking_tree.heading("fluxo", text="Fluxo", anchor="w")
ranking_tree.heading("skin", text="Skin factor(S)", anchor="w")
ranking_tree.heading("fluxo_S", text="Fluxo usando (S)", anchor="w")
ranking_tree.heading("deltaP", text="Queda de pressão(deltaP)", anchor="w")
ranking_tree.heading("Eficiência(FE)", text="Eficiência (FE)", anchor="w")
ranking_tree.column("pos", width=60, anchor="w")
ranking_tree.column("nome", width=150, anchor="w")
ranking_tree.column("fluxo", width=100, anchor="w")
ranking_tree.column("skin", width=100, anchor="w")
ranking_tree.column("fluxo_S", width=100, anchor="w")
ranking_tree.column("deltaP", width=150, anchor="w")
ranking_tree.column("Eficiência(FE)", width=100, anchor="w")
ranking_tree.grid(row=1, column=0, columnspan=2, sticky="w")

scrollbar = ttk.Scrollbar(ranking_frame, orient="vertical", command=ranking_tree.yview)
ranking_tree.configure(yscroll=scrollbar.set)
scrollbar.grid(row=1, column=2, sticky="ns")

def atualizar_ranking():
    for item in ranking_tree.get_children():
        ranking_tree.delete(item)
    if not poços:
        ranking_tree.insert("", "end", values=("", "Nenhum poço adicionado", "", "", "", "", ""))
        return
    ranking = sorted(poços, key=lambda p: p["fluxo"], reverse=True)
    for idx, poco in enumerate(ranking, start=1):
        ranking_tree.insert(
            "",
            "end",
            values=(
                idx,
                poco["nome"],
                f"{poco['fluxo']:.4f}",
                f"{poco['skin']:.4f}",
                f"{poco['fluxo_S']:.4f}",
                f"{poco['deltaP']:.4f}",
                poco.get("Eficiência(FE)", "")
            )
        )

def limpar_ranking():
    poços.clear()
    atualizar_ranking()

btn_limpar = ttk.Button(ranking_frame, text="Limpar Ranking", command=limpar_ranking)
btn_limpar.grid(row=2, column=0, columnspan=3, pady=5, sticky="w")

def apagar_poco():
    selected = ranking_tree.selection()
    if not selected:
        messagebox.showinfo("Apagar Poço", "Selecione um poço para apagar.")
        return
    for item in selected:
        values = ranking_tree.item(item)["values"]
        nome_poco = values[1]
        global poços
        poços = [p for p in poços if p["nome"] != nome_poco]
    atualizar_ranking()

btn_apagar = ttk.Button(ranking_frame, text="Apagar Poço", command=apagar_poco)
btn_apagar.grid(row=3, column=0, columnspan=3, pady=5, sticky="w")

app.mainloop()
