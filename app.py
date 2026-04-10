import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Passo Seguro", page_icon="👣", layout="centered")

# Estilo CSS para parecer com a interface que você enviou
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #007bff;
        color: white;
    }
    .card {
        padding: 20px;
        border-radius: 15px;
        background-color: #ffffff;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        border-left: 5px solid #007bff;
    }
    </style>
    """, unsafe_allow_html=True)

# Conexão com o Google Sheets
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error("Erro na conexão com as Secrets. Verifique o painel do Streamlit.")

# Gerenciamento de Etapas
if 'etapa' not in st.session_state:
    st.session_state.etapa = 1
if 'dados' not in st.session_state:
    st.session_state.dados = {}

# --- TELA 1: PERFIL (Interface Azulada) ---
if st.session_state.etapa == 1:
    st.markdown("<h1 style='text-align: center; color: #007bff;'>👣 Passo Seguro</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Monitoramento e Autocuidado do Pé Diabético</p>", unsafe_allow_html=True)
    
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
        if nome and cidade:
            idade = datetime.now().year - nasc.year
            st.session_state.dados.update({
                "Nome": nome, "Data Nasc": nasc.strftime('%d/%m/%Y'), 
                "Idade": idade, "Sexo": sexo, "Cidade": cidade
            })
            st.session_state.etapa = 2
            st.rerun()
        else:
            st.warning("Por favor, preencha o nome e a cidade.")

# --- TELA 2: AVALIAÇÃO CLÍNICA ---
elif st.session_state.etapa == 2:
    st.markdown("<h2 style='color: #007bff;'>🩺 Avaliação de Risco</h2>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        tempo = st.text_input("Há quanto tempo tem Diabetes? (anos)")
        calo = st.radio("Possui calosidade nos pés?", ["Não", "Sim"])
        ulcera = st.radio("Possui úlcera (ferida) ativa?", ["Não", "Sim"])
        amp = st.radio("Já passou por alguma amputação?", ["Não", "Sim"])
        local = st.text_area("Se houver ferida ou amputação, descreva o local (Ex: Dedo maior pé direito)")
        st.markdown('</div>', unsafe_allow_html=True)

    if st.button("SALVAR E VER ORIENTAÇÕES ✔"):
        st.session_state.dados.update({
            "Tempo Diabetes": tempo, "Calosidade": calo, 
            "Ulcera": ulcera, "Amputacao": amp, "Localizacao": local
        })
        
        # Lógica de Salvar no Google Sheets
        try:
            df_antigo = conn.read()
            novo_df = pd.DataFrame([st.session_state.dados])
            df_final = pd.concat([df_antigo, novo_df], ignore_index=True)
            conn.update(data=df_final)
            st.balloons()
            st.session_state.etapa = 3
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao salvar: {e}")

# --- TELA 3: ORIENTAÇÕES (Flashcards) ---
elif st.session_state.etapa == 3:
    st.markdown("<h2 style='color: #28a745;'>💡 Orientações de Autocuidado</h2>", unsafe_allow_html=True)
    
    st.success("✅ Dados salvos com sucesso na planilha do projeto!")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("**🔍 Inspeção Diária**\nUse um espelho para olhar a sola dos pés todos os dias.")
    with col2:
        st.info("**🧴 Hidratação**\nPasse creme no pé todo, mas NUNCA entre os dedos.")
        
    st.warning("**👟 Calçados**\nNunca ande descalço, nem dentro de casa. Use calçados macios.")

    if st.button("NOVO ATENDIMENTO 🔄"):
        st.session_state.etapa = 1
        st.session_state.dados = {}
        st.rerun()
