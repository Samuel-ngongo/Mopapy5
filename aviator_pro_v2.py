
import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime

try:
    from sklearn.linear_model import LinearRegression
except ImportError:
    LinearRegression = None

st.set_page_config(page_title="Aviator PRO V2", layout="centered")
st.title("Aviator PRO V2 - IA Avançada com Análise Adaptativa")

# Inicializar histórico
if "valores" not in st.session_state:
    st.session_state.valores = []
if "historico_completo" not in st.session_state:
    st.session_state.historico_completo = []

novo = st.text_input("Insira um valor (ex: 2.31):")
if st.button("Adicionar") and novo:
    try:
        valor = float(novo)
        st.session_state.valores.append(valor)
        st.session_state.historico_completo.append((valor, datetime.now().strftime("%d/%m/%Y %H:%M")))
        st.success("Valor adicionado.")
    except:
        st.error("Formato inválido.")

def prever_faixas(dados):
    if len(dados) < 5:
        return (1.2, 1.5, 1.8), 40, "Poucos dados para análise precisa."

    pesos = np.linspace(1, 2, len(dados))
    media_pond = np.average(dados, weights=pesos)
    desvio = np.std(dados[-10:]) if len(dados) >= 10 else np.std(dados)
    confianca = max(10, 100 - desvio * 100)

    if LinearRegression and len(dados) >= 6:
        X = np.array(range(len(dados))).reshape(-1, 1)
        y = np.array(dados)
        modelo = LinearRegression()
        modelo.fit(X, y)
        pred = modelo.predict(np.array([[len(dados) + 1]]))[0]
    else:
        pred = media_pond

    min_prev = max(1.01, pred - desvio)
    max_prev = pred + desvio
    media_prev = (min_prev + max_prev) / 2

    explicacao = f"Nos últimos 10 jogos, a média foi de {np.mean(dados[-10:]):.2f}x, com desvio de {desvio:.2f}."
    return (round(min_prev, 2), round(media_prev, 2), round(max_prev, 2)), round(confianca, 1), explicacao

def detectar_nova_tendencia(dados):
    if len(dados) < 10:
        return False
    ultimos = dados[-5:]
    anteriores = dados[-10:-5]
    return abs(np.mean(ultimos) - np.mean(anteriores)) > 1.0

def mostrar_graficos(valores):
    df = pd.DataFrame({'Índice': list(range(1, len(valores) + 1)), 'Valor': valores})
    st.subheader("Gráfico de Barras (últimos 10)")
    st.bar_chart(df.tail(10).set_index("Índice"))
    st.subheader("Linha de Tendência")
    df['Média Móvel'] = df['Valor'].rolling(window=3, min_periods=1).mean()
    st.line_chart(df.set_index("Índice")[['Valor', 'Média Móvel']])

if st.session_state.valores:
    st.subheader("Histórico")
    for valor, data in st.session_state.historico_completo[-30:]:
        cor = "🟥" if valor < 1.5 else "🟩" if valor > 2.5 else "⬜"
        st.write(f"{cor} {valor:.2f}x - {data}")

    mostrar_graficos(st.session_state.valores)

    st.subheader("Previsão Inteligente")
    (min_p, media_p, max_p), confianca, explicacao = prever_faixas(st.session_state.valores)
    st.info(f"Faixa Prevista: {min_p}x a {max_p}x (Média esperada: {media_p}x)")
    st.info(f"Nível de confiança: {confianca}%")
    st.caption(explicacao)

    if confianca >= 75:
        st.success("Alta confiança para próxima rodada.")
    elif confianca >= 50:
        st.warning("Confiança moderada. Acompanhe com atenção.")
    else:
        st.error("Confiança baixa. Evite ações precipitadas.")

    if detectar_nova_tendencia(st.session_state.valores):
        st.warning("Novo padrão detectado. IA ajustando comportamento.")

if st.button("Limpar dados"):
    st.session_state.valores = []
    st.session_state.historico_completo = []
    st.success("Histórico limpo.")
