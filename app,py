import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Passo Seguro - PPGBiotec", page_icon="👣")

# --- ESTILO VISUAL ---
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .card-orientacao {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        border-left: 6px solid #007bff;
        margin-bottom: 15px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    }
    .titulo-etapa { color: #0056b3; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZAÇÃO DE VARIÁVEIS DE ESTADO ---
if 'etapa' not in st.session_state:
    st.session_state.etapa = 1
if 'dados' not in st.session_state:
    st.session_state.dados = {}

# --- FUNÇÕES DE NAVEGAÇÃO ---
def proxima_etapa(): st.session_state.etapa += 1
def reiniciar(): st.session_state.etapa = 1

# --- ETAPA 1: PERFIL DO PACIENTE ---
if st.session_state.etapa == 1:
    st.title("👣 Passo Seguro")
    st.subheader("Cadastro de Perfil")
    
    with st.container():
        nome = st.text_input("Nome Completo")
        dt_nasc = st.date_input("Data de Nascimento", min_value=datetime(1920, 1, 1))
        idade = st.number_input("Idade Atual", min_value=0, max_value=120)
        sexo = st.selectbox("Sexo", ["Masculino", "Feminino", "Não informar"])
        cidade = st.text_input("Cidade")
        
        if st.button("Continuar ➡️", use_container_width=True):
            if nome and cidade:
                st.session_state.dados.update({"nome": nome, "cidade": cidade})
                proxima_etapa()
                st.rerun()
            else:
                st.warning("Preencha o nome e a cidade para prosseguir.")

# --- ETAPA 2: QUESTIONÁRIO DE RISCO ---
elif st.session_state.etapa == 2:
    st.markdown("<h2 class='titulo-etapa'>🩺 Avaliação de Saúde</h2>", unsafe_allow_html=True)
    
    tempo_diabetes = st.text_input("Possui diabetes há quanto tempo?")
    
    st.divider()
    st.write("**Histórico de Calos e Úlceras**")
    
    # Campo para Calosidade
    tem_calo = st.radio("Já teve ou possui calosidade?", ["Sim", "Não"])
    if tem_calo == "Sim":
        st.text_input("Qual o local da calosidade?")
        
    # Campo para Úlcera
    tem_ulcera = st.radio("Já teve ou possui ferida (úlcera) nos pés?", ["Sim", "Não"])
    if tem_ulcera == "Sim":
        st.text_input("Qual o local da ferida?")

    st.divider()
    # Campo para Amputação
    tem_amp = st.radio("Já passou por alguma amputação?", ["Sim", "Não"])
    if tem_amp == "Sim":
        st.info("Utilize a imagem abaixo como referência para indicar o local:")
        st.image("https://cdn-icons-png.flaticon.com/512/2865/2865913.png", width=100) # Placeholder para mapa do pé
        st.multiselect("Marque a região:", ["Hálux (Dedão)", "Dedos", "Meio do Pé", "Calcanhar", "Membro Inferior"])

    if st.button("Finalizar e Ver Recomendações ✨", use_container_width=True):
        proxima_etapa()
        st.rerun()

# --- ETAPA 3: ORIENTAÇÕES (FLASHCARDS) ---
elif st.session_state.etapa == 3:
    st.success(f"Avaliação concluída para: {st.session_state.dados.get('nome')}")
    st.title("💡 Autocuidado Diário")
    
    # Flashcard 1
    st.markdown("""
        <div class="card-orientacao">
            <h4>🔍 Inspeção Diária</h4>
            <p>Observe seus pés todos os dias. Use um espelho para ver a sola. Procure por cortes, bolhas ou vermelhidão.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Flashcard 2
    st.markdown("""
        <div class="card-orientacao">
            <h4>🧴 Hidratação</h4>
            <p>Aplique hidratante para evitar rachaduras, mas <b>NUNCA</b> passe entre os dedos.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Flashcard 3
    st.markdown("""
        <div class="card-orientacao">
            <h4>👟 Calçados</h4>
            <p>Use calçados macios e fechados. Evite andar descalço, mesmo em casa.</p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("Novo Atendimento 🔄", use_container_width=True):
        reiniciar()
        st.rerun()
