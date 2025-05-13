import streamlit as st
import numpy as np
import pandas as pd
from collections import Counter
from sklearn.ensemble import RandomForestClassifier
import re

st.set_page_config(page_title="Super Bot de Roleta PRO", layout="wide")
st.title("🎰 Super Bot de Roleta – IA Avançada e Padrões Curtos")

# --- Sessão ---
if "resultados" not in st.session_state:
    st.session_state.resultados = []

# Funções auxiliares
red_numbers = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}
black_numbers = {2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35}

def get_color(number):
    if number == 0:
        return 'Green'
    elif number in red_numbers:
        return 'Red'
    else:
        return 'Black'

def get_parity(number):
    if number == 0:
        return 'None'
    elif number % 2 == 0:
        return 'Even'
    else:
        return 'Odd'

def get_range(number):
    if number == 0:
        return 'Zero'
    elif 1 <= number <= 18:
        return '1-18'
    elif 19 <= number <= 36:
        return '19-36'
    else:
        return 'None'

def get_dozen(number):
    if number == 0:
        return 'None'
    elif 1 <= number <= 12:
        return '1st 12'
    elif 13 <= number <= 24:
        return '2nd 12'
    else:
        return '3rd 12'

def get_column(number):
    if number == 0:
        return 'None'
    elif number % 3 == 1:
        return '1st'
    elif number % 3 == 2:
        return '2nd'
    else:
        return '3rd'

def parse_input(text):
    return [int(x) for x in re.findall(r'\d+', text)]

def gerar_features(seq):
    df = pd.DataFrame({'numero': seq})
    df['cor'] = df['numero'].apply(get_color).map({'Red':1, 'Black':0, 'Green':-1})
    df['par'] = df['numero'].apply(get_parity).map({'Even':1, 'Odd':0, 'None':-1})
    df['faixa'] = df['numero'].apply(get_range).map({'1-18':1, '19-36':2, 'Zero':0, 'None':-1})
    df['duzia'] = df['numero'].apply(get_dozen).map({'1st 12':1, '2nd 12':2, '3rd 12':3, 'None':0})
    df['coluna'] = df['numero'].apply(get_column).map({'1st':1, '2nd':2, '3rd':3, 'None':0})
    for lag in range(1,4):
        df[f'lag_{lag}'] = df['numero'].shift(lag, fill_value=0)
    return df

def max_seq(lst, value):
    max_seq = seq = 0
    for v in lst:
        if v == value:
            seq += 1
            max_seq = max(max_seq, seq)
        else:
            seq = 0
    return max_seq

def tendencia_curta(lst):
    if not lst:
        return None, 0
    c = Counter(lst)
    mais_comum = c.most_common(1)[0][0]
    freq = c[mais_comum]/len(lst)
    return mais_comum, freq

def explicacao_curta(campo, tendencia, freq, ultimos):
    if freq == 1.0 and len(ultimos) > 1:
        return f"Nos últimos {len(ultimos)} resultados, só saiu {tendencia} em {campo}. Forte tendência, mas reversão pode ocorrer."
    elif freq >= 0.67:
        return f"{tendencia} domina {campo} nos últimos {len(ultimos)} resultados. Tendência moderada."
    elif freq >= 0.5:
        return f"{campo} está equilibrado, mas {tendencia} aparece um pouco mais."
    else:
        return f"Não há tendência forte para {campo} nos últimos {len(ultimos)} resultados."

# --- Layout com abas ---
tabs = st.tabs([
    "Histórico", "Estatísticas", "Previsão/IA", "Mudanças de Padrão Curto", "Estratégias", "Ajuda"
])

# --- HISTÓRICO ---
with tabs[0]:
    st.header("Histórico de Resultados")
    entrada = st.text_area("Insira resultados (um número por linha, vírgula ou espaço):")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Adicionar ao histórico"):
            novos = parse_input(entrada)
            st.session_state.resultados.extend(novos)
            st.success(f"{len(novos)} resultados adicionados ao histórico.")
    with col2:
        if st.button("Limpar histórico"):
            st.session_state.resultados = []
            st.success("Histórico limpo.")
    if st.session_state.resultados:
        ultimos = st.session_state.resultados[-20:]
        df_hist = pd.DataFrame({
            "Número": ultimos,
            "Cor": [get_color(n) for n in ultimos],
            "Par/Ímpar": [get_parity(n) for n in ultimos],
            "Faixa": [get_range(n) for n in ultimos],
            "Dúzia": [get_dozen(n) for n in ultimos],
            "Coluna": [get_column(n) for n in ultimos]
        })
        st.dataframe(df_hist)

