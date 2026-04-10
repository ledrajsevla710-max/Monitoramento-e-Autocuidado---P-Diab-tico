import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Passo Seguro", page_icon="👣", layout="wide")

# --- CONEXÃO COM GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

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
                    df_users = conn.read(worksheet="usuarios", ttl=0)
                    df_users.columns = [str(c).strip().lower() for c in df_users.columns]
                    email_digitado = email_login.strip().lower()
                    senha_digitada = str(senha_login).strip()
                    
                    def limpar_v(v):
                        v = str(v).strip()
                        return v[:-2] if v.endswith('.0') else v

                    df_users['email_c'] = df_users['email'].astype(str).str.strip().str.lower()
                    df_users['senha_c'] = df_users['senha'].apply(limpar_v)
                    
                    user_match = df_users[(df_users['email_c'] == email_digitado) & (df_users['senha_c'] == senha_digitada)]
                    
                    if not user_match.empty:
                        st.session_state.authenticated = True
                        col_nome = [c for c in df_users.columns if 'nome' in c][0]
                        st.session_state.usuario_nome = user_match.iloc[0][col_nome]
                        st.rerun()
                    else:
                        st.error("Dados incorretos.")
                except Exception as e:
                    st.error(f"Erro: {e}")
        return False
    return True

if auth_system():
    # CSS Customizado
    st.markdown("""
        <style>
        .stButton>button { width: 100%; border-radius: 10px; background-color: #007bff; color: white; font-weight: bold; }
        .card { padding: 20px; border-radius: 15px; background-color: #ffffff; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; border-left: 5px solid #007bff; color: black; }
        .flashcard { padding: 20px; border-radius: 15px; background-color: #e3f2fd; border: 1px solid #90caf9; text-align: center; margin-bottom: 10px; min-height: 150px; display: flex; align-items: center; justify-content: center; font-weight: bold; color: #0d47a1; }
        .alerta-card { padding: 15px; border-radius: 10px; background-color: #fff3cd; border-left: 5px solid #ffc107; color: #856404; margin-top: 10px; font-weight: bold; }
        .lembrete-pes { background-color: #ffeb3b; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold; color: black; margin-bottom: 20px; border: 2px dashed #f44336; }
        </style>
        """, unsafe_allow_html=True)

    if 'etapa' not in st.session_state: st.session_state.etapa = 1
    if 'dados_paciente' not in st.session_state: st.session_state.dados_paciente = {}

    # --- BARRA LATERAL (HISTÓRICO E CONSULTA) ---
    st.sidebar.markdown(f"### 👤 {st.session_state.usuario_nome}")
    
    with st.sidebar.expander("📊 Consultar Dados Salvos"):
        try:
            df_historico = conn.read(ttl=0)
            st.dataframe(df_historico, use_container_width=True)
        except:
            st.write("Nenhum dado encontrado ainda.")

    if st.sidebar.button("Sair do Sistema"):
        st.session_state.authenticated = False
        st.rerun()

    # --- LEMBRETE FIXO ---
    st.markdown('<div class="lembrete-pes">🔔 LEMBRETE DIÁRIO: Já olhou seus pés hoje? Verifique feridas, bolhas ou manchas!</div>', unsafe_allow_html=True)

    # --- ETAPA 1: PERFIL DO PACIENTE ---
    if st.session_state.etapa == 1:
        st.markdown("<h2 style='text-align: center;'>👤 Perfil do Paciente</h2>", unsafe_allow_html=True)
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            nome_p = st.text_input("Nome Completo")
            col1, col2 = st.columns(2)
            with col1:
                nasc = st.date_input("Data de Nascimento", min_value=datetime(1920,1,1), format="DD/MM/YYYY")
            with col2:
                sexo = st.selectbox("Sexo", ["Masculino", "Feminino", "Outro"])
            
            col_cid, col_uf = st.columns([3, 1])
            with col_cid:
                cidade = st.text_input("Cidade", value="") 
            with col_uf:
                lista_uf = ["", "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"]
                uf = st.selectbox("UF", options=lista_uf)
            st.markdown('</div>', unsafe_allow_html=True)

        if st.button("AVANÇAR PARA AVALIAÇÃO ➡"):
            if nome_p and uf != "":
                idade = datetime.now().year - nasc.year
                st.session_state.dados_paciente = {
                    "Nome": nome_p, "Nasc": nasc.strftime('%d/%m/%Y'), "Idade": idade,
                    "Sexo": sexo, "Cidade": cidade, "UF": uf
                }
                st.session_state.etapa = 2
                st.rerun()
            else:
                st.warning("Preencha o nome e selecione a UF.")

    # --- ETAPA 2: AVALIAÇÃO E FLASHCARDS ---
    elif st.session_state.etapa == 2:
        p = st.session_state.dados_paciente
        st.markdown(f"### 🩺 Avaliação Clínica: {p['Nome']}")
        
        col_form, col_flash = st.columns([2, 1])

        with col_form:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            tempo = st.text_input("Possui diabetes há quanto tempo? (anos)")
            calo = st.radio("Já teve ou possui calosidade?", ["Não", "Sim"])
            ulcera = st.radio("Tem ou já teve úlcera nos pés?", ["Não", "Sim"])
            amp = st.radio("Já passou por amputação?", ["Não", "Sim"])
            local = st.text_area("Se sim, qual o local da ferida ou amputação?")
            st.markdown('</div>', unsafe_allow_html=True)

            bloqueio_critico = False
            if ulcera == "Sim" or calo == "Sim":
                st.markdown('<div class="alerta-card">⚠️ NOTIFICAÇÃO: Nova alteração detectada! Procure um enfermeiro ou médico para avaliação do pé diabético.</div>', unsafe_allow_html=True)
                confirmou = st.checkbox("Confirmo que recebi orientação sobre a alteração.")
                if not confirmou: bloqueio_critico = True

        with col_flash:
            st.markdown("### 💡 Orientações")
            st.markdown('<div class="flashcard">👀 Olhe seus pés todos os dias em busca de cortes ou vermelhidão.</div>', unsafe_allow_html=True)
            st.markdown('<div class="flashcard">🧴 Use hidratante diariamente, mas NUNCA passe entre os dedos.</div>', unsafe_allow_html=True)
            st.markdown('<div class="flashcard">👟 Use sempre calçados adequados e fechados. Nunca ande descalço.</div>', unsafe_allow_html=True)

        if st.button("SALVAR REGISTRO ✔"):
            if bloqueio_critico:
                st.error("Por favor, confirme que recebeu a orientação antes de salvar.")
            else:
                registro_final = {
                    "Data/Hora": datetime.now().strftime('%d/%m/%Y %H:%M'),
                    **st.session_state.dados_paciente,
                    "Tempo Diabetes": tempo, "Calo": calo, "Ulcera": ulcera, 
                    "Amputação": amp, "Local/Obs": local,
                    "Avaliador": st.session_state.usuario_nome
                }
                try:
                    df_atual = conn.read()
                    df_novo = pd.concat([df_atual, pd.DataFrame([registro_final])], ignore_index=True)
                    conn.update(data=df_novo)
                    st.session_state.etapa = 3
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao salvar: {e}")

    # --- ETAPA 3: SUCESSO ---
    elif st.session_state.etapa == 3:
        st.balloons()
        st.success("✅ Os dados foram armazenados com sucesso!")
        if st.button("Nova Avaliação"):
            st.session_state.etapa = 1
            st.session_state.dados_paciente = {}
            st.rerun()
