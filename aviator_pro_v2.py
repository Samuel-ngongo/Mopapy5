import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor
from sklearn.exceptions import NotFittedError

st.set_page_config(page_title="Aviator PRO - IA Avançada", layout="centered")
st.title("Aviator PRO - IA Avançada com Machine Learning e Análise de Padrões")

# Limite máximo de dados para evitar lentidão
MAX_HIST = 200

# Inicializa session_state
if "valores" not in st.session_state:
    st.session_state.valores = []
if "historico_completo" not in st.session_state:
    st.session_state.historico_completo = []
if "modelo" not in st.session_state:
    st.session_state.modelo = None

# Função para criar features a partir dos dados
def criar_features(dados):
    df = pd.DataFrame({'valor': dados})
    df['media_movel_3'] = df['valor'].rolling(window=3, min_periods=1).mean()
    df['media_movel_5'] = df['valor'].rolling(window=5, min_periods=1).mean()
    df['variacao_pct'] = df['valor'].pct_change().fillna(0)
    df['desvio_3'] = df['valor'].rolling(window=3, min_periods=1).std().fillna(0)
    df['desvio_5'] = df['valor'].rolling(window=5, min_periods=1).std().fillna(0)
    df['indice'] = range(len(df))
    return df.dropna()

# Função para treinar modelo Random Forest
def treinar_modelo(dados):
    if len(dados) < 10:
        return None  # dados insuficientes
    df = criar_features(dados)
    X = df.drop(columns=['valor'])
    y = df['valor']
    modelo = RandomForestRegressor(n_estimators=100, random_state=42)
    modelo.fit(X, y)
    return modelo

# Função para prever próximo valor
def prever_proximo_valor(modelo, dados):
    if modelo is None:
        return None
    df = criar_features(dados)
    ultima_linha = df.iloc[[-1]].drop(columns=['valor'])
    try:
        pred = modelo.predict(ultima_linha)[0]
    except NotFittedError:
        return None
    return pred

# Função para detectar mudança brusca
def detectar_mudanca(dados, lim_media=1.0, lim_desvio=1.2):
    if len(dados) < 15:
        return False
    ultimos = np.array(dados[-5:])
    anteriores = np.array(dados[-10:-5])
    media_diff = abs(np.mean(ultimos) - np.mean(anteriores))
    desvio_diff = abs(np.std(ultimos) - np.std(anteriores))
    return media_diff > lim_media or desvio_diff > lim_desvio

# Função para analisar padrões simples
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

# Entrada do usuário
novo = st.text_input("Insira um valor (ex: 2.31):")

# Parâmetros ajustáveis
st.sidebar.header("Configurações")
janela_media = st.sidebar.slider("Janela média móvel para gráfico", 2, 10, 3)
limiar_queda = st.sidebar.slider("Limiar para alerta de queda", 1.0, 3.0, 1.5)
limiar_alta = st.sidebar.slider("Limiar para alerta de alta", 2.0, 5.0, 2.5)
limiar_mudanca_media = st.sidebar.slider("Limiar mudança média", 0.5, 3.0, 1.0)
limiar_mudanca_desvio = st.sidebar.slider("Limiar mudança desvio", 0.5, 3.0, 1.2)

if st.button("Adicionar") and novo:
    try:
        valor = float(novo)
        st.session_state.valores.append(valor)
        st.session_state.historico_completo.append((valor, datetime.now().strftime("%d/%m/%Y %H:%M")))
        # Limita tamanho do histórico
        if len(st.session_state.valores) > MAX_HIST:
            st.session_state.valores = st.session_state.valores[-MAX_HIST:]
            st.session_state.historico_completo = st.session_state.historico_completo[-MAX_HIST:]
        st.success("Valor adicionado.")
    except ValueError:
        st.error("Formato inválido. Insira um número decimal válido.")

if st.session_state.valores:
    # Treina o modelo com os dados atuais
    st.session_state.modelo = treinar_modelo(st.session_state.valores)

    # Previsão
    pred = prever_proximo_valor(st.session_state.modelo, st.session_state.valores)
    media_atual = np.mean(st.session_state.valores[-janela_media:])
    desvio_atual = np.std(st.session_state.valores[-janela_media:])

    st.subheader("Histórico (últimos 30 valores)")
    for valor, data in st.session_state.historico_completo[-30:]:
        cor = "🟥" if valor < limiar_queda else "🟩" if valor > limiar_alta else "⬜"
        st.write(f"{cor} {valor:.2f}x - {data}")

    # Gráficos
    df_plot = pd.DataFrame({
        'Índice': range(1, len(st.session_state.valores) + 1),
        'Valor': st.session_state.valores
    })
    df_plot['Média Móvel'] = df_plot['Valor'].rolling(window=janela_media, min_periods=1).mean()

    st.subheader("Gráfico de Valores e Média Móvel")
    st.line_chart(df_plot.set_index('Índice')[['Valor', 'Média Móvel']])

    # Resultados da previsão
    if pred is not None:
        st.subheader("Previsão do próximo valor")
        st.info(f"Previsão (Random Forest): {pred:.2f}x")
        st.info(f"Média móvel ({janela_media}): {media_atual:.2f}x")
        st.info(f"Desvio padrão ({janela_media}): {desvio_atual:.2f}")

        # Nível de confiança simplificado (quanto menor o desvio, maior a confiança)
        confianca = max(10, 100 - desvio_atual * 50)
        st.info(f"Nível de confiança estimado: {confianca:.1f}%")

        if confianca >= 75:
            st.success("Alta confiança nas próximas rodadas.")
        elif confianca >= 50:
            st.warning("Confiança moderada. Observe antes de agir.")
        else:
            st.error("Confiança baixa. Alta incerteza.")
    else:
        st.warning("Dados insuficientes para previsão.")

    # Detectar mudanças bruscas
    if detectar_mudanca(st.session_state.valores, limiar_mudanca_media, limiar_mudanca_desvio):
        st.warning("Mudança brusca de padrão detectada. IA recalibrando...")

    # Análise de padrões
    padroes = analisar_padroes(st.session_state.valores)
    for alerta, chance in padroes:
        st.info(f"Alerta de padrão: {alerta} ({chance}% de chance)")

if st.button("Limpar dados"):
    st.session_state.valores = []
    st.session_state.historico_completo = []
    st.session_state.modelo = None
    st.success("Histórico limpo.")