# --- ESTATÍSTICAS ---
with tabs[1]:
    st.header("Estatísticas Detalhadas")
    if st.session_state.resultados:
        cores = [get_color(n) for n in st.session_state.resultados]
        pares = [get_parity(n) for n in st.session_state.resultados]
        faixas = [get_range(n) for n in st.session_state.resultados]
        duzias = [get_dozen(n) for n in st.session_state.resultados]
        colunas = [get_column(n) for n in st.session_state.resultados]
        st.subheader("Frequências")
        colA, colB, colC, colD = st.columns(4)
        with colA:
            st.metric("Vermelho", cores.count("Red"))
            st.metric("Preto", cores.count("Black"))
        with colB:
            st.metric("Par", pares.count("Even"))
            st.metric("Ímpar", pares.count("Odd"))
        with colC:
            st.metric("1-18", faixas.count("1-18"))
            st.metric("19-36", faixas.count("19-36"))
        with colD:
            st.metric("Zero", faixas.count("Zero"))
            st.metric("Total", len(st.session_state.resultados))
        st.write("Números mais frequentes:", Counter(st.session_state.resultados).most_common(5))
        st.subheader("Gráficos")
        st.bar_chart(pd.Series(st.session_state.resultados).value_counts().sort_index())
    else:
        st.info("Adicione resultados para ver estatísticas.")

# --- PREVISÃO / IA ---
with tabs[2]:
    st.header("Previsão Inteligente para Todos os Mercados")
    if len(st.session_state.resultados) >= 3:
        ultimos = st.session_state.resultados[-3:]
        df_feat = gerar_features(st.session_state.resultados)
        X = df_feat.drop(columns=['numero'])
        # Previsão de cor
        y_cor = [get_color(n) for n in df_feat['numero']]
        model_cor = RandomForestClassifier(n_estimators=100, random_state=42)
        if len(X) > 3:
            model_cor.fit(X[:-1], y_cor[1:])
            pred_cor = model_cor.predict([X.iloc[-1]])[0]
            prob_cor = model_cor.predict_proba([X.iloc[-1]])[0]
            cor_labels = model_cor.classes_
            prob_cor_dict = {cor_labels[i]: f"{prob_cor[i]*100:.1f}%" for i in range(len(cor_labels))}
            st.info(f"Previsão de cor: **{pred_cor}** | Probabilidades: {prob_cor_dict}")
        else:
            st.info("Poucos dados para IA, usando análise de padrão curto.")
            cor_tend, cor_conf = tendencia_curta([get_color(n) for n in ultimos])
            st.info(f"Previsão de cor: **{cor_tend}** (confiança: {cor_conf*100:.1f}%)")
            st.caption(explicacao_curta("cor", cor_tend, cor_conf, ultimos))
        # Previsão de paridade
        y_par = [get_parity(n) for n in df_feat['numero']]
        model_par = RandomForestClassifier(n_estimators=100, random_state=42)
        if len(X) > 3:
            model_par.fit(X[:-1], y_par[1:])
            pred_par = model_par.predict([X.iloc[-1]])[0]
            st.info(f"Previsão de Par/Ímpar: **{pred_par}**")
        else:
            par_tend, par_conf = tendencia_curta([get_parity(n) for n in ultimos])
            st.info(f"Previsão Par/Ímpar: **{par_tend}** (confiança: {par_conf*100:.1f}%)")
            st.caption(explicacao_curta("paridade", par_tend, par_conf, ultimos))
        # Previsão de faixa (1-18 / 19-36)
        y_faixa = [get_range(n) for n in df_feat['numero']]
        model_faixa = RandomForestClassifier(n_estimators=100, random_state=42)
        if len(X) > 3:
            model_faixa.fit(X[:-1], y_faixa[1:])
            pred_faixa = model_faixa.predict([X.iloc[-1]])[0]
            st.info(f"Previsão de Faixa: **{pred_faixa}**")
        else:
            faixa_tend, faixa_conf = tendencia_curta([get_range(n) for n in ultimos])
            st.info(f"Previsão de Faixa: **{faixa_tend}** (confiança: {faixa_conf*100:.1f}%)")
            st.caption(explicacao_curta("faixa", faixa_tend, faixa_conf, ultimos))
        # Previsão de dúzia
        y_duzia = [get_dozen(n) for n in df_feat['numero']]
        model_duzia = RandomForestClassifier(n_estimators=100, random_state=42)
        if len(X) > 3:
            model_duzia.fit(X[:-1], y_duzia[1:])
            pred_duzia = model_duzia.predict([X.iloc[-1]])[0]
            st.info(f"Previsão de Dúzia: **{pred_duzia}**")
        else:
            duzia_tend, duzia_conf = tendencia_curta([get_dozen(n) for n in ultimos])
            st.info(f"Previsão de Dúzia: **{duzia_tend}** (confiança: {duzia_conf*100:.1f}%)")
            st.caption(explicacao_curta("dúzia", duzia_tend, duzia_conf, ultimos))
        # Previsão de coluna
        y_coluna = [get_column(n) for n in df_feat['numero']]
        model_coluna = RandomForestClassifier(n_estimators=100, random_state=42)
        if len(X) > 3:
            model_coluna.fit(X[:-1], y_coluna[1:])
            pred_coluna = model_coluna.predict([X.iloc[-1]])[0]
            st.info(f"Previsão de Coluna: **{pred_coluna}**")
        else:
            coluna_tend, coluna_conf = tendencia_curta([get_column(n) for n in ultimos])
            st.info(f"Previsão de Coluna: **{coluna_tend}** (confiança: {coluna_conf*100:.1f}%)")
            st.caption(explicacao_curta("coluna", coluna_tend, coluna_conf, ultimos))
    else:
        st.warning("Insira pelo menos 3 resultados para ativar a previsão.")

