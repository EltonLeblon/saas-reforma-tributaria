import streamlit as st
import pandas as pd
import sqlite3
import streamlit_authenticator as stauth
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Simulador Fiscal Pro", layout="wide")

# --- 1. BASE DE DADOS ---
def init_db():
    conn = sqlite3.connect('usuarios_saas.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS historico 
                 (usuario TEXT, produto TEXT, preco_novo REAL, data TEXT)''')
    conn.commit()
    return conn

conn = init_db()

# --- 2. AUTENTICAÇÃO (VERSÃO ATUALIZADA) ---
# Em produção, use senhas criptografadas!
config = {
    'usernames': {
        'demo': {'name': 'Utilizador Demo', 'password': '123'},
        'premium': {'name': 'Cliente Premium', 'password': '456'}
    }
}

authenticator = stauth.Authenticate(
    config['usernames'],
    'cookie_saas',
    'signature_key',
    cookie_expiry_days=30
)

# CHAMADA CORRETA DO LOGIN: Apenas o parâmetro 'location'
authenticator.login(location='main')

# --- 3. LÓGICA DO APP ---
if st.session_state["authentication_status"]:
    # Captura dados da sessão
    name = st.session_state["name"]
    username = st.session_state["username"]
    
    authenticator.logout('Sair do Sistema', 'sidebar')
    
    st.sidebar.success(f"Logado como: {name}")
    st.title("📊 Simulador de Precificação - Reforma Tributária")

    # Layout em colunas
    tab1, tab2 = st.tabs(["Cálculo Individual", "Histórico de Simulações"])

    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Entrada de Dados")
            produto = st.text_input("Nome do Item", placeholder="Ex: Cadeira de Escritório")
            p_venda = st.number_input("Preço de Venda Atual (R$)", min_value=0.0, value=100.0)
            carga_atual = st.slider("Carga Tributária Atual (%)", 0.0, 40.0, 27.25)
            
            # Configurações da Reforma
            st.divider()
            aliq_iva = st.sidebar.number_input("Nova Alíquota IBS/CBS (%)", value=26.5)
            credito = st.sidebar.number_input("Crédito de Insumos (%)", value=5.0)

        with col2:
            st.subheader("Resultado Pós-Reforma")
            
            # Lógica Tributária:
            # 1. Preço Base (Líquido de impostos antigos)
            preco_base = p_venda * (1 - carga_atual / 100)
            
            # 2. Custo Ajustado (Considerando crédito da reforma)
            custo_ajustado = preco_base * (1 - credito / 100)
            
            # 3. Novo Preço (Fórmula com imposto "por fora")
            # Novo Preço = Custo / (1 - (IVA / 100))
            novo_preco = custo_ajustado / (1 - (aliq_iva / 100))
            
            variacao = ((novo_preco / p_venda) - 1) * 100
            
            st.metric("Novo Preço Sugerido", f"