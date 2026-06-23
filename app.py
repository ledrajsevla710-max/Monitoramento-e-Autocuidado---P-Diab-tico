import streamlit as st
import pandas as pd
from datetime import datetime, date
from streamlit_gsheets import GSheetsConnection

# --- CONFIG ---
st.set_page_config(page_title="Passo Seguro", page_icon="👣", layout="wide")

conn = st.connection("gsheets", type=GSheetsConnection)

# --- SAFE READ ---
def ler_planilha(worksheet):
    try:
        df = conn.read(worksheet=worksheet, ttl=0)
        if df is None:
            return pd.DataFrame()
        return df
    except:
        return pd.DataFrame()

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

# --- AUTH ---
def auth_system():

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:

        st.markdown("<h1 style='text-align:center;'>👣 Passo Seguro</h1>", unsafe_allow_html=True)

        tab_login, tab_cadastro = st.tabs(["🔐 Login", "📝 Cadastro"])

        # LOGIN
        with tab_login:
            email_login = st.text_input("E-mail")
            senha_login = st.text_input("Senha", type="password")

            if st.button("Entrar"):

                df = ler_planilha("usuarios")

                if df.empty:
                    st.error("Nenhum usuário cadastrado")
                    return False

                df.columns = [c.lower().strip() for c in df.columns]

                if "email" not in df.columns or "senha" not in df.columns:
                    st.error("Planilha inválida")
                    return False

                df = df.astype(str)
                df["email"] = df["email"].str.lower().str.strip()
                df["senha_c"] = df["senha"].apply(limpar_valor)

                user = df[
                    (df["email"] == email_login.lower().strip()) &
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

            nome = st.text_input("Nome")
            email = st.text_input("Email")
            senha = st.text_input("Senha", type="password")
            telefone = st.text_input("Telefone")

            nascimento = st.date_input(
                "Data de nascimento",
                value=date(2000, 1, 1),
                min_value=date(1900, 1, 1),
                max_value=date.today()
            )

            cidade = st.text_input("Cidade")

            uf = st.selectbox(
                "UF",
                ["AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS","MG","PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO"]
            )

            if st.button("Cadastrar"):

                if nome and email and senha and cidade:

                    df = ler_planilha("usuarios")

                    novo = pd.DataFrame([{
                        "nome": nome.strip(),
                        "email": email.strip().lower(),
                        "senha": senha.strip(),
                        "cidade": cidade.strip(),
                        "uf": uf,
                        "telefone": telefone.strip(),
                        "nascimento": str(nascimento)
                    }])

                    conn.append(worksheet="usuarios", data=novo)
                    st.success("Cadastro realizado!")

                else:
                    st.warning("Preencha todos os campos")

        return False

    return True


# --- APP ---
if auth_system():

    if "etapa" not in st.session_state:
        st.session_state.etapa = 0

    st.sidebar.write(f"👤 {st.session_state.usuario_nome}")

    if st.sidebar.button("🏠 Início"):
        st.session_state.etapa = 0
        st.rerun()

    if st.sidebar.button("🩺 Avaliação"):
        st.session_state.etapa = 2
        st.rerun()

    if st.sidebar.button("✏️ Perfil"):
        st.session_state.etapa = 1
        st.rerun()

    if st.sidebar.button("🚪 Sair"):
        st.session_state.authenticated = False
        st.rerun()

    if not st.session_state.get("lembrete_ok", False):
        st.warning("🔔 Já olhou seus pés hoje?")
        if st.button("Sim, já olhei"):
            st.session_state.lembrete_ok = True
            st.rerun()

    # HOME
    if st.session_state.etapa == 0:

        st.title("👣 Passo Seguro")

        busca = st.text_input("Pesquisar saúde")
        if busca:
            st.markdown(f"[Buscar no Google](https://www.google.com/search?q={busca})")

        st.success("✔ Examine os pés diariamente")
        st.success("✔ Hidrate corretamente")
        st.success("✔ Use calçado adequado")

    # PERFIL
    elif st.session_state.etapa == 1:

        p = st.session_state.dados_paciente

        nome = st.text_input("Nome", p["Nome"])
        telefone = st.text_input("Telefone", p["Telefone"])

        nascimento = st.date_input(
            "Data de nascimento",
            value=pd.to_datetime(p["Nascimento"], errors="coerce") if p["Nascimento"] else date(2000,1,1)
        )

        cidade = st.text_input("Cidade", p["Cidade"])

        if st.button("Salvar"):

            df = ler_planilha("usuarios")

            if not df.empty:
                df["email"] = df["email"].astype(str).str.lower().str.strip()

                idx = df[df["email"] == st.session_state.usuario_email].index

                if len(idx) > 0:
                    i = idx[0]
                    df.loc[i, "nome"] = nome
                    df.loc[i, "telefone"] = telefone
                    df.loc[i, "cidade"] = cidade
                    df.loc[i, "nascimento"] = str(nascimento)

                    conn.update(worksheet="usuarios", data=df)

            st.success("Atualizado!")
            st.session_state.etapa = 0
            st.rerun()

    # AVALIAÇÃO
    elif st.session_state.etapa == 2:

        p = st.session_state.dados_paciente
        idade = calcular_idade(p.get("Nascimento"))

        st.subheader("Avaliação")

        calo = st.radio("Calosidade?", ["Não","Sim"])
        ulcera = st.radio("Úlcera?", ["Não","Sim"])
        amputacao = st.radio("Amputação?", ["Não","Sim"])

        local = st.text_input("Local amputação") if amputacao == "Sim" else ""

        risco = "BAIXO"
        if ulcera == "Sim":
            risco = "ALTO"
        elif calo == "Sim":
            risco = "MÉDIO"

        if st.button("Salvar avaliação"):

            registro = pd.DataFrame([{
                "Nome": p["Nome"],
                "Idade": idade,
                "Cidade": p["Cidade"],
                "Calosidade": calo,
                "Úlcera": ulcera,
                "Amputação": amputacao,
                "Local Amputação": local,
                "Risco": risco,
                "Data": datetime.now().strftime("%d/%m/%Y %H:%M")
            }])

            conn.append(worksheet="avaliacoes", data=registro)
            st.success("Avaliação salva!")

        st.markdown("### Histórico")

        df_hist = ler_planilha("avaliacoes")

        if not df_hist.empty:
            df_p = df_hist[df_hist["Nome"] == p["Nome"]]
            st.dataframe(df_p.tail(5))
        else:
            st.info("Sem registros")