# --- PADRÃO CURTO ---
with tabs[3]:
    st.header("Mudanças e Tendências com Poucos Dados")
    if st.session_state.resultados:
        ultimos = st.session_state.resultados[-3:]
        st.write(f"Últimos 3 resultados: {ultimos}")
        cores = [get_color(n) for n in ultimos]
        pares = [get_parity(n) for n in ultimos]
        faixas = [get_range(n) for n in ultimos]
        duzias = [get_dozen(n) for n in ultimos]
        colunas = [get_column(n) for n in ultimos]
        st.info(f"Tendência de cor: {tendencia_curta(cores)[0]} ({tendencia_curta(cores)[1]*100:.1f}%)")
        st.info(f"Tendência de paridade: {tendencia_curta(pares)[0]} ({tendencia_curta(pares)[1]*100:.1f}%)")
        st.info(f"Tendência de faixa: {tendencia_curta(faixas)[0]} ({tendencia_curta(faixas)[1]*100:.1f}%)")
        st.info(f"Tendência de dúzia: {tendencia_curta(duzias)[0]} ({tendencia_curta(duzias)[1]*100:.1f}%)")
        st.info(f"Tendência de coluna: {tendencia_curta(colunas)[0]} ({tendencia_curta(colunas)[1]*100:.1f}%)")
        # Mudança detectada?
        if len(set(cores)) > 1:
            st.warning("Mudança de cor detectada nos últimos 3 resultados!")
        if len(set(pares)) > 1:
            st.warning("Mudança de paridade detectada nos últimos 3 resultados!")
        if len(set(faixas)) > 1:
            st.warning("Mudança de faixa detectada nos últimos 3 resultados!")
    else:
        st.info("Adicione pelo menos 3 resultados para análise de padrão curto.")

# --- ESTRATÉGIAS ---
with tabs[4]:
    st.header("Estratégias Automáticas")
    st.markdown("Simule estratégias clássicas e veja o desempenho.")
    if st.session_state.resultados:
        saldo_inicial = st.number_input("Saldo inicial", min_value=10, value=1000)
        aposta = st.number_input("Valor da aposta base", min_value=1, value=10)
        escolha = st.selectbox("Tipo de aposta", ["Red", "Black"])
        estrategia = st.selectbox("Estratégia", ["Flat", "Martingale"])
        resultados = [get_color(n) for n in st.session_state.resultados]
        saldo = saldo_inicial
        aposta_atual = aposta
        historico_saldo = [saldo]
        for res in resultados:
            if res == escolha:
                saldo += aposta_atual
                if estrategia == "Martingale":
                    aposta_atual = aposta
            else:
                saldo -= aposta_atual
                if estrategia == "Martingale":
                    aposta_atual *= 2
            if saldo <= 0:
                break
            historico_saldo.append(saldo)
        st.line_chart(pd.Series(historico_saldo, name="Saldo"))
        st.success(f"Saldo final: {saldo}")
    else:
        st.info("Adicione resultados para simular estratégias.")

# --- AJUDA ---
with tabs[5]:
    st.header("Ajuda e Dicas")
    st.markdown("""
    **Como usar este painel:**
    - Insira resultados na aba Histórico.
    - Veja estatísticas e padrões na aba Estatísticas.
    - Use a aba Previsão/IA para prever todos os mercados (cor, par/ímpar, dúzia, coluna, faixa).
    - Veja tendências e mudanças mesmo com poucos dados (3 resultados já ativam a análise).
    - Simule estratégias automáticas e veja gráficos do saldo.
    - Sempre jogue com responsabilidade!
    """)

st.caption("Versão IA Adaptativa – Desenvolvido por Por SAMUEL Ngongo")

