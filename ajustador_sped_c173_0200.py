import customtkinter as ctk
from tkinter import filedialog
import re
import os

# Configuração do visual: tinta azul-escura com marca-texto âmbar no que muda no arquivo
ctk.set_appearance_mode("dark")

FUNDO = "#18202D"
SUPERFICIE = "#212B3B"
BORDA = "#2E3A4F"
TEXTO = "#E7EBF3"
SUAVE = "#8B96AB"
MARCA = "#F2B544"
MARCA_HOVER = "#FFC65C"
TINTA = "#1A1406"
ERRO = "#F27C6B"

FONTE_TITULO = ("Bahnschrift SemiBold", 26)
FONTE_REGISTRO = ("Bahnschrift SemiBold", 16)
FONTE_NUMERO = ("Bahnschrift SemiBold", 26)
FONTE_SPED = ("Consolas", 14)
FONTE_TEXTO = ("Segoe UI", 13)
FONTE_DESTAQUE = ("Segoe UI Semibold", 14)
FONTE_PEQUENA = ("Segoe UI", 11)
FONTE_BOTAO = ("Bahnschrift SemiBold", 16)

# Criando a janela principal
app = ctk.CTk(fg_color=FUNDO)
app.title("Ajustador SPED (C173 / 0200)")
app.resizable(False, False)

# --- LÓGICA PARA CENTRALIZAR A JANELA ---
largura_janela = 600
altura_janela = 480

# Obtém a largura e altura da tela do computador
largura_tela = app.winfo_screenwidth()
altura_tela = app.winfo_screenheight()

