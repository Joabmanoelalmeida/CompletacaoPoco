import math
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class FluxoOilCalculator:
    def __init__(
        self,
        ko: float, h: float, pr: float, pw: float, Bo: float, uo: float,
        re: float, rw: float, L: float, A: float, rd: float, kd: float,
        q1: float = 0.0, psat: float = 0.0
    ):
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
        self.q1 = q1
        self.psat = psat

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

    def calcular_ip(self, Pe: float, pwf: float) -> float:
        if pwf - Pe == 0:
            raise ValueError("Divisor é zero, verifique os valores de Pe e pwf.")
        return self.q1 / (Pe - pwf)

    def calcular_ii(self, Pe: float, pwf: float) -> float:
        if pwf - Pe == 0:
            raise ValueError("Divisor é zero, verifique os valores de Pe e pwf.")
        return self.q1 / (pwf - Pe)
    
    def calcular_qsat(self, Pe: float, pwf1: float) -> float:
        ip_value = self.calcular_ip(Pe, pwf1)
        return ip_value * (Pe - self.psat)

    def calcular_qc(self, Pe: float, pwf1: float) -> float:
        qsat = self.calcular_qsat(Pe, pwf1)
        denominator = 1.8 * (Pe - self.psat)
        if denominator == 0:
            raise ValueError("Denominador é zero, verifique os valores de Pe e psat.")
        return (qsat * self.psat) / denominator
    
    def calcular_qmax(self, Pe: float, pwf1: float) -> float:
        qc = self.calcular_qc(Pe, pwf1)
        qsat = self.calcular_qsat(Pe, pwf1)
        return qc + qsat
    
    def criar_curva(self, Pe: float, Psat: float, Pwfx_values: list) -> list:
        curva = []
        qc = self.calcular_qc(Pe, self.pw)
        for Pwfx in Pwfx_values:
            f = qc * (1.8 * (Pe / Psat) - 0.8 - 0.2 * (Pwfx / Psat) - 0.8 * (Pwfx / Psat) ** 2)
            curva.append((Pwfx, f))
        return curva
    
    
# Lista global para armazenar resultados dos poços (aba Eficiência)
poços = []
# Lista global para armazenar resultados do IP e II (aba Produtividade/Injetabilidade)
i_pocos = []

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

        # Instancia com valores padrão para q1 e psat
        calculadora = FluxoOilCalculator(ko, h, pr, pw, Bo, uo, re, rw, L, A, rd, kd)
        resultado = calculadora.calcular_qo()
        skin_result = calculadora.calcular_skin()
        resultado_S = calculadora.calcular_qo_alternativo()
        delta_p = calculadora.calcular_deltaP()
        eficiencia = calculadora.calcular_eficiencia()
        poços.append({
            "nome": nome,
            "fluxo": resultado,
            "skin": skin_result,
            "fluxo_S": resultado_S,
            "deltaP": delta_p,
            "Eficiência(FE)": eficiencia,
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
        label_result.config(text=f"Poço '{nome}': Fluxo = {resultado:.4f} | Fluxo usando S = {resultado_S:.4f} | Skin = {skin_result:.4f} | Queda de pressão = {delta_p:.4f} | Eficiência = {eficiencia:.4f}")
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
                  f"Queda de pressão = {poco['deltaP']:.4f} | Eficiência = {poco.get('Eficiência(FE)', 0):.4f}\n")
    messagebox.showinfo("Ranking", texto)

def limpar_entradas():
    entry_nome.delete(0, tk.END)
    for entrada in entries:
        entrada.delete(0, tk.END)

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
                f"{poco.get('Eficiência(FE)', 0):.4f}"
            )
        )

def limpar_ranking():
    poços.clear()
    atualizar_ranking()

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

