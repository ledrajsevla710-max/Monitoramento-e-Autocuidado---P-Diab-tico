import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Passo Seguro", page_icon="👣", layout="wide")

conn = st.connection("gsheets", type=GSheetsConnection)

# --- LOGIN / CADASTRO ---
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

                    df_users['email_c'] = df_users['email'].astype(str).str.strip().str.lower()
                    df_users['senha_c'] = df_users['senha'].astype(str).str.strip()

                    user_match = df_users[
                        (df_users['email_c'] == email_digitado) &
                        (df_users['senha_c'] == senha_digitada)
                    ]

                    if not user_match.empty:
                        st.session_state.authenticated = True

                        col_nome = [c for c in df_users.columns if 'nome' in c][0]

                        cidade = user_match.iloc[0].get('cidade', "")
                        uf = user_match.iloc[0].get('uf', "")

                        cidade = "" if pd.isna(cidade) else str(cidade).strip()
                        uf = "" if pd.isna(uf) else str(uf).strip()

                        st.session_state.usuario_nome = user_match.iloc[0][col_nome]

                        st.session_state.dados_paciente = {
                            "Nome": user_match.iloc[0][col_nome],
                            "Cidade": cidade,
                            "UF": uf
                        }

                        st.session_state.etapa = 2
                        st.session_state.lembrete_ok = False  # 🔔 controle do lembrete

                        st.rerun()
                    else:
                        st.error("Dados incorretos.")

                except Exception as e:
                    st.error(f"Erro no login: {e}")

        with tab_cadastro:
            novo_nome = st.text_input("Nome Completo:", key="reg_nome")
            novo_email = st.text_input("E-mail:", key="reg_email")
            nova_senha = st.text_input("Senha:", type="password", key="reg_senha")

            col1, col2 = st.columns([3,1])
            with col1:
                nova_cidade = st.text_input("Cidade:", key="reg_cidade")
            with col2:
                uf_reg = st.selectbox("UF:", ["AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS","MG","PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO"], index=17)

            if st.button("FINALIZAR CADASTRO"):
                if novo_nome and novo_email and nova_senha:
                    df = conn.read(worksheet="usuarios", ttl=0)

                    novo = pd.DataFrame([{
                        "nome": novo_nome,
                        "email": novo_email.strip().lower(),
                        "senha": nova_senha,
                        "cidade": nova_cidade,
                        "uf": uf_reg
                    }])

                    df = pd.concat([df, novo], ignore_index=True)
                    conn.update(worksheet="usuarios", data=df)

                    st.success("Cadastro realizado!")
                else:
                    st.warning("Preencha tudo.")

        return False
    return True

# --- APP PRINCIPAL ---
if auth_system():

    if 'etapa' not in st.session_state:
        st.session_state.etapa = 2

    # --- SIDEBAR ---
    st.sidebar.markdown(f"### 👤 {st.session_state.usuario_nome}")

    if st.sidebar.button("🏠 Início"):
        st.session_state.etapa = 2
        st.rerun()

    if st.sidebar.button("✏️ Editar Perfil"):
        st.session_state.etapa = 1
        st.rerun()

    if st.sidebar.button("🚪 Sair"):
        st.session_state.authenticated = False
        st.rerun()

    # --- LEMBRETE CONTROLADO ---
    if not st.session_state.get("lembrete_ok", False):
        st.warning("🔔 Já olhou seus pés hoje?")
        if st.button("✔ Já olhei"):
            st.session_state.lembrete_ok = True
            st.rerun()

    # --- ETAPA 1: EDITAR PERFIL ---
    if st.session_state.etapa == 1:
        st.markdown("## 📝 Editar Perfil")

        nome = st.text_input("Nome", value=st.session_state.dados_paciente.get("Nome",""))
        cidade = st.text_input("Cidade", value=st.session_state.dados_paciente.get("Cidade",""))

        uf_lista = ["AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS","MG","PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO"]
        uf = st.selectbox("UF", uf_lista, index=17)

        if st.button("Salvar"):
            st.session_state.dados_paciente.update({
                "Nome": nome,
                "Cidade": cidade,
                "UF": uf
            })
            st.success("Atualizado!")
            st.session_state.etapa = 2
            st.rerun()

    # --- ETAPA 2: AVALIAÇÃO ---
    elif st.session_state.etapa == 2:

        p = st.session_state.dados_paciente
        cidade_formatada = f"{p['Cidade']}-{p['UF']}" if p['Cidade'] else "Não informada"

        st.markdown("## 🩺 Avaliação de Autocuidado")
        st.write(f"Paciente: **{p['Nome']}** | Cidade: **{cidade_formatada}**")

        tempo = st.text_input("Tempo de diabetes")
        calo = st.radio("Calo?", ["Não","Sim"])
        ulcera = st.radio("Ferida?", ["Não","Sim"])

        if st.button("Salvar avaliação"):
            registro = {
                "Nome": p['Nome'],
                "Cidade": p['Cidade'],
                "UF": p['UF'],
                "Tempo": tempo,
                "Calo": calo,
                "Ulcera": ulcera,
                "Data": datetime.now().strftime("%d/%m/%Y %H:%M")
            }

            df = conn.read()
            df = pd.concat([df, pd.DataFrame([registro])], ignore_index=True)
            conn.update(data=df)

            st.success("Salvo com sucesso!")
