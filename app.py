import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Passo Seguro", page_icon="👣", layout="centered")

# --- SISTEMA DE ACESSO PARA O USUÁRIO (PACIENTE) ---
def check_password():
    # Verifica se o usuário já validou o acesso anteriormente
    if "auth_user" in st.query_params and st.query_params["auth_user"] == "liberado":
        st.session_state.authenticated = True
        return True

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.markdown("<h1 style='text-align: center; color: #007bff;'>👣 Bem-vindo ao Passo Seguro</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>Por favor, insira a senha de acesso para iniciar sua avaliação.</p>", unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div style="padding: 20px; border-radius: 15px; background-color: #ffffff; border: 1px solid #ddd;">', unsafe_allow_html=True)
            
            senha = st.text_input("Senha de Acesso:", type="password")
            manter_conectado = st.checkbox("Manter conectado neste dispositivo")
            
            if st.button("INICIAR AVALIAÇÃO"):
                if senha == "biotec2026":
                    st.session_state.authenticated = True
                    
                    if manter_conectado:
                        st.query_params["auth_user"] = "liberado"
                    st.rerun()
                else:
                    st.error("Senha incorreta. Peça ajuda ao avaliador se necessário.")
            st.markdown('</div>', unsafe_allow_html=True)
        return False
    return True

if check_password():
    # Estilo Visual
    st.markdown("""
        <style>
        .stButton>button { width: 100%; border-radius: 10px; background-color: #007bff; color: white; font-weight: bold; height: 3em; }
        .card { padding: 20px; border-radius: 15px; background-color: #ffffff; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; border-left: 5px solid #007bff; color: black; }
        </style>
        """, unsafe_allow_html=True)

    conn = st.connection("gsheets", type=GSheetsConnection)

    if 'etapa' not in st.session_state:
        st.session_state.etapa = 1
    if 'dados' not in st.session_state:
        st.session_state.dados = {}

    # --- TELA 1: IDENTIFICAÇÃO ---
    if st.session_state.etapa == 1:
        st.markdown("<h1 style='text-align: center; color: #007bff;'>👣 Passo Seguro</h1>", unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="card"><h3>👤 Suas Informações</h3>', unsafe_allow_html=True)
            nome = st.text_input("Seu Nome Completo")
            
            col_nasc, col_sexo = st.columns(2)
            with col_nasc:
                nasc = st.date_input("Data de Nascimento", min_value=datetime(1920, 1, 1), format="DD/MM/YYYY")
            with col_sexo:
                sexo = st.selectbox("Sexo", ["Masculino", "Feminino", "Outro"])
            
            col_cid, col_uf = st.columns([3, 1])
            with col_cid:
                cidade = st.text_input("Cidade", value="José de Freitas")
            with col_uf:
                # Adicionado campo UF que faltava
                uf = st.selectbox("UF", ["PI", "MA", "CE", "PE", "BA", "TO", "Outros"], index=0)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("PRÓXIMO ➡"):
            if nome:
                st.session_state.dados.update({
                    "Data/Hora": datetime.now().strftime('%d/%m/%Y %H:%M'),
                    "Nome": nome, 
                    "Data Nasc.": nasc.strftime('%d/%m/%Y'),
                    "Idade": datetime.now().year - nasc.year, 
                    "Sexo": sexo, 
                    "Cidade": cidade,
                    "UF": uf
                })
                st.session_state.etapa = 2
                st.rerun()
            else:
                st.warning("Por favor, digite seu nome.")

    # --- TELA 2: DADOS CLÍNICOS ---
    elif st.session_state.etapa == 2:
        st.markdown("<h2>🩺 Sua Avaliação</h2>", unsafe_allow_html=True)
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            tempo = st.text_input("Há quantos anos você tem Diabetes?")
            calo = st.radio("Você possui calos nos pés?", ["Não", "Sim"])
            ulcera = st.radio("Você possui alguma ferida aberta atualmente?", ["Não", "Sim"])
            amp = st.radio("Já precisou realizar alguma amputação?", ["Não", "Sim"])
            local = st.text_area("Se sim, descreva o local ou deixe uma observação:")
            st.markdown('</div>', unsafe_allow_html=True)

        if st.button("FINALIZAR E ENVIAR ✔"):
            st.session_state.dados.update({
                "Tempo Diabetes": tempo, 
                "Calosidade": calo, 
                "Úlcera": ulcera, 
                "Amputação": amp, 
                "Localização": local
            })
            
            try:
                # Tenta ler e concatenar
                try:
                    df_existente = conn.read()
                except:
                    df_existente = pd.DataFrame()

                novo_registro = pd.DataFrame([st.session_state.dados])
                df_final = pd.concat([df_existente, novo_registro], ignore_index=True)
                
                conn.update(data=df_final)
                st.balloons()
                st.session_state.etapa = 3
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")

    # --- TELA 3: CONCLUSÃO ---
    elif st.session_state.etapa == 3:
        st.success("✅ Suas informações foram enviadas com sucesso! Obrigado.")
        
        if st.button("REALIZAR NOVO REGISTRO 🔄"):
            st.session_state.etapa = 1
            st.session_state.dados = {}
            st.rerun()

        if st.button("SAIR"):
            st.session_state.authenticated = False
            st.query_params.clear()
            st.rerun()
