import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Passo Seguro", page_icon="👣", layout="centered")

# --- CONEXÃO COM GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def auth_system():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.markdown("<h1 style='text-align: center; color: #007bff;'>👣 Passo Seguro</h1>", unsafe_allow_html=True)
        tab_login, tab_cadastro = st.tabs(["🔐 Entrar", "📝 Cadastrar-se"])

        with tab_login:
            email_login = st.text_input("E-mail:", key="l_email")
            senha_login = st.text_input("Senha:", type="password", key="l_senha")
            if st.button("ACESSAR SISTEMA"):
                try:
                    df_users = conn.read(worksheet="usuarios", ttl=0)
                    df_users.columns = [str(c).strip().lower() for c in df_users.columns]
                    email_digitado = email_login.strip().lower()
                    senha_digitada = str(senha_login).strip()
                    
                    def limpar_v(v):
                        v = str(v).strip()
                        return v[:-2] if v.endswith('.0') else v

                    df_users['email_c'] = df_users['email'].astype(str).str.strip().str.lower()
                    df_users['senha_c'] = df_users['senha'].apply(limpar_v)
                    
                    user_match = df_users[(df_users['email_c'] == email_digitado) & (df_users['senha_c'] == senha_digitada)]
                    
                    if not user_match.empty:
                        st.session_state.authenticated = True
                        col_nome = [c for c in df_users.columns if 'nome' in c][0]
                        st.session_state.usuario_nome = user_match.iloc[0][col_nome]
                        st.rerun()
                    else:
                        st.error("Dados incorretos.")
                except Exception as e:
                    st.error(f"Erro: {e}")
        return False
    return True

if auth_system():
    # CSS Customizado
    st.markdown("""
        <style>
        .stButton>button { width: 100%; border-radius: 10px; background-color: #007bff; color: white; font-weight: bold; }
        .card { padding: 20px; border-radius: 15px; background-color: #ffffff; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; border-left: 5px solid #007bff; color: black; }
        .alerta-card { padding: 15px; border-radius: 10px; background-color: #fff3cd; border-left: 5px solid #ffc107; color: #856404; margin-top: 10px; font-weight: bold; }
        .orientacao-card { padding: 15px; border-radius: 10px; background-color: #d1ecf1; border-left: 5px solid #17a2b8; color: #0c5460; margin-top: 10px; }
        </style>
        """, unsafe_allow_html=True)

    if 'etapa' not in st.session_state: st.session_state.etapa = 1
    if 'dados_paciente' not in st.session_state: st.session_state.dados_paciente = {}

    st.sidebar.write(f"👤 {st.session_state.usuario_nome}")
    if st.sidebar.button("Sair"):
        st.session_state.authenticated = False
        st.rerun()

    # --- ETAPA 1: DADOS FIXOS DO PACIENTE ---
    if st.session_state.etapa == 1:
        st.markdown("<h2 style='text-align: center;'>👤 Identificação do Paciente</h2>", unsafe_allow_html=True)
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            nome_p = st.text_input("Nome do Paciente")
            col1, col2 = st.columns(2)
            with col1:
                nasc = st.date_input("Nascimento", min_value=datetime(1920,1,1), format="DD/MM/YYYY")
            with col2:
                sexo = st.selectbox("Sexo", ["Masculino", "Feminino", "Outro"])
            
            col_cid, col_uf = st.columns
