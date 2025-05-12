import tkinter as tk
from tkinter import ttk, messagebox
import statistics

valores_digitados = []

# Função para adicionar novo valor
def adicionar_valor():
    try:
        valor = float(entrada_valor.get())
        valores_digitados.append(valor)
        entrada_valor.delete(0, tk.END)
        atualizar_lista()
        atualizar_analises()
    except ValueError:
        messagebox.showerror("Erro", "Por favor, insira um número válido.")

# Atualizar a lista dos valores
def atualizar_lista():
    lista_valores.config(state='normal')
    lista_valores.delete(1.0, tk.END)
    for i, valor in enumerate(valores_digitados, 1):
        lista_valores.insert(tk.END, f"{i}: {valor}\n")
    lista_valores.config(state='disabled')

# Probabilidade do próximo valor ser alto ou baixo
def probabilidade_proximo_valor():
    ultimos = valores_digitados[-10:]
    if len(ultimos) < 5:
        return "Poucos dados para probabilidade."
    altos = sum(1 for v in ultimos if v >= 2)
    baixos = len(ultimos) - altos
    p_alto = altos / len(ultimos)
    p_baixo = baixos / len(ultimos)
    return f"Prob. Alto (≥2x): {p_alto:.1%} | Baixo (<2x): {p_baixo:.1%}"

# Detectar mudanças bruscas no padrão
def detectar_mudanca_padrao():
    if len(valores_digitados) < 20:
        return "Poucos dados para detectar mudanças."
    bloco1 = valores_digitados[-20:-10]
    bloco2 = valores_digitados[-10:]
    media1 = statistics.mean(bloco1)
    media2 = statistics.mean(bloco2)
    diferenca = abs(media2 - media1)
    if diferenca >= 1:
        return "Mudança brusca de padrão detectada!"
    return "Padrão relativamente estável."

# Previsão com base nos últimos valores
def proxima_previsao():
    if len(valores_digitados) < 3:
        return "Poucos dados para previsão."
    ultimos = valores_digitados[-3:]
    altos = sum(1 for v in ultimos if v >= 2)
    baixos = 3 - altos
    if altos >= 2:
        return "Próximo valor tende a ser BAIXO."
    elif baixos >= 2:
        return "Próximo valor tende a ser ALTO."
    return "Sem tendência clara."

# Atualiza análises e resultados
def atualizar_analises():
    analise1 = probabilidade_proximo_valor()
    analise2 = detectar_mudanca_padrao()
    analise3 = proxima_previsao()
    campo_resultado.config(state='normal')
    campo_resultado.delete(1.0, tk.END)
    campo_resultado.insert(tk.END, f"{analise1}\n{analise2}\n{analise3}")
    campo_resultado.config(state='disabled')

# Interface gráfica
janela = tk.Tk()
janela.title("Previsão Inteligente - Aviator")

frame = tk.Frame(janela)
frame.pack(pady=10)

entrada_valor = ttk.Entry(frame, width=20)
entrada_valor.grid(row=0, column=0, padx=5)

botao_adicionar = ttk.Button(frame, text="Adicionar Valor", command=adicionar_valor)
botao_adicionar.grid(row=0, column=1, padx=5)

lista_valores = tk.Text(janela, width=30, height=12, state='disabled', bg="#f0f0f0")
lista_valores.pack(pady=5)

campo_resultado = tk.Text(janela, width=50, height=5, state='disabled', bg="#e8f8f5", font=('Arial', 10, 'bold'))
campo_resultado.pack(pady=5)

janela.mainloop()
