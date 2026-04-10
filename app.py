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
                    
                    user_match = df_users[(df_users['email'] == email_digitado) & (df_users['senha'].astype(str) == senha_digitada)]
                    
                    if not user_match.empty:
                        st.session_state.authenticated = True
                        st.session_state.usuario_email = email_digitado
                        st.session_state.usuario_nome = user_match.iloc[0]['nome']
                        # Armazena os dados cadastrais para evitar repetir a Etapa 1
                        st.session_state.dados_paciente = {
                            "Nome": user_match.iloc[0]['nome'],
                            "Cidade": user_match.iloc[0].get('cidade', ""),
                            "UF": user_match.iloc[0].get('uf', ""),
                            "Sexo": user_match.iloc[0].get('sexo', "Outro")
                        }
                        # Se já tem os dados básicos, vai direto para a clínica (Etapa 2)
                        st.session_state.etapa = 2
                        st.rerun()
                    else:
                        st.error("Dados incorretos.")
                except Exception as e:
                    st.error(f"Erro ao conectar: {e}")
        return False
    return True

if auth_system():
    # CSS para posicionar o botão de editar no topo
    st.markdown("""
        <style>
        .stButton>button { width: 100%; border-radius: 10px; background-color: #007bff; color: white; font-weight: bold; }
        .card { padding: 20px; border-radius: 15px; background-color: #ffffff; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; border-left: 5px solid #007bff; color: black; }
        .flashcard { padding: 15px; border-radius: 15px; background-color: #e3f2fd; text-align: center; margin-bottom: 10px; font-weight: bold; color: #0d47a1; border: 1px solid #90caf9; }
        .lembrete-pes { background-color: #ffeb3b; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold; color: black; margin-bottom: 20px; border: 2px dashed #f44336; }
        </style>
        """, unsafe_allow_html=True)

    # BARRA SUPERIOR / LATERAL
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.usuario_nome}")
        if st.button("✏️ Editar Meus Dados (Endereço/Perfil)"):
            st.session_state.etapa = 1
            st.rerun()
        
        st.divider()
        if st.button("🚪 Sair"):
            st.session_state.authenticated = False
            st.rerun()

    # --- LEMBRETE FIXO ---
    st.markdown('<div class="lembrete-pes">🔔 LEMBRETE: Já examinou seus pés hoje? Procure por novas feridas ou calos!</div>', unsafe_allow_html=True)

    # --- ETAPA 1: EDIÇÃO DE DADOS (SÓ APARECE SE CLICAR EM EDITAR OU NO PRIMEIRO ACESSO) ---
    if st.session_state.etapa == 1:
        st.markdown("## 📝 Atualizar Dados Cadastrais")
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            nome_p = st.text_input("Nome Completo", value=st.session_state.dados_paciente.get("Nome", ""))
            col_cid, col_uf = st.columns([3, 1])
            with col_cid:
                cidade = st.text_input("Cidade", value=st.session_state.dados_paciente.get("Cidade", ""))
            with col_uf:
                lista_uf = ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"]
                idx_uf = lista_uf.index(st.session_state.dados_paciente.get("UF", "PI")) if st.session_state.dados_paciente.get("UF") in lista_uf else 17
                uf = st.selectbox("UF", options=lista_uf, index=idx_uf)
            st.markdown('</div>', unsafe_allow_html=True)
            
            if st.button("SALVAR E IR PARA AVALIAÇÃO ➡"):
                st.session_state.dados_paciente.update({"Nome": nome_p, "Cidade": cidade, "UF": uf})
                st.session_state.etapa = 2
                st.rerun()

    # --- ETAPA 2: AVALIAÇÃO CLÍNICA (FOCO TOTAL AQUI) ---
    elif st.session_state.etapa == 2:
        st.markdown(f"### 🩺 Nova Avaliação Clínica")
        st.info(f"Paciente: {st.session_state.dados_paciente['Nome']} | Local: {st.session_state.dados_paciente['Cidade']}-{st.session_state.dados_paciente['UF']}")
        
        col_form, col_orienta = st.columns([2, 1])

        with col_form:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            tempo = st.text_input("Tempo de Diabetes (anos)")
            calo = st.radio("Notou alguma calosidade nova?", ["Não", "Sim"])
            ulcera = st.radio("Notou alguma ferida (úlcera) nova?", ["Não", "Sim"])
            amp = st.radio("Histórico de amputação?", ["Não", "Sim"])
            obs = st.text_area("Descreva o local da nova ferida ou calo:")
            st.markdown('</div>', unsafe_allow_html=True)

            trava = False
            if ulcera == "Sim" or calo == "Sim":
                st.warning("⚠️ Você relatou uma nova alteração! É essencial procurar ajuda profissional.")
                check = st.checkbox("Entendo que devo procurar o posto de saúde para avaliar esta alteração.")
                if not check: trava = True

        with col_orienta:
            st.markdown("### 📋 Orientações")
            st.markdown('<div class="flashcard">🦶 Examine a planta dos pés com um espelho.</div>', unsafe_allow_html=True)
            st.markdown('<div class="flashcard">🧴 Hidrate os pés, exceto entre os dedos.</div>', unsafe_allow_html=True)
            st.markdown('<div class="flashcard">👟 Use meias sem costura e calçados macios.</div>', unsafe_allow_html=True)

        if st.button("FINALIZAR AVALIAÇÃO ✔"):
            if trava:
                st.error("Por favor, confirme a ciência do encaminhamento médico.")
            else:
                registro = {
                    "Data/Hora": datetime.now().strftime('%d/%m/%Y %H:%M'),
                    **st.session_state.dados_paciente,
                    "Tempo Diabetes": tempo, "Calo": calo, "Ulcera": ulcera,
                    "Amputação": amp, "Observações": obs,
                    "Avaliador": st.session_state.usuario_nome
                }
                try:
                    df_atual = conn.read()
                    df_novo = pd.concat([df_atual, pd.DataFrame([registro])], ignore_index=True)
                    conn.update(data=df_novo)
                    st.session_state.etapa = 3
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao salvar: {e}")

    # --- ETAPA 3: FINALIZAÇÃO ---
    elif st.session_state.etapa == 3:
        st.balloons()
        st.success("✅ Avaliação registrada!")
        if st.button("Fazer outra Avaliação"):
            st.session_state.etapa = 2 # Volta direto para a clínica, sem pedir dados pessoais
            st.rerun()
