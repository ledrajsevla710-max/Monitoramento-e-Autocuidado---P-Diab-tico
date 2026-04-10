import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Passo Seguro", page_icon="👣", layout="centered")

# --- SISTEMA DE LOGIN SIMPLES ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.markdown("<h1 style='text-align: center;'>🔐 Acesso Restrito</h1>", unsafe_allow_html=True)
        senha = st.text_input("Digite a senha do projeto:", type="password")
        if st.button("Entrar"):
            if senha == "biotec2026": # VOCÊ PODE MUDAR A SENHA AQUI
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Senha incorreta")
        return False
    return True

if check_password():
    # Estilo CSS
    st.markdown("""
        <style>
        .stButton>button { width: 100%; border-radius: 10px; background-color: #007bff; color: white; font-weight: bold; }
        .card { padding: 20px; border-radius: 15px; background-color: #ffffff; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; border-left: 5px solid #007bff; }
        </style>
        """, unsafe_allow_html=True)

    # Conexão
    conn = st.connection("gsheets", type=GSheetsConnection)

    if 'etapa' not in st.session_state:
        st.session_state.etapa = 1
    if 'dados' not in st.session_state:
        st.session_state.dados = {}

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
            cidade = st.text_input("Cidade", value="José de Freitas")
            st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("PRÓXIMO ➡"):
            if nome:
                st.session_state.dados.update({
                    "Nome": nome, "Data Nasc.": nasc.strftime('%d/%m/%Y'),
                    "Idade": datetime.now().year - nasc.year, "Sexo": sexo, "Cidade": cidade
                })
                st.session_state.etapa = 2
                st.rerun()

    # --- TELA 2: AVALIAÇÃO ---
    elif st.session_state.etapa == 2:
        st.markdown("<h2>🩺 Avaliação de Risco</h2>", unsafe_allow_html=True)
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            tempo = st.text_input("Tempo de Diabetes")
            calo = st.radio("Calosidade?", ["Não", "Sim"])
            ulcera = st.radio("Úlcera ativa?", ["Não", "Sim"])
            amp = st.radio("Amputação?", ["Não", "Sim"])
            local = st.text_area("Localização")
            st.markdown('</div>', unsafe_allow_html=True)

        if st.button("SALVAR DADOS ✔"):
            st.session_state.dados.update({
                "Tempo Diabetes": tempo, "Calosidade": calo, 
                "Úlcera": ulcera, "Amputação": amp, "Localização": local
            })
            
            try:
                # --- AQUI ESTÁ O SEGREDO PARA NÃO SOBRESCREVER ---
                # 1. Lê os dados que já estão lá
                df_existente = conn.read()
                
                # 2. Cria o novo dado
                novo_registro = pd.DataFrame([st.session_state.dados])
                
                # 3. Junta o antigo com o novo (Coloca na linha de baixo)
                df_final = pd.concat([df_existente, novo_registro], ignore_index=True)
                
                # 4. Atualiza a planilha inteira com a lista nova
                conn.update(data=df_final)
                
                st.balloons()
                st.session_state.etapa = 3
                st.rerun()
            except Exception as e:
                st.error(f"Erro: {e}")

    # --- TELA 3: FINALIZAÇÃO ---
    elif st.session_state.etapa == 3:
        st.success("✅ Dados salvos na planilha!")
        if st.button("NOVO ATENDIMENTO 🔄"):
            st.session_state.etapa = 1
            st.session_state.dados = {}
            st.rerun()
        if st.button("SAIR (LOGOUT)"):
            st.session_state.authenticated = False
            st.rerun()
