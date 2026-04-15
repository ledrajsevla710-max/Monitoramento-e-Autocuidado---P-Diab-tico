import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

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

        st.title("👣 Passo Seguro")

        tab_login, tab_cadastro = st.tabs(["Login", "Cadastro"])

        # LOGIN
        with tab_login:
            email = st.text_input("Email", key="login_email")
            senha = st.text_input("Senha", type="password", key="login_senha")

            if st.button("Entrar", key="btn_login"):

                df = conn.read(worksheet="usuarios", ttl=0)
                df.columns = [str(c).strip().lower() for c in df.columns]

                df["email_c"] = df["email"].astype(str).str.lower().str.strip()
                df["senha_c"] = df["senha"].apply(limpar_valor)

                user = df[
                    (df["email_c"] == email.lower().strip()) &
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
        with tab_cadastro:
            nome = st.text_input("Nome", key="cad_nome")
            email = st.text_input("Email", key="cad_email")
            senha = st.text_input("Senha", type="password", key="cad_senha")
            nascimento = st.date_input("Nascimento", key="cad_nasc")
            cidade = st.text_input("Cidade", key="cad_cidade")

            uf = st.selectbox("UF",
                ["AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS","MG","PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO"],
                index=17
            )

            if st.button("Cadastrar", key="btn_cad"):
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

    st.sidebar.write(f"👤 {st.session_state.usuario_nome}")

    if st.sidebar.button("Início"):
        st.session_state.etapa = 0

    if st.sidebar.button("Nova Avaliação"):
        st.session_state.etapa = 1

    if st.sidebar.button("Sair"):
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

        st.markdown("## 👣 Cuidados com os pés")

        st.success("✔ Examine os pés diariamente")
        st.success("✔ Hidrate (não entre os dedos)")
        st.success("✔ Use calçado adequado")
        st.success("✔ Nunca ande descalço")

    # AVALIAÇÃO
    elif st.session_state.etapa == 1:

        p = st.session_state.dados_paciente
        idade = calcular_idade(p.get("Nascimento"))

        st.markdown("## 🩺 Avaliação Clínica")

        st.write(f"Paciente: **{p['Nome']}** | Idade: **{idade}**")

        calo = st.radio("Calosidade?", ["Não","Sim"])
        ulcera = st.radio("Úlcera?", ["Não","Sim"])
        amputacao = st.radio("Amputação?", ["Não","Sim"])

        local_amp = ""
        if amputacao == "Sim":
            local_amp = st.text_input("Local da amputação")

        if ulcera == "Sim":
            risco = "ALTO"
            st.error("🚨 Procurar UPA imediatamente")
        elif calo == "Sim":
            risco = "MÉDIO"
            st.warning("⚠️ Procurar avaliação profissional")
        else:
            risco = "BAIXO"

        if st.button("Salvar avaliação"):

            df = conn.read(worksheet="avaliacoes")

            registro = {
                "Nome": p["Nome"],
                "Nascimento": p["Nascimento"],
                "Idade": idade,
                "Cidade": p["Cidade"],
                "Calosidade": calo,
                "Úlcera": ulcera,
                "Amputação": amputacao,
                "Local Amputação": local_amp,
                "Risco": risco,
                "Data": datetime.now().strftime("%d/%m/%Y %H:%M")
            }

            df = pd.concat([df, pd.DataFrame([registro])], ignore_index=True)
            conn.update(worksheet="avaliacoes", data=df)

            st.success("Avaliação salva com sucesso!")

        # HISTÓRICO
        st.markdown("### 📊 Histórico")

        df_hist = conn.read(worksheet="avaliacoes")
        df_p = df_hist[df_hist["Nome"] == p["Nome"]]

        if not df_p.empty:
            st.dataframe(df_p.tail(5))
        else:
            st.info("Sem histórico ainda")
