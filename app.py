import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Passo Seguro", page_icon="👣", layout="centered")

# --- CONEXÃO COM GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- SISTEMA DE LOGIN E CADASTRO ---
def auth_system():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.markdown("<h1 style='text-align: center;'>👣 Passo Seguro</h1>", unsafe_allow_html=True)
        
        # Criando abas para separar Login de Cadastro
        tab_login, tab_cadastro = st.tabs(["🔐 Entrar", "📝 Cadastrar-se"])

        # --- ABA DE LOGIN ---
        with tab_login:
            email_login = st.text_input("E-mail:")
            senha_login = st.text_input("Senha:", type="password")
            manter = st.checkbox("Manter conectado")
            
            if st.button("LOGAR"):
                try:
                    # Lê a aba de usuários (certifique-se que ela existe na sua planilha)
                    df_users = conn.read(worksheet="usuarios")
                    
                    # Verifica se o email e senha batem
                    user_match = df_users[(df_users['email'] == email_login) & (df_users['senha'] == senha_login)]
                    
                    if not user_match.empty:
                        st.session_state.authenticated = True
                        st.session_state.usuario_nome = user_match.iloc[0]['nome']
                        if manter:
                            st.query_params["auth_user"] = "liberado"
                            st.query_params["user_nome"] = st.session_state.usuario_nome
                        st.rerun()
                    else:
                        st.error("E-mail ou senha incorretos.")
                except Exception as e:
                    st.error("Erro ao acessar base de usuários. Verifique se a aba 'usuarios' existe na planilha.")

        # --- ABA DE CADASTRO ---
        with tab_cadastro:
            st.subheader("Crie sua conta")
            novo_nome = st.text_input("Nome Completo:")
            novo_email = st.text_input("E-mail para acesso:")
            nova_senha = st.text_input("Crie uma senha:", type="password")
            confirma_senha = st.text_input("Confirme a senha:", type="password")
            
            if st.button("FINALIZAR CADASTRO"):
                if nova_senha != confirma_senha:
                    st.warning("As senhas não coincidem.")
                elif not novo_nome or not novo_email:
                    st.warning("Preencha todos os campos.")
                else:
                    try:
                        # Tenta ler usuários existentes
                        try:
                            df_users = conn.read(worksheet="usuarios")
                        except:
                            df_users = pd.DataFrame(columns=["nome", "email", "senha"])

                        if novo_email in df_users['email'].values:
                            st.error("Este e-mail já está cadastrado.")
                        else:
                            # Adiciona novo usuário
                            novo_u = pd.DataFrame([{"nome": novo_nome, "email": novo_email, "senha": nova_senha}])
                            df_atualizado = pd.concat([df_users, novo_u], ignore_index=True)
                            
                            conn.update(worksheet="usuarios", data=df_atualizado)
                            st.success("Cadastro realizado com sucesso! Vá para a aba 'Entrar'.")
                    except Exception as e:
                        st.error(f"Erro ao salvar cadastro: {e}")
        return False
    return True

# --- INÍCIO DO APP APÓS LOGIN ---
if auth_system():
    # Se o usuário já estiver logado (pela URL ou pelo botão)
    if "usuario_nome" not in st.session_state:
        st.session_state.usuario_nome = st.query_params.get("user_nome", "Usuário")

    st.sidebar.write(f"Bem-vindo, **{st.session_state.usuario_nome}**!")
    if st.sidebar.button("Sair"):
        st.session_state.authenticated = False
        st.query_params.clear()
        st.rerun()

    # O RESTANTE DO SEU CÓDIGO (ETAPAS 1, 2 e 3) CONTINUA AQUI...
    st.write("---")
    st.info(f"Olá {st.session_state.usuario_nome}, vamos começar a avaliação?")
    # (Inserir aqui a lógica de etapas que corrigimos anteriormente)