# Funções para a aba Produtividade/Injetabilidade (IP e II)
def adicionar_poco_ip():
    try:
        nome = entry_nome_ip.get()
        # Recebe os valores inseridos na aba de Produtividade/Injetabilidade
        q1 = float(entry_q1_prod.get())
        Pe = float(entry_Pe.get())
        pwf = float(entry_pwf.get())
        psat = float(entry_Psat.get())
        if pwf - Pe == 0:
            raise ValueError("Divisor é zero. Verifique os valores de Pe e pwf.")
        # Usa os parâmetros fornecidos nesta aba para o cálculo de IP e II
        # Os demais parâmetros não são utilizados nos métodos calcular_ip e calcular_ii
        calculadora = FluxoOilCalculator(
            ko=0, h=0, pr=0, pw=0, Bo=0, uo=0,
            re=0, rw=0, L=0, A=0, rd=0, kd=1,
            q1=q1, psat=psat
        )
        ip = calculadora.calcular_ip(Pe, pwf)
        ii = calculadora.calcular_ii(Pe, pwf)
        i_pocos.append({"nome": nome, "ip": ip, "ii": ii, "pwf": pwf})
        label_ip_result.config(text=f"IP = {ip:.4f} | II = {ii:.4f} | pwf = {pwf:.4f}")
        atualizar_ranking_ip()
        limpar_campos_ip()
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao calcular o IP/II: {e}")

def atualizar_ranking_ip():
    for item in ranking_tree_ip.get_children():
        ranking_tree_ip.delete(item)
    if not i_pocos:
        ranking_tree_ip.insert("", "end", values=("", "Nenhum poço adicionado", "", ""))
        return
    ranking = sorted(i_pocos, key=lambda p: p["ip"], reverse=True)
    for idx, poco in enumerate(ranking, start=1):
        ranking_tree_ip.insert(
            "",
            "end",
            values=(
                idx,
                poco["nome"],
                f"{poco['ip']:.4f}",
                f"{poco['ii']:.4f}"
            )
        )

def limpar_campos_ip():
    entry_nome_ip.delete(0, tk.END)
    entry_q1_prod.delete(0, tk.END)
    entry_Pe.delete(0, tk.END)
    entry_pwf.delete(0, tk.END)
    entry_Psat.delete(0, tk.END)

def limpar_ranking_ip():
    i_pocos.clear()
    atualizar_ranking_ip()

def apagar_poco_ip():
    selected = ranking_tree_ip.selection()
    if not selected:
        messagebox.showinfo("Apagar Poço", "Selecione um poço para apagar.")
        return
    for item in selected:
        values = ranking_tree_ip.item(item)["values"]
        nome_poco = values[1]
        global i_pocos
        i_pocos = [p for p in i_pocos if p["nome"] != nome_poco]
    atualizar_ranking_ip()

# Global list para armazenar os resultados do canhoneamento para o ranking
ranking_canh = []

def calcular_deltaP_canh(k: float, phasing: float) -> float:
    if phasing == 0:
        return 3000 / (k ** 0.37)
    elif phasing == 180:
        return 3000 / (k ** 0.4)
    else:
        raise ValueError("Phasing deve ser 0 (oil) ou 180 (gas).")

def calcular_hd(h: float, lp: float, kh: float = 1.0, kv: float = 1.0) -> float:
    # Se não fornecidos, assume kh/kv = 1
    return (h / lp) * math.sqrt(kh / kv)

def calcular_rpd(rp: float, h: float, kh: float = 1.0, kv: float = 1.0) -> float:
    # rpd = (rp/(2*h))*(1 + sqrt(kv/kh)). Com kh=kv=1, rpd = rp/h.
    return (rp / (2 * h)) * (1 + math.sqrt(kv / kh))

def calcular_rwD(rw: float, lp: float) -> float:
    return rw / (lp + rw)

def calcular_Sp(rw: float, lp: float, hd: float, rpd: float, phasing: float) -> tuple[float, float, float, float, float, float]:
    # Seleciona os parâmetros de acordo com o phasing
    if phasing == 0:
        C1, C2 = 0.16, 2.675
        a1, a2 = -2.091, 0.0453
        b1, b2 = 5.1313, 1.867
    elif phasing == 180:
        C1, C2 = 0.026, 532
        a1, a2 = -2.0251, 0.0943
        b1, b2 = 3.073, 1.8115
    else:
        raise ValueError("Phasing deve ser 0 (oil) ou 180 (gas).")
    
    rwD = calcular_rwD(rw, lp)
    Sh = math.log(4 * rw / lp)
    Swb = C1 * math.exp(C2 * rwD)
    if rpd <= 0:
        raise ValueError("rpd deve ser maior que zero para calcular log.")
    a = a1 * math.log(rpd) + a2
    b = b1 * rpd + b2
    Sv = (10 ** a) * (hd ** (b - 1)) * (rpd ** b)
    Sp = Sh + Swb + Sv
    return Sp, Sh, Swb, Sv, a, b

