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
            
            iif st.button("ACESSAR SISTEMA"):
                try:
                    # ttl=0 obriga a ler o cadastro novo na hora!
                    df_users = conn.read(worksheet="usuarios", ttl=0)
                    
                    # Limpa o email digitado (tira espaços e põe minúsculo)
                    email_alvo = email_login.strip().lower()
                    
                    # COMPARAÇÃO BLINDADA: limpa a planilha e o que foi digitado
                    user_match = df_users[
                        (df_users['email'].str.strip().str.lower() == email_alvo) & 
                        (df_users['senha'].astype(str).str.strip() == senha_login.strip())
                    ]
                    
                    if not user_match.empty:
                        st.session_state.authenticated = True
                        st.session_state.usuario_nome = user_match.iloc[0]['nome']
                        st.rerun()
                    else:
                        st.error("E-mail ou senha não encontrados.")
                except Exception as e:
                    st.error(f"Erro ao acessar base: {e}")
            if st.button("FINALIZAR CADASTRO"):
                if n_nome and n_email and n_senha:
                    try:
                        try:
                            df_users = conn.read(worksheet="usuarios", ttl=0)
                        except:
                            df_users = pd.DataFrame(columns=["nome", "email", "senha"])

                        if not df_users.empty and n_email.strip().lower() in df_users['email'].str.strip().str.lower().values:
                            st.error("Este e-mail já está cadastrado.")
                        else:
                            novo_u = pd.DataFrame([{"nome": n_nome.strip(), "email": n_email.strip().lower(), "senha": n_senha.strip()}])
                            df_atualizado = pd.concat([df_users, novo_u], ignore_index=True)
                            conn.update(worksheet="usuarios", data=df_atualizado)
                            st.success("Cadastro realizado com sucesso! Vá para a aba 'Entrar'.")
                    except Exception as e:
                        st.error(f"Erro ao salvar cadastro: {e}")
                else:
                    st.warning("Preencha todos os campos.")
        return False
    return True

# --- INÍCIO DO FORMULÁRIO (APÓS LOGIN) ---
if auth_system():
    # Estilo CSS
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
        """, unsafe_allow_html=True)

    # Inicialização de variáveis de sessão para as etapas
    if 'etapa' not in st.session_state:
        st.session_state.etapa = 1
    if 'dados' not in st.session_state:
        st.session_state.dados = {}

    st.sidebar.write(f"👤 Logado como: **{st.session_state.usuario_nome}**")
    if st.sidebar.button("Sair"):
        st.session_state.authenticated = False
        st.rerun()

    # --- ETAPA 1: DADOS DO PACIENTE ---
    if st.session_state.etapa == 1:
        st.markdown("<h2 style='text-align: center;'>👤 Identificação do Paciente</h2>", unsafe_allow_html=True)
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            nome_p = st.text_input("Nome do Paciente")
            col1, col2 = st.columns(2)
            with col1:
                nasc = st.date_input("Data de Nascimento", min_value=datetime(1920, 1, 1), format="DD/MM/YYYY")
            with col2:
                sexo = st.selectbox("Sexo", ["Masculino", "Feminino", "Outro"])
            cidade = st.text_input("Cidade", value="José de Freitas")
            st.markdown('</div>', unsafe_allow_html=True)

        if st.button("PRÓXIMO ➡"):
            if nome_p:
                st.session_state.dados.update({
                    "Data/Hora": datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                    "Nome": nome_p,
                    "Data Nasc.": nasc.strftime('%d/%m/%Y'),
                    "Idade": datetime.now().year - nasc.year,
                    "Sexo": sexo,
                    "Cidade": cidade
                })
                st.session_state.etapa = 2
                st.rerun()
            else:
                st.warning("Preencha o nome do paciente.")

    # --- ETAPA 2: AVALIAÇÃO CLÍNICA ---
    elif st.session_state.etapa == 2:
        st.markdown("<h2 style='text-align: center;'>🩺 Avaliação Clínica</h2>", unsafe_allow_html=True)
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            tempo = st.text_input("Tempo de Diabetes (anos)")
            calo = st.radio("Possui calosidade?", ["Não", "Sim"])
            ulcera = st.radio("Possui úlcera ativa?", ["Não", "Sim"])
            amp = st.radio("Histórico de amputação?", ["Não", "Sim"])
            local = st.text_area("Observações")
            st.markdown('</div>', unsafe_allow_html=True)

        if st.button("FINALIZAR E SALVAR ✔"):
            st.session_state.dados.update({
                "Tempo Diabetes": tempo,
                "Calosidade": calo,
                "Úlcera": ulcera,
                "Amputação": amp,
                "Localização": local,
                "Avaliador": st.session_state.usuario_nome
            })
            
            try:
                df_existente = conn.read()
                novo_reg = pd.DataFrame([st.session_state.dados])
                df_final = pd.concat([df_existente, novo_reg], ignore_index=True)
                conn.update(data=df_final)
                st.session_state.etapa = 3
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")

    # --- ETAPA 3: SUCESSO ---
    elif st.session_state.etapa == 3:
        st.balloons()
        st.success("✅ Dados registrados com sucesso!")
        if st.button("Novo Registro"):
            st.session_state.etapa = 1
            st.session_state.dados = {}
            st.rerun()
