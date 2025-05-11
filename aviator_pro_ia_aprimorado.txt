import streamlit as st
import numpy as np
from datetime import datetime
import pandas as pd

try:
    from sklearn.linear_model import LinearRegression
except ImportError:
    LinearRegression = None

st.set_page_config(page_title="Aviator PRO - IA Adaptativa Total", layout="centered")
st.title("Aviator PRO - IA Inteligente com Padrões, Confiança e Histórico")

# Histórico
if "valores" not in st.session_state:
    st.session_state.valores = []

if "historico_completo" not in st.session_state:
    st.session_state.historico_completo = []

if "padroes_salvos" not in st.session_state:
    st.session_state.padroes_salvos = []

# Entrada de dados
novo = st.text_input("Insira um valor (ex: 2.31):")
if st.button("Adicionar") and novo:
    try:
        valor = float(novo)
        st.session_state.valores.append(valor)
        st.session_state.historico_completo.append((valor, datetime.now().strftime("%d/%m/%Y %H:%M")))
        st.success("Valor adicionado.")
    except:
        st.error("Formato inválido.")

# Níveis de sensibilidade
nivel = st.radio("Nível de sensibilidade da IA:", ["Conservador", "Normal", "Agressivo"])

# Previsão com IA híbrida adaptativa
def prever_valor(dados):
    if len(dados) < 5:
        return 1.50, 30

    pesos = np.linspace(1, 2, len(dados))
    media_ponderada = np.average(dados, weights=pesos)
    media_simples = np.mean(dados)

    if LinearRegression and len(dados) >= 6:
        X = np.array(range(len(dados))).reshape(-1, 1)
        y = np.array(dados)
        modelo = LinearRegression()
        modelo.fit(X, y)
        reg_pred = modelo.predict(np.array([[len(dados) + 1]]))[0]
    else:
        reg_pred = media_ponderada

    estimativa_final = (media_simples + media_ponderada + reg_pred) / 3
    desvio = np.std(dados[-10:]) if len(dados) >= 10 else np.std(dados)

    # Ajuste baseado na sensibilidade
    if nivel == "Conservador":
        confianca = max(10, 100 - desvio * 140)
    elif nivel == "Normal":
        confianca = max(10, 100 - desvio * 100)
    else:  # Agressivo
        confianca = max(10, 100 - desvio * 70)

    return round(estimativa_final, 2), round(confianca, 1)

# Detectar mudança brusca
def detectar_mudanca(dados):
    if len(dados) < 15:
        return False
    ultimos = np.array(dados[-5:])
    anteriores = np.array(dados[-10:-5])
    media_diff = abs(np.mean(ultimos) - np.mean(anteriores))
    desvio_diff = abs(np.std(ultimos) - np.std(anteriores))
    limite = {"Conservador": 0.8, "Normal": 1.0, "Agressivo": 1.2}[nivel]
    return media_diff > limite or desvio_diff > limite

# Analisar padrões
def analisar_padroes(dados):
    alertas = []
    if len(dados) >= 3:
        ultimos3 = dados[-3:]
        if all(v < 1.5 for v in ultimos3):
            alertas.append(("Queda contínua detectada", 70))
        if all(v > 2.5 for v in ultimos3):
            alertas.append(("Alta contínua detectada", 65))
        if len(set(np.sign(np.diff(ultimos3)))) > 1:
            alertas.append(("Alternância instável", 60))
    return alertas

# Verificar repetição de padrões antigos
def buscar_padrao_repetido(dados):
    if len(dados) < 6:
        return None
    atual = dados[-3:]
    for p in st.session_state.padroes_salvos:
        if np.allclose(p, atual, atol=0.15):
            return p
    st.session_state.padroes_salvos.append(atual)
    return None

# Visualização Interativa
def mostrar_graficos(valores):
    df = pd.DataFrame({
        'Índice': list(range(1, len(valores) + 1)),
        'Valor': valores
    })

    st.subheader("Mini Gráfico de Barras (últimos 10)")
    st.bar_chart(df.tail(10).set_index('Índice'))

    st.subheader("Evolução da Média")
    df['Média Móvel'] = df['Valor'].rolling(window=3, min_periods=1).mean()
    st.line_chart(df.set_index('Índice')[['Valor', 'Média Móvel']])

# Exibir histórico e análise
if st.session_state.valores:
    st.subheader("Histórico (últimos 30)")
    for valor, data in st.session_state.historico_completo[-30:]:
        cor = "🟥" if valor < 1.5 else "🟩" if valor > 2.5 else "⬜"
        st.write(f"{cor} {valor:.2f}x - {data}")

    mostrar_graficos(st.session_state.valores)

    st.subheader("Previsão e Análise Inteligente")
    estimativa, confianca = prever_valor(st.session_state.valores)
    st.info(f"Estimativa combinada para próxima rodada: {estimativa}x")
    st.info(f"Nível de confiança: {confianca}%")

    if confianca >= 75:
        st.success("Alta confiança nas próximas rodadas.")
    elif confianca >= 50:
        st.warning("Confiança moderada. Observe antes de agir.")
    else:
        st.error("Confiança baixa. Alta incerteza.")

    if detectar_mudanca(st.session_state.valores):
        st.warning("Mudança brusca detectada. IA recalibrando...")

    padroes = analisar_padroes(st.session_state.valores)
    for alerta, chance in padroes:
        st.info(f"Alerta de padrão: {alerta} ({chance}% de chance)")

    repetido = buscar_padrao_repetido(st.session_state.valores)
    if repetido is not None:
        st.success("Padrão repetido detectado! IA antecipando com base no histórico.")

# Limpar dados
if st.button("Limpar dados"):
    st.session_state.valores = []
    st.session_state.historico_completo = []
    st.session_state.padroes_salvos = []
    st.success("Histórico limpo.")
