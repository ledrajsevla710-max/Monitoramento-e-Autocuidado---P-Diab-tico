import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- CONFIG ---
st.set_page_config(page_title="Passo Seguro - SUS", page_icon="🏥", layout="wide")

conn = st.connection("gsheets", type=GSheetsConnection)

# --- ESTILO SUS ---
st.markdown("""
<style>
body {
    background-color: #f4f9f4;
}
h1, h2, h3 {
    color: #006837;
}
.stButton>button {
    background-color: #00995d;
    color: white;
    border-radius: 8px;
    font-weight: bold;
}
.stButton>button:hover {
    background-color: #007a4d;
}
</style>
""", unsafe_allow_html=True)

# --- FUNÇÕES ---
def limpar_valor(v):
    v = str(v).strip()
    return v[:-2] if v.endswith(".0") else v

def calcular_idade(nascimento):
    try:
        if not nascimento:
            return "Não informado"
        nasc = pd.to_datetime(nascimento, errors="coerce")
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

        st.markdown("<h1 style='text-align:center;'>🏥 Passo Seguro - SUS</h1>", unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["🔐 Login", "📝 Cadastro"])

        # LOGIN
        with tab1:
            email = st.text_input("E-mail", key="login_email")
            senha = st.text_input("Senha", type="password", key="login_senha")

            if st.button("Entrar", key="btn_login"):

                df = conn.read(worksheet="usuarios", ttl=0)
                df.columns = [str(c).strip().lower() for c in df.columns]

                df["email_c"] = df["email"].astype(str).str.strip().str.lower()
                df["senha_c"] = df["senha"].apply(limpar_valor)

                user = df[
                    (df["email_c"] == email.strip().lower()) &
                    (df["senha_c"] == limpar_valor(senha))
                ]

                if not user.empty:

                    u = user.iloc[0]

                    nascimento = "" if pd.isna(u.get("nascimento")) else str(u.get("nascimento"))

                    st.session_state.authenticated = True
                    st.session_state.usuario_nome = u.get("nome","")

                    st.session_state.dados_paciente = {
                        "Nome": u.get("nome",""),
                        "Cidade": str(u.get("cidade","")),
                        "UF": str(u.get("uf","")),
                        "Nascimento": nascimento
                    }

                    st.session_state.etapa = 0
                    st.session_state.lembrete_ok = False
                    st.rerun()
                else:
                    st.error("Login inválido")

        # CADASTRO
        with tab2:
            nome = st.text_input("Nome")
            email = st.text_input("Email")
            senha = st.text_input("Senha", type="password")
            nascimento = st.date_input("Data de nascimento")
            cidade = st.text_input("Cidade")

            uf = st.selectbox("UF",
                ["AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS","MG","PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO"],
                index=17
            )

            if st.button("Cadastrar"):
                df = conn.read(worksheet="usuarios", ttl=0)

                novo = pd.DataFrame([{
                    "nome": nome,
                    "email": email.lower(),
                    "senha": senha,
                    "cidade": cidade,
                    "uf": uf,
                    "nascimento": str(nascimento)
                }])

                df = pd.concat([df, novo], ignore_index=True)
                conn.update(worksheet="usuarios", data=df)

                st.success("Cadastro realizado!")

        return False
    return True


# --- APP ---
if auth_system():

    if "etapa" not in st.session_state:
        st.session_state.etapa = 0

    st.sidebar.markdown(f"👤 {st.session_state.usuario_nome}")

    if st.sidebar.button("🏠 Início"):
        st.session_state.etapa = 0

    if st.sidebar.button("🩺 Avaliação"):
        st.session_state.etapa = 1

    if st.sidebar.button("📞 Suporte"):
        st.session_state.etapa = 2

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

        st.markdown("## 👣 Educação em Saúde - SUS")

        st.success("✔ Examine seus pés todos os dias")
        st.success("✔ Lave e seque bem")
        st.success("✔ Hidrate (não entre os dedos)")
        st.success("✔ Use calçados fechados")
        st.success("✔ Nunca ande descalço")

    # AVALIAÇÃO
    elif st.session_state.etapa == 1:

        p = st.session_state.dados_paciente
        idade = calcular_idade(p.get("Nascimento"))

        st.markdown("## 🩺 Avaliação de Autocuidado")

        st.text_input("Idade", value=idade, disabled=True)

        calo = st.radio("Calosidade?", ["Não","Sim"])
        ulcera = st.radio("Ferida?", ["Não","Sim"])

        if ulcera == "Sim":
            st.error("🚨 Procure uma UPA imediatamente")
        elif calo == "Sim":
            st.warning("⚠️ Procure avaliação profissional")

    # SUPORTE
    elif st.session_state.etapa == 2:

        st.markdown("## 📞 Contato com Suporte")

        st.info("Em caso de dúvidas ou problemas no sistema, entre em contato:")

        st.markdown("📧 **Email:** jardelalves@id.uff.br")

        st.markdown("⏱️ Tempo de resposta: até 48h úteis")

        st.success("✔ Este sistema é voltado ao cuidado preventivo do pé diabético no SUS")