def calcular_Sx(rd: float, rw: float, lp: float) -> float:
    ratio = rd / (rw + lp)
    if ratio >= 18:
        return 0.0
    elif ratio >= 2:
        return -0.001
    elif ratio >= 1.5:
        return -0.002
    else:
        return -0.0024

def calcular_Sdp(Sp: float, Sx: float) -> float:
    return Sp + Sx

def processar_canhoneamento():
    try:
        # Capturar os valores dos campos
        k = float(entry_k_canh.get())
        rw = float(entry_rw_canh.get())
        lp = float(entry_lp.get())
        rp = float(entry_rp.get())
        phasing = float(entry_phasing.get())
        h_canh = float(entry_h_canh.get())
        rd = float(entry_rd_canh.get())
        
        # Cálculos utilizando as funções definidas
        deltaP = calcular_deltaP_canh(k, phasing)
        hd = calcular_hd(h_canh, lp)
        rpd = calcular_rpd(rp, h_canh)
        rwD_value = calcular_rwD(rw, lp)
        Sp, Sh, Swb, Sv, a, b = calcular_Sp(rw, lp, hd, rpd, phasing)
        Sx = calcular_Sx(rd, rw, lp)
        Sdp = calcular_Sdp(Sp, Sx)
        
        # Armazenar os resultados no ranking global para canhoneamento
        resultado = {
            "deltaP": deltaP,
            "hd": hd,
            "rpd": rpd,
            "rwD": rwD_value,
            "Sh": Sh,
            "Swb": Swb,
            "Sv": Sv,
            "Sp": Sp,
            "Sx": Sx,
            "Sdp": Sdp,
            "a": a,
            "b": b
        }
        ranking_canh.append(resultado)
        
        # Se não existir um container para o ranking, cria-o
        if not hasattr(processar_canhoneamento, "container"):
            processar_canhoneamento.container = ttk.Frame(tab_canhoneamento, padding="20", relief="sunken")
            processar_canhoneamento.container.grid(row=0, column=2, rowspan=10, padx=20, pady=5, sticky="nw")
            processar_canhoneamento.tree = ttk.Treeview(
                processar_canhoneamento.container, 
                columns=("Pos", "deltaP", "Sp", "Sdp"), 
                show="headings", height=12
            )
            processar_canhoneamento.tree.heading("Pos", text="Posição")
            processar_canhoneamento.tree.heading("deltaP", text="deltaP")
            processar_canhoneamento.tree.heading("Sp", text="Sp")
            processar_canhoneamento.tree.heading("Sdp", text="Sdp")
            processar_canhoneamento.tree.column("Pos", width=60)
            processar_canhoneamento.tree.column("deltaP", width=100)
            processar_canhoneamento.tree.column("Sp", width=100)
            processar_canhoneamento.tree.column("Sdp", width=100)
            processar_canhoneamento.tree.pack(side=tk.RIGHT, expand=True, fill="both", padx=10, pady=10)
        else:
            # Limpar itens anteriores do ranking para atualizar a listagem
            for item in processar_canhoneamento.tree.get_children():
                processar_canhoneamento.tree.delete(item)
        
        # Ordenar os resultados do ranking; aqui utilizamos Sdp para definir a posição
        ranking_ordenado = sorted(ranking_canh, key=lambda x: x["Sdp"], reverse=True)
        for idx, res in enumerate(ranking_ordenado, start=1):
            processar_canhoneamento.tree.insert(
                "", "end",
                values=(
                    idx,
                    f"{res['deltaP']:.4f}",
                    f"{res['Sp']:.4f}",
                    f"{res['Sdp']:.4f}"
                )
            )
        
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao processar canhoneamento: {e}")

