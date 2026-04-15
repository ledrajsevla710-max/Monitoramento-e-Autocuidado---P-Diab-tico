import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- CONFIG ---
st.set_page_config(page_title="Passo Seguro", page_icon="👣", layout="wide")

conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNÇÕES ---
def limpar_valor(v):
    v = str(v).strip()
    return v[:-2] if v.endswith(".0") else v

def calcular_idade(nascimento):
    try:
        nasc = pd.to_datetime(str(nascimento), errors="coerce")
        if pd.isna(nasc):
            return "Não informado"
        hoje = datetime.today()
        return hoje.year - nasc.year - ((hoje.month, hoje.day) < (nasc.month, nasc.day))
    except:
        return "Não informado"

# --- LOGIN / CADASTRO ---
def auth_system():

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:

        st.markdown("<h1 style='text-align: center;'>👣 Passo Seguro</h1>", unsafe_allow_html=True)

        tab_login, tab_cadastro = st.tabs(["🔐 Login", "📝 Cadastro"])

        # LOGIN
        with tab_login:
            email_login = st.text_input("E-mail", key="login_email")
            senha_login = st.text_input("Senha", type="password", key="login_senha")

            if st.button("Entrar", key="btn_login"):

                df = conn.read(worksheet="usuarios", ttl=0)
                df.columns = [str(c).strip().lower() for c in df.columns]

                df = df.astype(str)
                df["email"] = df["email"].str.strip().str.lower()

                df["senha_c"] = df["senha"].apply(limpar_valor)

                user = df[
                    (df["email"] == email_login.strip().lower()) &
                    (df["senha_c"] == limpar_valor(senha_login))
                ]

                if not user.empty:
                    u = user.iloc[0]

                    st.session_state.authenticated = True
                    st.session_state.usuario_nome = u.get("nome", "")
                    st.session_state.usuario_email = u.get("email", "")

                    st.session_state.dados_paciente = {
                        "Nome": u.get("nome", ""),
                        "Cidade": u.get("cidade", ""),
                        "UF": u.get("uf", ""),
                        "Telefone": u.get("telefone", ""),
                        "Nascimento": u.get("nascimento", "")
                    }

                    st.session_state.etapa = 0
                    st.session_state.lembrete_ok = False
                    st.rerun()
                else:
                    st.error("Login inválido")

        # CADASTRO
        with tab_cadastro:

            nome = st.text_input("Nome", key="cad_nome")
            email = st.text_input("Email", key="cad_email")
            senha = st.text_input("Senha", type="password", key="cad_senha")
            telefone = st.text_input("Telefone", key="cad_tel")
            nascimento = st.date_input("Data de nascimento", key="cad_nasc")
            cidade = st.text_input("Cidade", key="cad_cidade")

            uf = st.selectbox(
                "UF",
                ["AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS","MG","PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO"],
                index=17,
                key="cad_uf"
            )

            if st.button("Cadastrar", key="btn_cad"):

                if nome and email and senha and cidade:

                    df = conn.read(worksheet="usuarios", ttl=0)
                    df = df.astype(str)

                    novo = pd.DataFrame([{
                        "nome": nome.strip(),
                        "email": email.strip().lower(),
                        "senha": senha.strip(),
                        "cidade": cidade.strip(),
                        "uf": uf,
                        "telefone": telefone.strip(),
                        "nascimento": str(nascimento)
                    }])

                    df = pd.concat([df, novo], ignore_index=True)
                    conn.update(worksheet="usuarios", data=df)

                    st.success("Cadastro realizado!")
                else:
                    st.warning("Preencha os campos obrigatórios")

        return False

    return True


# --- APP ---
if auth_system():

    if "etapa" not in st.session_state:
        st.session_state.etapa = 0

    # SIDEBAR
    st.sidebar.markdown(f"👤 {st.session_state.usuario_nome}")

    if st.sidebar.button("🏠 Página Inicial"):
        st.session_state.etapa = 0
        st.rerun()

    if st.sidebar.button("🩺 Nova Avaliação"):
        st.session_state.etapa = 2
        st.rerun()

    if st.sidebar.button("✏️ Editar Perfil"):
        st.session_state.etapa = 1
        st.rerun()

    if st.sidebar.button("🚪 Sair"):
        st.session_state.authenticated = False
        st.rerun()

    # LEMBRETE
    if not st.session_state.lembrete_ok:
        st.warning("🔔 Já olhou seus pés hoje?")
        if st.button("Sim, já olhei"):
            st.session_state.lembrete_ok = True
            st.rerun()

    # HOME
    if st.session_state.etapa == 0:

        st.markdown("## 👣 Bem-vindo ao Passo Seguro")
        st.markdown("### 🩺 Autocuidado no Diabetes")

        st.divider()

        st.markdown("### 🔎 Buscar informações confiáveis")
        busca = st.text_input("Digite o que deseja pesquisar (ex: pé diabético)")
        if busca:
            st.markdown(f"[🔍 Buscar no Google](https://www.google.com/search?q={busca})")

        st.divider()

        st.markdown("### 🌐 Sites confiáveis")
        st.markdown("[Ministério da Saúde](https://www.gov.br/saude)")
        st.markdown("[Sociedade Brasileira de Diabetes](https://diabetes.org.br)")
        st.markdown("[Fiocruz](https://portal.fiocruz.br)")

        st.divider()

        st.markdown("### 👣 Cuidados essenciais")
        st.success("✔ Examine os pés diariamente")
        st.success("✔ Hidrate (não entre os dedos)")
        st.success("✔ Use calçado adequado")
        st.success("✔ Nunca ande descalço")

        if st.button("🩺 Iniciar Avaliação"):
            st.session_state.etapa = 2
            st.rerun()

    # AVALIAÇÃO
    elif st.session_state.etapa == 2:

        p = st.session_state.dados_paciente
        idade = calcular_idade(p.get("Nascimento"))

        st.markdown("## 🩺 Avaliação")
        st.write(f"Paciente: **{p['Nome']}** | Idade: **{idade}**")

        calo = st.radio("Calosidade?", ["Não","Sim"])
        ulcera = st.radio("Úlcera?", ["Não","Sim"])

        if ulcera == "Sim":
            st.error("🚨 Procure atendimento imediato")

        if st.button("Salvar"):
            st.success("Avaliação registrada")
