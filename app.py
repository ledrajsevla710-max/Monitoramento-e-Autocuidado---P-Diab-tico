import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Passo Seguro", page_icon="👣", layout="centered")

# --- SISTEMA DE LOGIN COM PERSISTÊNCIA ---
def check_password():
    # 1. Verifica se já existe um login salvo na URL (Manter Conectado)
    if "auth" in st.query_params and st.query_params["auth"] == "confirmado":
        st.session_state.authenticated = True
        if "avaliador_nome" not in st.session_state:
            st.session_state.avaliador_nome = st.query_params.get("user", "Avaliador")
        return True

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.markdown("<h1 style='text-align: center;'>🔐 Acesso ao Sistema</h1>", unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div style="padding: 20px; border-radius: 15px; background-color: #f8f9fa; border: 1px solid #ddd;">', unsafe_allow_html=True)
            
            # Seleção de usuário salvo/avaliador
            usuario = st.selectbox("Selecione o Avaliador:", [
                "Avaliador 01", 
                "Avaliador 02", 
                "Coordenador",
                "Outro"
            ])
            
            senha = st.text_input("Digite a senha do projeto:", type="password")
            manter_logado = st.checkbox("Manter conectado neste dispositivo")
            
            if st.button("ENTRAR"):
                if senha == "biotec2026":
                    st.session_state.authenticated = True
                    st.session_state.avaliador_nome = usuario
                    
                    if manter_logado:
                        # Salva na URL para a próxima visita
                        st.query_params["auth"] = "confirmado"
                        st.query_params["user"] = usuario
                    
                    st.rerun()
                else:
                    st.error("Senha incorreta")
            st.markdown('</div>', unsafe_allow_html=True)
        return False
    return True

if check_password():
    # --- ESTILO CSS ---
    st.markdown("""
        <style>
        .stButton>button { width: 100%; border-radius: 10px; background-color: #007bff; color: white; font-weight: bold; }
        .card { padding: 20px; border-radius: 15px; background-color: #ffffff; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; border-left: 5px solid #007bff; }
        .user-badge { text-align: right; color: #666; font-size: 0.9em; margin-bottom: 10px; }
        </style>
        """, unsafe_allow_html=True)

    # Conexão GSheets
    conn = st.connection("gsheets", type=GSheetsConnection)

    if 'etapa' not in st.session_state:
        st.session_state.etapa = 1
    if 'dados' not in st.session_state:
        st.session_state.dados = {}

    # Exibe quem está logado
    st.markdown(f"<div class='user-badge'>👤 Conectado como: <b>{st.session_state.avaliador_nome}</b></div>", unsafe_allow_html=True)

   # --- TELA 1: PERFIL ---
    if st.session_state.etapa == 1:
        st.markdown("<h1 style='text-align: center;'>👣 Passo Seguro</h1>", unsafe_allow_html=True)
        with st.container():
            st.markdown('<div class="card"><h3>👤 Perfil do Paciente</h3>', unsafe_allow_html=True)
            nome = st.text_input("Nome Completo")
            
            col1, col2 = st.columns(2)
            with col1:
                nasc = st.date_input("Data de Nascimento", min_value=datetime(1920, 1, 1), format="DD/MM/YYYY")
            with col2:
                sexo = st.selectbox("Sexo", ["Masculino", "Feminino", "Outro"])
            
            col_cid, col_uf = st.columns([3, 1])
            with col_cid:
                cidade = st.text_input("Cidade", value="José de Freitas")
            with col_uf:
                # O ERRO ESTAVA NESTA LINHA ABAIXO
                uf = st.selectbox("UF", ["PI", "MA", "CE", "PE", "BA", "Outros"], index=0)
            
            st.markdown('</div>', unsafe_allow_html=True)