# Substituindo a função existente do botão por esta nova implementação:
# The button has already been created with the appropriate command.

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

# Aba de Índice de Produtividade e Injetabilidade
tab_prod_inj = ttk.Frame(notebook, padding="20")
notebook.add(tab_prod_inj, text="Índice de Produtividade e Injetabilidade")

# Aba de Canhoneamento
tab_canhoneamento = ttk.Frame(notebook, padding="20")
notebook.add(tab_canhoneamento, text="Canhoneamento")

# Aplicando tema moderno usando ttk nos widgets
style = ttk.Style(app)
style.theme_use('clam')
style.configure('TLabel', font=("Segoe UI", 10))
style.configure('TEntry', padding=5)
style.configure('TButton', font=("Segoe UI", 10, "bold"), padding=5)

# ------------------- Aba Eficiência de Fluxo e Queda de pressão -------------------
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

# ------------------- Aba Índice de Produtividade e Injetabilidade -------------------
lbl_info_prod = ttk.Label(tab_prod_inj, text="Informe os valores para o Índice de Produtividade:")
lbl_info_prod.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="w")

label_nome_ip = ttk.Label(tab_prod_inj, text="Nome do Poço:")
label_nome_ip.grid(row=1, column=0, padx=10, pady=5, sticky="w")
entry_nome_ip = ttk.Entry(tab_prod_inj)
entry_nome_ip.grid(row=1, column=1, padx=10, pady=5, sticky="w")

label_qo = ttk.Label(tab_prod_inj, text="Fluxo (q1):")
label_qo.grid(row=2, column=0, padx=10, pady=5, sticky="w")
entry_q1_prod = ttk.Entry(tab_prod_inj)
entry_q1_prod.grid(row=2, column=1, padx=10, pady=5, sticky="w")

label_Pe = ttk.Label(tab_prod_inj, text="Pe (psi):")
label_Pe.grid(row=3, column=0, padx=10, pady=5, sticky="w")
entry_Pe = ttk.Entry(tab_prod_inj)
entry_Pe.grid(row=3, column=1, padx=10, pady=5, sticky="w")

label_pwf = ttk.Label(tab_prod_inj, text="pwf (psi):")
label_pwf.grid(row=4, column=0, padx=10, pady=5, sticky="w")
entry_pwf = ttk.Entry(tab_prod_inj)
entry_pwf.grid(row=4, column=1, padx=10, pady=5, sticky="w")

label_Psat = ttk.Label(tab_prod_inj, text="Psat (psi):")
label_Psat.grid(row=5, column=0, padx=10, pady=5, sticky="w")
entry_Psat = ttk.Entry(tab_prod_inj)
entry_Psat.grid(row=5, column=1, padx=10, pady=5, sticky="w")

btn_calcular_ip = ttk.Button(tab_prod_inj, text="Calcular IP/II", command=adicionar_poco_ip)
btn_calcular_ip.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

label_ip_result = ttk.Label(tab_prod_inj, text="", font=("Segoe UI", 10, "bold"))
label_ip_result.grid(row=8, column=0, columnspan=2, padx=10, pady=10, sticky="w")

def representar_curva_ipr():
    try:
        Pe = float(entry_Pe.get())
        pwf = float(entry_pwf.get())
        q1 = float(entry_q1_prod.get())
        if pwf - Pe == 0:
            raise ValueError("Divisor é zero. Verifique os valores de Pe e pwf.")
        # Utiliza a fórmula para II para representar a curva
        calculadora = FluxoOilCalculator(ko=0, h=0, pr=0, pw=0, Bo=0, uo=0, re=0, rw=0, L=0, A=0, rd=0, kd=1, q1=q1, psat=0)
        ii = calculadora.calcular_ii(Pe, pwf)
        pwf_values = [i for i in range(int(pwf), int(Pe) + 1)]
        qo_values = [ii * (Pe - p) for p in pwf_values]
        
        fig, ax = plt.subplots()
        ax.plot(pwf_values, qo_values, label="Curva IPR (usando II)")
        ax.set_xlabel("pwf (psi)")
        ax.set_ylabel("qo (STB/d)")
        ax.set_title("Curva IPR")
        ax.legend()
        
        canvas = FigureCanvasTkAgg(fig, master=tab_prod_inj)
        canvas.draw()
        canvas.get_tk_widget().grid(row=2, column=3, rowspan=8, padx=10, pady=10, sticky="n")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao representar a curva IPR: {e}")

