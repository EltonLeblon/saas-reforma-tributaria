import streamlit as st
import pandas as pd
import sqlite3
import streamlit_authenticator as stauth
from datetime import datetime

# --- 1. CONFIGURAÇÃO DA BASE DE DADOS (SQLite) ---
def init_db():
    conn = sqlite3.connect('usuarios_saas.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS historico 
                 (usuario TEXT, produto TEXT, preco_novo REAL, data TEXT)''')
    conn.commit()
    return conn

conn = init_db()

# --- 2. SISTEMA DE AUTENTICAÇÃO (SIMPLIFICADO) ---
# Em produção, usaria um ficheiro YAML ou Base de Dados para as passwords
names = ['Utilizador Demo', 'Cliente Premium']
usernames = ['demo', 'premium']
passwords = ['123', '456'] # NOTA: Use passwords hasheadas em produção!

authenticator = stauth.Authenticate(
    {'usernames': {usernames[i]: {'name': names[i], 'password': passwords[i]} for i in range(len(usernames))}},
    'cookie_saas', 'signature_key', cookie_expiry_days=30
)

name, authentication_status, username = authenticator.login('Login', 'main')

# --- 3. LÓGICA DO SAAS (ÁREA LOGADA) ---
if authentication_status:
    authenticator.logout('Sair', 'sidebar')
    st.sidebar.title(f"Bem-vindo, {name}")
    
    st.title("🚀 Painel de Precificação Pro")

    # Verificação de Plano
    if username == 'demo':
        st.warning("⚠️ Você está no plano Grátis. O processamento em lote está bloqueado.")
    
    # --- CÁLCULO ---
    col1, col2 = st.columns(2)
    with col1:
        prod = st.text_input("Nome do Produto")
        preco = st.number_input("Preço Atual (R$)", min_value=0.0)
        carga = st.sidebar.slider("Alíquota IVA (%)", 25.0, 30.0, 26.5)
        
    if st.button("Calcular e Salvar"):
        # Lógica de cálculo (mesma do passo anterior)
        novo_p = (preco * 0.72) / (1 - (carga/100)) # Exemplo simplificado
        
        # Salvar na Base de Dados
        c = conn.cursor()
        c.execute("INSERT INTO historico VALUES (?, ?, ?, ?)", 
                  (username, prod, novo_p, datetime.now().strftime("%d/%m/%Y %H:%M")))
        conn.commit()
        st.success(f"Preço sugerido: R$ {novo_p:.2f}")

    # --- HISTÓRICO (O VALOR DO SAAS) ---
    st.divider()
    st.subheader("📜 Seu Histórico de Cálculos")
    historico_df = pd.read_sql_query(f"SELECT * FROM historico WHERE usuario='{username}'", conn)
    st.table(historico_df)

    # --- GATE DE PAGAMENTO (MONETIZAÇÃO) ---
    if username == 'demo':
        st.sidebar.divider()
        st.sidebar.markdown("### 💎 Torne-se Premium")
        st.sidebar.write("Aceda ao upload de Excel e suporte prioritário.")
        # Link do Stripe ou Checkout
        st.sidebar.link_button("Assinar por R$ 49/mês", "https://buy.stripe.com/exemplo")

elif authentication_status is False:
    st.error('Utilizador/Password incorretos')
elif authentication_status is None:
    st.warning('Por favor, insira o seu login.')