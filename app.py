import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Passo Seguro", page_icon="👣", layout="centered")

# --- SISTEMA DE LOGIN ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.markdown("<h1 style='text-align: center; color: #007bff;'>🔐 Acesso ao Sistema</h1>", unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div style="padding: 20px; border-radius: 15px; background-color: #ffffff; border: 1px solid #ddd;">', unsafe_allow_html=True)
            
            usuario = st.selectbox("Selecione o Avaliador:", [
                "Avaliador 01", 
                "Avaliador 02", 
                "Coordenador do Projeto",
                "Outro"
            ])
            
            senha = st.text_input("Senha de Acesso:", type="password")
            
            if st.button("ENTRAR"):
                if senha == "passo2026": 
                    st.session_state.authenticated = True
                    st.session_state.avaliador = usuario
                    st.rerun()
                else:
                    st.error("Senha incorreta.")
            st.markdown('</div>', unsafe_allow_html=True)
        return False
    return True

if check_password():
    # Estilo Visual Passo Seguro
    st.markdown("""
        <style>
        .stButton>button { width: 100%; border-radius: 10px; background-color: #007bff; color: white; font-weight: bold; height: 3em; }
        .card { padding: 20px; border-radius: 15px; background-color: #ffffff; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; border-left: 5px solid #007bff; }
        </style>
        """, unsafe_allow_html=True)

    conn = st.connection("gsheets", type=GSheetsConnection)

    if 'etapa' not in st.session_state:
        st.session_state.etapa = 1
    if 'dados' not in st.session_state:
        st.session_state.dados = {}

    # --- TELA 1: IDENTIFICAÇÃO DO PACIENTE ---
    if st.session_state.etapa == 1:
        st.markdown(f"<p style='text-align: right; color: gray;'>👤 Avaliador: {st.session_state.avaliador}</p>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; color: #007bff;'>👣 Passo Seguro</h1>", unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="card"><h3>👤 Dados de Identificação</h3>', unsafe_allow_html=True)
            nome = st.text_input("Nome Completo do Paciente")
            
            col_nasc, col_sexo = st.columns(2)
            with col_nasc:
                nasc = st.date_input("Data de Nascimento", min_value=datetime(1920, 1, 1), format="DD/MM/YYYY")
            with col_sexo:
                sexo = st.selectbox("Sexo", ["Masculino", "Feminino", "Outro"])
            
            col_cid, col_est = st.columns([3, 1])
            with col_cid:
                cidade = st.text_input("Cidade")
            with col_est:
                # Foco no Piauí e estados adjacentes
                estado = st.selectbox("UF", ["PI", "MA", "CE", "PE", "BA", "TO", "Outros"], index=0)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("AVANÇAR PARA AVALIAÇÃO ➡"):
            if nome and cidade:
                st.session_state.dados.update({
                    "Avaliador": st.session_state.avaliador,
                    "Nome": nome, 
                    "Data Nasc.": nasc.strftime('%d/%m/%Y'),
                    "Idade": datetime.now().year - nasc.year, 
                    "Sexo": sexo, 
                    "Cidade": cidade,
                    "Estado": estado
                })
                st.session_state.etapa = 2
                st.rerun()
            else:
                st.warning("Os campos Nome e Cidade são obrigatórios.")

    # --- TELA 2: AVALIAÇÃO CLÍNICA DOS PÉS ---
    elif st.session_state.etapa == 2:
        st.markdown("<h2>🩺 Avaliação Clínica e Risco</h2>", unsafe_allow_html=True)
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            tempo = st.text_input("Tempo de Diabetes (anos)")
            calo = st.radio("Presença de calosidade nos pés?", ["Não", "Sim"])
            ulcera = st.radio("Possui úlcera (ferida) ativa?", ["Não", "Sim"])
            amp = st.radio("Já sofreu alguma amputação?", ["Não", "Sim"])
            local = st.text_area("Descreva a localização das lesões ou amputações")
            st.markdown('</div>', unsafe_allow_html=True)

        if st.button("FINALIZAR REGISTRO ✔"):
            st.session_state.dados.update({
                "Tempo Diabetes": tempo, 
                "Calosidade": calo, 
                "Úlcera": ulcera, 
                "Amputação": amp, 
                "Localização": local
            })
            
            try:
                # Garante que os dados sejam acrescentados sem apagar os anteriores
                df_existente = conn.read()
                novo_registro = pd.DataFrame([st.session_state.dados])
                df_final = pd.concat([df_existente, novo_registro], ignore_index=True)
                
                conn.update(data=df_final)
                st.balloons()
                st.session_state.etapa = 3
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao salvar na planilha: {e}")

    # --- TELA 3: CONCLUSÃO ---
    elif st.session_state.etapa == 3:
        st.success("✅ Atendimento registrado com sucesso no banco de dados!")
        
        st.markdown("""
        ### Recomendações de Segurança:
        * Verifique se os calçados do paciente são adequados.
        * Reforce a necessidade de hidratação e inspeção diária.
        """)
        
        if st.button("NOVO PACIENTE 🔄"):
            st.session_state.etapa = 1
            st.session_state.dados = {}
            st.rerun()
            
        if st.button("ENCERRAR SESSÃO"):
            st.session_state.authenticated = False
            st.rerun()
