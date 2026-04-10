import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Passo Seguro", page_icon="👣", layout="centered")

# --- CONEXÃO COM GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- SISTEMA DE AUTENTICAÇÃO (LOGIN/CADASTRO) ---
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
                    df_users = conn.read(worksheet="usuarios")
                    
                    # CORREÇÃO: Garante que a coluna email existe antes de filtrar
                    if 'email' not in df_users.columns:
                        st.error("Base de dados vazia. Por favor, realize o primeiro cadastro.")
                    else:
                        user_match = df_users[(df_users['email'] == email_login) & (df_users['senha'] == senha_login)]
                        if not user_match.empty:
                            st.session_state.authenticated = True
                            st.session_state.usuario_nome = user_match.iloc[0]['nome']
                            st.rerun()
                        else:
                            st.error("E-mail ou senha incorretos.")
                except:
                    st.error("Erro: A aba 'usuarios' não existe na planilha. Crie-a com as colunas: nome, email, senha")

        with tab_cadastro:
            st.subheader("Crie sua conta")
            n_nome = st.text_input("Nome Completo:", key="c_nome")
            n_email = st.text_input("E-mail:", key="c_email")
            n_senha = st.text_input("Senha:", type="password", key="c_senha")
            
            if st.button("FINALIZAR CADASTRO"):
                if n_nome and n_email and n_senha:
                    try:
                        try:
                            df_users = conn.read(worksheet="usuarios")
                        except:
                            # Se a aba estiver sumida, cria a estrutura do zero
                            df_users = pd.DataFrame(columns=["nome", "email", "senha"])

                        # CORREÇÃO: Força a criação da coluna 'email' se a planilha vier limpa
                        if 'email' not in df_users.columns:
                             df_users = pd.DataFrame(columns=["nome", "email", "senha"])

                        if n_email in df_users['email'].values:
                            st.error("Este e-mail já está cadastrado.")
                        else:
                            novo_u = pd.DataFrame([{"nome": n_nome, "email": n_email, "senha": n_senha}])
                            df_atualizado = pd.concat([df_users, novo_u], ignore_index=True)
                            conn.update(worksheet="usuarios", data=df_atualizado)
                            st.success("Cadastro realizado! Vá para a aba 'Entrar'.")
                    except Exception as e:
                        st.error(f"Erro técnico ao salvar: {e}")
                else:
                    st.warning("Preencha todos os campos.")
        return False
    return True
        # --- ABA DE LOGIN ---
        with tab_login:
            email_login = st.text_input("E-mail:", key="l_email")
            senha_login = st.text_input("Senha:", type="password", key="l_senha")
            if st.button("ACESSAR SISTEMA"):
                try:
                    df_users = conn.read(worksheet="usuarios")
                    # Verifica credenciais
                    user_match = df_users[(df_users['email'] == email_login) & (df_users['senha'] == senha_login)]
                    
                    if not user_match.empty:
                        st.session_state.authenticated = True
                        st.session_state.usuario_nome = user_match.iloc[0]['nome']
                        st.rerun()
                    else:
                        st.error("E-mail ou senha incorretos.")
                except:
                    st.error("Erro: A aba 'usuarios' não foi encontrada ou está vazia.")

        # --- ABA DE CADASTRO ---
        with tab_cadastro:
            st.subheader("Crie sua conta")
            n_nome = st.text_input("Nome Completo:", key="c_nome")
            n_email = st.text_input("E-mail:", key="c_email")
            n_senha = st.text_input("Senha:", type="password", key="c_senha")
            
            if st.button("FINALIZAR CADASTRO"):
                if n_nome and n_email and n_senha:
                    try:
                        try:
                            df_users = conn.read(worksheet="usuarios")
                        except:
                            df_users = pd.DataFrame(columns=["nome", "email", "senha"])

                        if n_email in df_users['email'].values:
                            st.error("Este e-mail já está cadastrado.")
                        else:
                            novo_u = pd.DataFrame([{"nome": n_nome, "email": n_email, "senha": n_senha}])
                            df_atualizado = pd.concat([df_users, novo_u], ignore_index=True)
                            conn.update(worksheet="usuarios", data=df_atualizado)
                            st.success("Cadastro realizado! Agora faça o login na aba ao lado.")
                    except Exception as e:
                        st.error(f"Erro ao cadastrar: {e}")
                else:
                    st.warning("Preencha todos os campos.")
        return False
    return True

# --- INÍCIO DO FORMULÁRIO (APÓS LOGIN) ---
if auth_system():
    # Estilo CSS
    # --- ESTILO CSS (CORRIGIDO) ---
    st.markdown("""
        <style>
        .stButton>button { 
            width: 100%; 
            border-radius: 10px; 
            background-color: #007bff; 
            color: white; 
            font-weight: bold; 
            height: 3em; 
        }
        .card { 
            padding: 20px; 
            border-radius: 15px; 
            background-color: #ffffff; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.1); 
            margin-bottom: 20px; 
            border-left: 5px solid #007bff; 
            color: black; 
        }
        </style>
        """, unsafe_allow_html=True) # <-- O fechamento deve ser exatamente assim