btn_representar_ipr = ttk.Button(tab_prod_inj, text="Representar Curva IPR", command=representar_curva_ipr)
btn_representar_ipr.grid(row=9, column=0, columnspan=2, padx=10, pady=10)

ranking_frame_ip = ttk.Frame(tab_prod_inj, padding="20", relief="sunken")
ranking_frame_ip.grid(row=0, column=2, rowspan=9, padx=20, pady=5, sticky="nw")

ranking_title_ip = ttk.Label(ranking_frame_ip, text="Ranking dos Poços (IP e II)", font=("Segoe UI", 12, "bold"))
ranking_title_ip.grid(row=0, column=0, columnspan=3, pady=(0,10), sticky="w")

ranking_tree_ip = ttk.Treeview(
    ranking_frame_ip,
    columns=("pos", "nome", "ip", "ii"),
    show="headings",
    height=10
)
ranking_tree_ip.heading("pos", text="Posição", anchor="w")
ranking_tree_ip.heading("nome", text="Nome do Poço", anchor="w")
ranking_tree_ip.heading("ip", text="IP", anchor="w")
ranking_tree_ip.heading("ii", text="II", anchor="w")
ranking_tree_ip.column("pos", width=60, anchor="w")
ranking_tree_ip.column("nome", width=150, anchor="w")
ranking_tree_ip.column("ip", width=100, anchor="w")
ranking_tree_ip.column("ii", width=100, anchor="w")
ranking_tree_ip.grid(row=1, column=0, columnspan=2, sticky="w")

scrollbar_ip = ttk.Scrollbar(ranking_frame_ip, orient="vertical", command=ranking_tree_ip.yview)
ranking_tree_ip.configure(yscroll=scrollbar_ip.set)
scrollbar_ip.grid(row=1, column=2, sticky="ns")

btn_limpar_ip = ttk.Button(ranking_frame_ip, text="Limpar Ranking", command=limpar_ranking_ip)
btn_limpar_ip.grid(row=2, column=0, columnspan=3, pady=5, sticky="w")

btn_apagar_ip = ttk.Button(ranking_frame_ip, text="Apagar Poço", command=apagar_poco_ip)
btn_apagar_ip.grid(row=3, column=0, columnspan=3, pady=5, sticky="w")

# ------------------- Aba Canhoneamento -------------------
mainframe_canh = tab_canhoneamento
mainframe_canh.columnconfigure(0, weight=1)
mainframe_canh.columnconfigure(1, weight=1)

# Criação de um frame de entrada e tabela de resultados lado a lado na aba Canhoneamento
frame_esquerda = ttk.Frame(mainframe_canh, padding="10")
frame_esquerda.grid(row=0, column=0, sticky="nw")

lbl_info_canh = ttk.Label(frame_esquerda, text="Informe os valores para Canhoneamento:")
lbl_info_canh.grid(row=0, column=0, columnspan=2, pady=(10, 10), sticky="w")

labels_text_canh = [
    "k (em md):",
    "rw (em in):",
    "lp (em in):",
    "rp (em in):",
    "Phasing (em in):",
    "h (em in):",
    "rc (em in):",
    "rd (em in):"
]
entries_canh = []
for i, text in enumerate(labels_text_canh):
    label = ttk.Label(frame_esquerda, text=text)
    label.grid(row=i+1, column=0, padx=10, pady=5, sticky="w")
    entry = ttk.Entry(frame_esquerda)
    entry.grid(row=i+1, column=1, padx=10, pady=5, sticky="w")
    entries_canh.append(entry)

