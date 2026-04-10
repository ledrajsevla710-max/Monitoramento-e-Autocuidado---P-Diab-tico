import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Passo Seguro", page_icon="👣", layout="centered")

# Estilo CSS para interface moderna (baseada nos seus slides)
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
        font-weight: bold;
    }
    .card {
        padding: 20px;
        border-radius: 15px;
        background-color: #ffffff;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        border-left: 5px solid #007bff;
    }
    h1, h2, h3 {
        color: #007bff;
    }
    </style>
    """, unsafe_allow_html=True)

# Conexão com o Google Sheets
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error("Erro na conexão com as Secrets. Verifique o painel do Streamlit.")

# Gerenciamento de Etapas do Formulário
if 'etapa' not in st.session_state:
    st.session_state.etapa = 1
if 'dados' not in st.session_state:
    st.session_state.dados = {}

# --- TELA 1: PERFIL ---
if st.session_state.etapa == 1:
    st.markdown("<h1 style='text-align: center;'>👣 Passo Seguro</h1>", unsafe_allow_html=True)
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
            # Ajustado para bater com o "Data Nasc." da sua planilha (com ponto)
            st.session_state.dados.update({
                "Nome": nome, 
                "Data Nasc.": nasc.strftime('%d/%m/%Y'), 
                "Idade": idade, 
                "Sexo": sexo, 
                "Cidade": cidade
            })
            st.session_state.etapa = 2
            st.rerun()
        else:
            st.warning("Por favor, preencha o nome e a cidade.")

# --- TELA 2: AVALIAÇÃO CLÍNICA ---
elif st.session_state.etapa == 2:
    st.markdown("<h2>🩺 Avaliação de Risco</h2>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        tempo = st.text_input("Há quanto tempo tem Diabetes? (anos)")
        calo = st.radio("Possui calosidade nos pés?", ["Não", "Sim"])
        ulcera = st.radio("Possui úlcera (ferida) ativa?", ["Não", "Sim"])
        amp = st.radio("Já passou por alguma amputação?", ["Não", "Sim"])
        local = st.text_area("Se houver ferida ou amputação, descreva o local")
        st.markdown('</div>', unsafe_allow_html=True)

    if st.button("SALVAR E VER ORIENTAÇÕES ✔"):
        # Ajustado para bater com os nomes exatos das colunas da sua planilha (com acentos)
        st.session_state.dados.update({
            "Tempo Diabetes": tempo, 
            "Calosidade": calo, 
            "Úlcera": ulcera, 
            "Amputação": amp, 
            "Localização": local
        })
        
        try:
            # Tenta ler os dados existentes
            df_antigo = conn.read()
            # Cria o novo registro
            novo_df = pd.DataFrame([st.session_state.dados])
            # Une e faz o update na planilha
            df_final = pd.concat([df_antigo, novo_df], ignore_index=True)
            conn.update(data=df_final)
            
            st.balloons()
            st.session_state.etapa = 3
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao salvar: {e}")
            st.info("Verifique se a conta de serviço tem permissão de EDITOR na planilha.")

# --- TELA 3: ORIENTAÇÕES ---
elif st.session_state.etapa == 3:
    st.markdown("<h2 style='color: #28a745;'>💡 Orientações de Autocuidado</h2>", unsafe_allow_html=True)
    
    st.success("✅ Os dados foram salvos com sucesso no banco de dados do PPGBiotec!")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("**🔍 Inspeção Diária**\nUse um espelho para olhar a sola dos pés todos os dias em busca de cortes ou vermelhidão.")
    with col2:
        st.info("**🧴 Hidratação**\nPasse creme hidratante em todo o pé, mas evite passar entre os dedos para não criar fungos.")
        
    st.warning("**👟 Calçados**\nNunca ande descalço, mesmo dentro de casa. Antes de calçar o sapato, verifique se não há pedrinhas dentro.")

    if st.button("NOVO ATENDIMENTO 🔄"):
        st.session_state.etapa = 1
        st.session_state.dados = {}
        st.rerun()
