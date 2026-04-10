import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Passo Seguro", page_icon="👣", layout="wide")

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
                        
                        st.session_state.dados_paciente = {
                            "Nome": user_match.iloc[0][col_nome],
                            "Cidade": user_match.iloc[0].get('cidade', ""),
                            "UF": user_match.iloc[0].get('uf', ""),
                            "Sexo": user_match.iloc[0].get('sexo', "Outro")
                        }
                        st.session_state.etapa = 2
                        st.rerun()
                    else:
                        st.error("Dados incorretos.")
                except Exception as e:
                    st.error(f"Erro no login: {e}")

        with tab_cadastro:
            st.markdown("### Criar Nova Conta")
            novo_nome = st.text_input("Nome Completo:", key="reg_nome")
            novo_email = st.text_input("E-mail:", key="reg_email")
            nova_senha = st.text_input("Senha:", type="password", key="reg_senha")
            
            col_c, col_u = st.columns([3, 1])
            with col_c:
                nova_cidade = st.text_input("Cidade:", key="reg_cidade")
            with col_u:
                lista_uf_reg = ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"]
                uf_reg = st.selectbox("UF:", lista_uf_reg, index=17, key="reg_uf")