(entry_k_canh, entry_rw_canh, entry_lp, entry_rp,
 entry_phasing, entry_h_canh, entry_rc, entry_rd_canh) = entries_canh

def processar_canhoneamento():
    try:
        k = float(entry_k_canh.get())
        rw = float(entry_rw_canh.get())
        lp = float(entry_lp.get())
        rp = float(entry_rp.get())
        phasing = float(entry_phasing.get())
        h_canh = float(entry_h_canh.get())
        rc = float(entry_rc.get())
        rd_canh = float(entry_rd_canh.get())
        
        # Cálculo de exemplo para os resultados (substitua pelos cálculos reais)
        deltaP = 3000 / (k ** 0.37) if phasing == 0 else 3000 / (k ** 0.4)
        Sp = 0    # Exemplo; substitua pelo cálculo real
        Sdp = 0   # Exemplo; substitua pelo cálculo real
        
        # Armazena os resultados no ranking global para canhoneamento
        resultado = {
            "deltaP": deltaP,
            "Sp": Sp,
            "Sdp": Sdp
        }
        ranking_canh.append(resultado)
        
        # Atualiza a tabela de resultados
        atualizar_ranking_canh()
        
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao processar canhoneamento: {e}")

btn_processar_canh = ttk.Button(frame_esquerda, text="Processar Canhoneamento", command=processar_canhoneamento)
btn_processar_canh.grid(row=len(labels_text_canh)+1, column=0, columnspan=2, pady=10, sticky="w")

# Criação do frame para a tabela de resultados, reposicionado mais à esquerda (coluna 1 ao invés de 2)
ranking_frame_canh = ttk.Frame(mainframe_canh, padding="20", relief="sunken")
ranking_frame_canh.grid(row=0, column=1, rowspan=9, padx=20, pady=5, sticky="w")

ranking_title_canh = ttk.Label(ranking_frame_canh, text="Resultados", font=("Segoe UI", 12, "bold"))
ranking_title_canh.grid(row=0, column=0, columnspan=3, pady=(0,10), sticky="w")

ranking_tree_canh = ttk.Treeview(
    ranking_frame_canh,
    columns=("pos", "deltaP", "Sp", "Sdp"),
    show="headings",
    height=10
)
ranking_tree_canh.heading("pos", text="Posição", anchor="w")
ranking_tree_canh.heading("deltaP", text="deltaP", anchor="w")
ranking_tree_canh.heading("Sp", text="Sp", anchor="w")
ranking_tree_canh.heading("Sdp", text="Sdp", anchor="w")
ranking_tree_canh.column("pos", width=60, anchor="w")
ranking_tree_canh.column("deltaP", width=100, anchor="w")
ranking_tree_canh.column("Sp", width=100, anchor="w")
ranking_tree_canh.column("Sdp", width=100, anchor="w")
ranking_tree_canh.grid(row=1, column=0, columnspan=3, sticky="w")

scrollbar_canh = ttk.Scrollbar(ranking_frame_canh, orient="vertical", command=ranking_tree_canh.yview)
ranking_tree_canh.configure(yscroll=scrollbar_canh.set)
scrollbar_canh.grid(row=1, column=3, sticky="ns")

btn_limpar_canh = ttk.Button(ranking_frame_canh, text="Limpar Ranking", command=lambda: [ranking_canh.clear(), atualizar_ranking_canh()])
btn_limpar_canh.grid(row=2, column=0, columnspan=3, pady=5, sticky="w")

def atualizar_ranking_canh():
    for item in ranking_tree_canh.get_children():
        ranking_tree_canh.delete(item)
    if not ranking_canh:
        ranking_tree_canh.insert("", "end", values=("", "Nenhum resultado", "", ""))
        return
    ranking_ordenado = sorted(ranking_canh, key=lambda x: x["Sdp"], reverse=True)
    for idx, res in enumerate(ranking_ordenado, start=1):
        ranking_tree_canh.insert(
            "", "end",
            values=(
                idx,
                f"{res['deltaP']:.4f}",
                f"{res['Sp']:.4f}",
                f"{res['Sdp']:.4f}"
            )
        )

tk.mainloop()