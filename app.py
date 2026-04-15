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

                    user_match = df_users[
                        (df_users['email_c'] == email_digitado) &
                        (df_users['senha_c'] == senha_digitada)
                    ]

                    if not user_match.empty:
                        st.session_state.authenticated = True
                        col_nome = [c for c in df_users.columns if 'nome' in c][0]

                        st.session_state.usuario_nome = user_match.iloc[0][col_nome]

                        # 🔥 CORREÇÃO DO NAN
                        cidade = user_match.iloc[0].get('cidade', "")
                        uf = user_match.iloc[0].get('uf', "")

                        cidade = "" if pd.isna(cidade) else str(cidade).strip()
                        uf = "" if pd.isna(uf) else str(uf).strip()

                        st.session_state.dados_paciente = {
                            "Nome": user_match.iloc[0][col_nome],
                            "Cidade": cidade,
                            "UF": uf,
                            "Sexo": user_match.iloc[0].get('sexo', "Outro")
                        }

                        st.session_state.etapa = 2
                        st.rerun()
                    else:
                        st.error("Dados incorretos.")
                except Exception as e:
                    st.error(f"Erro no login: {e}")

        with tab_cadastro:
            st.markdown("### Criar Nova Conta")
            novo_nome = st.text_input("Nome Completo:", key="reg_nome")
            novo_email = st.text_input("E-mail:", key="reg_email")
            nova_senha = st.text_input("Senha:", type="password", key="reg_senha")

            col_c, col_u = st.columns([3, 1])
            with col_c:
                nova_cidade = st.text_input("Cidade:", key="reg_cidade")
            with col_u:
                uf_reg = st.selectbox(
                    "UF:",
                    ["AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS","MG","PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO"],
                    index=17,
                    key="reg_uf"
                )

            if st.button("FINALIZAR CADASTRO"):
                if novo_nome and novo_email and nova_senha:
                    try:
                        df_users_at = conn.read(worksheet="usuarios", ttl=0)

                        novo_user = pd.DataFrame([{
                            "nome": novo_nome,
                            "email": novo_email.strip().lower(),
                            "senha": nova_senha,
                            "cidade": nova_cidade,
                            "uf": uf_reg
                        }])

                        df_final_u = pd.concat([df_users_at, novo_user], ignore_index=True)
                        conn.update(worksheet="usuarios", data=df_final_u)

                        st.success("Cadastro realizado! Agora faça o login.")
                    except Exception as e:
                        st.error(f"Erro ao cadastrar: {e}")
                else:
                    st.warning("Preencha todos os campos.")
        return False
    return True


if auth_system():

    st.markdown("""
        <style>
        .stButton>button { width: 100%; border-radius: 10px; background-color: #007bff; color: white; font-weight: bold; }
        .card { padding: 20px; border-radius: 15px; background-color: #ffffff; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; border-left: 5px solid #007bff; color: black; }
        .flashcard { padding: 20px; border-radius: 15px; background-color: #e3f2fd; border: 1px solid #90caf9; text-align: center; margin-bottom: 10px; min-height: 120px; display: flex; align-items: center; justify-content: center; font-weight: bold; color: #0d47a1; }
        .alerta-card { padding: 15px; border-radius: 10px; background-color: #fff3cd; border-left: 5px solid #ffc107; color: #856404; margin-top: 10px; font-weight: bold; }
        .lembrete-pes { background-color: #ffeb3b; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold; color: black; margin-bottom: 20px; border: 2px dashed #f44336; }
        </style>
    """, unsafe_allow_html=True)

    if 'etapa' not in st.session_state:
        st.session_state.etapa = 2

    st.sidebar.markdown(f"### 👤 {st.session_state.usuario_nome}")

    if st.sidebar.button("🏠 Início / Nova Avaliação"):
        st.session_state.etapa = 2
        st.rerun()

    if st.sidebar.button("✏️ Editar Perfil"):
        st.session_state.etapa = 1
        st.rerun()

    st.sidebar.divider()

    if st.sidebar.button("🚪 Sair do Sistema"):
        st.session_state.authenticated = False
        st.rerun()

    st.markdown('<div class="lembrete-pes">🔔 LEMBRETE DIÁRIO: Já olhou seus pés hoje?</div>', unsafe_allow_html=True)

    if st.session_state.etapa == 2:
        p = st.session_state.dados_paciente

        cidade_formatada = f"{p['Cidade']}-{p['UF']}" if p['Cidade'] and p['UF'] else "Não informada"

        st.markdown(f"### 🩺 Avaliação de Autocuidado")
        st.write(f"Paciente: **{p['Nome']}** | Cidade: **{cidade_formatada}**")

        tempo = st.text_input("Tempo de Diabetes (anos)")
        calo = st.radio("Notou alguma calosidade nova?", ["Não", "Sim"])
        ulcera = st.radio("Notou alguma ferida nova?", ["Não", "Sim"])

        if st.button("SALVAR ✔"):
            st.success("Registro salvo!")
