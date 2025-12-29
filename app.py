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

# --- 2. AUTENTICAÇÃO (ESTRUTURA CORRIGIDA PARA VERSION 0.3.x) ---
# A chave 'credentials' é OBRIGATÓRIA para evitar o KeyError
config = {
    'credentials': {
        'usernames': {
            'demo': {'name': 'Utilizador Demo', 'password': '123'},
            'premium': {'name': 'Cliente Premium', 'password': '456'}
        }
    },
    'cookie': {
        'expiry_days': 30,
        'key': 'assinatura_secreta',
        'name': 'cookie_saas'
    }
}

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# Chama o formulário de login
authenticator.login(location='main')

# --- 3. LÓGICA DO APP ---
if st.session_state["authentication_status"]:
    name = st.session_state["name"]
    username = st.session_state["username"]
    
    authenticator.logout('Sair do Sistema', 'sidebar')
    st.sidebar.success(f"Logado como: {name}")
    st.title("📊 Simulador de Precificação - Reforma Tributária")

    tab1, tab2 = st.tabs(["Cálculo Individual", "Histórico"])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Entrada de Dados")
            produto = st.text_input("Nome do Item", value="Produto Exemplo")
            p_venda = st.number_input("Preço de Venda Atual (R$)", min_value=0.0, value=100.0)
            carga_atual = st.slider("Carga Tributária Atual (%)", 0.0, 40.0, 27.25)
            
            st.divider()
            aliq_iva = st.sidebar.number_input("Nova Alíquota IBS/CBS (%)", value=26.5)
            credito = st.sidebar.number_input("Crédito de Insumos (%)", value=5.0)

        with col2:
            st.subheader("Resultado Pós-Reforma")
            # Lógica de cálculo
            preco_base = p_venda * (1 - carga_atual / 100)
            custo_ajustado = preco_base * (1 - credito / 100)
            novo_preco = custo_ajustado / (1 - (aliq_iva / 100))
            variacao = ((novo_preco / p_venda) - 1) * 100
            
            # Metric corrigida (sem erro de f-string)
            st.metric("Novo Preço Sugerido", f"R$ {novo_preco:.2f}", f"{variacao:.2f}%")
            
            if st.button("💾 Salvar Simulação"):
                c = conn.cursor()
                c.execute("INSERT INTO historico VALUES (?, ?, ?, ?)", 
                          (username, produto, round(novo_preco, 2), datetime.now().strftime("%d/%m %H:%M")))
                conn.commit()
                st.toast("Simulação salva!")

    with tab2:
        df_hist = pd.read_sql_query(f"SELECT produto, preco_novo, data FROM historico WHERE usuario='{username}'", conn)
        st.dataframe(df_hist, use_container_width=True)

elif st.session_state["authentication_status"] is False:
    st.error('Usuário ou senha incorretos.')
elif st.session_state["authentication_status"] is None:
    st.info('Por favor, faça o login para acessar o sistema.')