# Calcula a posição X e Y exata para o centro
pos_x = (largura_tela // 2) - (largura_janela // 2)
pos_y = (altura_tela // 2) - (altura_janela // 2)

# Aplica o tamanho e a posição na tela (formato: larguraxaltura+x+y)
app.geometry(f"{largura_janela}x{altura_janela}+{pos_x}+{pos_y}")
# ----------------------------------------

# Variáveis para guardar os caminhos
caminho_origem = ctk.StringVar()
caminho_destino = ctk.StringVar()

def limpar_contagens():
    for numero, unidade in (contagem_c173, contagem_0200):
        numero.configure(text="–", text_color=BORDA)
        unidade.configure(text="")

def selecionar_arquivo():
    arquivo = filedialog.askopenfilename(
        title="Selecione o arquivo SPED",
        filetypes=[("Arquivos de Texto", "*.txt")]
    )
    if arquivo:
        caminho_origem.set(arquivo)
        # Cria o nome do arquivo de saída automaticamente na mesma pasta
        nome_base, extensao = os.path.splitext(arquivo)
        caminho_destino.set(f"{nome_base}_corrigido{extensao}")

        pasta = os.path.normpath(os.path.dirname(arquivo))
        if len(pasta) > 46:
            pasta = "…" + pasta[-45:]
        label_arquivo.configure(text=os.path.basename(arquivo), text_color=TEXTO)
        label_pasta.configure(text=pasta)
        btn_selecionar.configure(text="Trocar arquivo")
        btn_corrigir.configure(state="normal", fg_color=MARCA, text_color=TINTA)
        limpar_contagens()
        label_status.configure(text="")

def corrigir():
    origem = caminho_origem.get()
    destino = caminho_destino.get()

    if not origem:
        label_status.configure(text="Escolha um arquivo SPED antes de corrigir.", text_color=ERRO)
        return

    try:
        total_corrigidas = 0
        total_cest = 0
        with open(origem, 'r', encoding='latin-1') as f_in, \
             open(destino, 'w', encoding='latin-1') as f_out:
            for linha in f_in:
                # Faz a alteração cirúrgica no C173
                if linha.startswith('|C173|'):
                    linha, n = re.subn(r'\|0,00\|(\s*)$', r'|1,00|\1', linha)
                    total_corrigidas += n
                # Limpa o CEST (campo 13 do 0200) quando contém apenas zeros
                elif linha.startswith('|0200|'):
                    campos = linha.split('|')
                    if len(campos) > 14 and re.fullmatch(r'0+', campos[13]):
                        campos[13] = ''
                        linha = '|'.join(campos)
                        total_cest += 1
                f_out.write(linha)

        contagem_c173[0].configure(text=str(total_corrigidas), text_color=MARCA if total_corrigidas else SUAVE)
        contagem_c173[1].configure(text="alterado(s)")
        contagem_0200[0].configure(text=str(total_cest), text_color=MARCA if total_cest else SUAVE)
        contagem_0200[1].configure(text="apagado(s)")
        label_status.configure(text=f"Concluído! Salvo como {os.path.basename(destino)}", text_color=TEXTO)
    except Exception as e:
        label_status.configure(text=f"Erro ao processar: {str(e)}", text_color=ERRO)

def criar_regra(pai, linha, registro, antes, depois, descricao):
    # Uma regra de ajuste: registro, trecho do SPED antes → depois e a contagem à direita
    ctk.CTkLabel(pai, text=registro, font=FONTE_REGISTRO, text_color=TEXTO, width=58, anchor="w").grid(row=linha, column=0, rowspan=2, sticky="w", padx=(20, 8), pady=14)

    trecho = ctk.CTkFrame(pai, fg_color="transparent")
    trecho.grid(row=linha, column=1, sticky="sw", pady=(14, 0))
    ctk.CTkLabel(trecho, text=antes, font=FONTE_SPED, text_color=SUAVE).pack(side="left")
    ctk.CTkLabel(trecho, text="→", font=FONTE_TEXTO, text_color=SUAVE).pack(side="left", padx=10)
    # O valor novo aparece como marca-texto: é o que o programa escreve no arquivo
    ctk.CTkLabel(trecho, text=depois, font=FONTE_SPED, text_color=TINTA, fg_color=MARCA, corner_radius=4, height=24).pack(side="left")

    ctk.CTkLabel(pai, text=descricao, font=FONTE_PEQUENA, text_color=SUAVE, anchor="w").grid(row=linha + 1, column=1, sticky="nw", pady=(0, 14))

    numero = ctk.CTkLabel(pai, text="–", font=FONTE_NUMERO, text_color=BORDA, anchor="e")
    numero.grid(row=linha, column=2, sticky="se", padx=20, pady=(10, 0))
    unidade = ctk.CTkLabel(pai, text="", font=FONTE_PEQUENA, text_color=SUAVE, anchor="e", height=16)
    unidade.grid(row=linha + 1, column=2, sticky="ne", padx=20, pady=(0, 14))
    return numero, unidade

# --- CONSTRUÇÃO DA INTERFACE ---

frame_cabecalho = ctk.CTkFrame(app, fg_color="transparent")
frame_cabecalho.pack(fill="x", padx=32, pady=(26, 0))

label_titulo = ctk.CTkLabel(frame_cabecalho, text="Ajustador SPED", font=FONTE_TITULO, text_color=TEXTO)
label_titulo.pack(side="left")

label_registros = ctk.CTkLabel(frame_cabecalho, text="C173 / 0200", font=FONTE_SPED, text_color=SUAVE)
label_registros.pack(side="left", padx=(12, 0), pady=(8, 0))

label_descricao = ctk.CTkLabel(app, text="Prepara o arquivo do SPED Fiscal para passar na validação do PVA.", font=FONTE_TEXTO, text_color=SUAVE)
label_descricao.pack(anchor="w", padx=32, pady=(0, 18))

# Arquivo escolhido
frame_arquivo = ctk.CTkFrame(app, fg_color=SUPERFICIE, border_color=BORDA, border_width=1, corner_radius=12)
frame_arquivo.pack(fill="x", padx=32)
frame_arquivo.grid_columnconfigure(0, weight=1)

label_arquivo = ctk.CTkLabel(frame_arquivo, text="Nenhum arquivo escolhido", font=FONTE_DESTAQUE, text_color=SUAVE, anchor="w")
label_arquivo.grid(row=0, column=0, sticky="w", padx=20, pady=(14, 0))

label_pasta = ctk.CTkLabel(frame_arquivo, text="Escolha o .txt do SPED gerado pelo sistema fiscal", font=FONTE_PEQUENA, text_color=SUAVE, anchor="w", height=18)
label_pasta.grid(row=1, column=0, sticky="w", padx=20, pady=(0, 14))

btn_selecionar = ctk.CTkButton(frame_arquivo, text="Escolher arquivo", command=selecionar_arquivo, font=FONTE_TEXTO, text_color=TEXTO, fg_color="transparent", hover_color=BORDA, border_color=BORDA, border_width=1, corner_radius=8, width=140, height=36)
btn_selecionar.grid(row=0, column=1, rowspan=2, padx=(10, 16))

# Regras de ajuste com a contagem de cada uma
frame_regras = ctk.CTkFrame(app, fg_color=SUPERFICIE, border_color=BORDA, border_width=1, corner_radius=12)
frame_regras.pack(fill="x", padx=32, pady=(12, 0))
frame_regras.grid_columnconfigure(1, weight=1)

contagem_c173 = criar_regra(frame_regras, 0, "C173", "|0,00|", "|1,00|", "Valor de tabela do medicamento zerado")
contagem_0200 = criar_regra(frame_regras, 3, "0200", "|0000000|", "||", "CEST preenchido só com zeros")

btn_corrigir = ctk.CTkButton(app, text="Corrigir arquivo", command=corrigir, font=FONTE_BOTAO, fg_color=BORDA, hover_color=MARCA_HOVER, text_color=TINTA, text_color_disabled=SUAVE, corner_radius=10, height=48, state="disabled")
btn_corrigir.pack(fill="x", padx=32, pady=(20, 0))

label_status = ctk.CTkLabel(app, text="", font=FONTE_TEXTO, anchor="w")
label_status.pack(fill="x", padx=34, pady=(8, 0))

# Roda o aplicativo
app.mainloop()
