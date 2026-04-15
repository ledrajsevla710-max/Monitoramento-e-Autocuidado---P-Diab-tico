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
        if nascimento is None or nascimento == "":
            return "Não informado"
        nasc = pd.to_datetime(nascimento, errors="coerce")
        if pd.isna(nasc):
            return "Não informado"
        hoje = datetime.today()
        idade = hoje.year - nasc.year - ((hoje.month, hoje.day) < (nasc.month, nasc.day))
        return int(idade)
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

                df["email_c"] = df["email"].astype(str).str.strip().str.lower()
                df["senha_c"] = df["senha"].apply(limpar_valor)

                user = df[
                    (df["email_c"] == email_login.strip().lower()) &
                    (df["senha_c"] == limpar_valor(senha_login))
                ]

                if not user.empty:
                    u = user.iloc[0]

                    st.session_state.authenticated = True
                    st.session_state.usuario_nome = u.get("nome","")

                    st.session_state.dados_paciente = {
                        "Nome": u.get("nome",""),
                        "Cidade": "" if pd.isna(u.get("cidade")) else str(u.get("cidade")),
                        "UF": "" if pd.isna(u.get("uf")) else str(u.get("uf")),
                        "Telefone": u.get("telefone",""),
                        "Nascimento": u.get("nascimento","")
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

            uf = st.selectbox("UF",
                ["AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS","MG","PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO"],
                index=17,
                key="cad_uf"
            )

            if st.button("Cadastrar", key="btn_cad"):

                if nome and email and senha and cidade:
                    df = conn.read(worksheet="usuarios", ttl=0)

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

    st.sidebar.markdown(f"👤 {st.session_state.usuario_nome}")

    if st.sidebar.button("🏠 Página Inicial"):
        st.session_state.etapa = 0
        st.rerun()

    if st.sidebar.button("🩺 Nova Avaliação"):
        st.session_state.etapa = 2
        st.rerun()

    if st.sidebar.button("🚪 Sair"):
        st.session_state.authenticated = False
        st.rerun()

    # LEMBRETE
    if not st.session_state.lembrete_ok:
        st.warning("🔔 Já olhou seus pés hoje?")
        if st.button("Sim, já olhei", key="btn_lembrete"):
            st.session_state.lembrete_ok = True
            st.success("Ótimo autocuidado 👏")
            st.rerun()

    # HOME
    if st.session_state.etapa == 0:
        st.markdown("## 👣 Educação em Saúde")

        st.info("🩸 Controle glicemia regularmente e conforme orientação médica")
        st.info("🥗 Evite açúcar e alimentos ultraprocessados")
        st.info("💧 Hidrate-se bem ao longo do dia")

        st.markdown("### 👣 Cuidados com os pés")

        st.success("✔ Examine seus pés TODOS os dias (use espelho se necessário)")
        st.success("✔ Lave com água morna e sabão neutro")
        st.success("✔ Seque bem, principalmente entre os dedos")
        st.success("✔ Hidrate a pele (NÃO entre os dedos)")
        st.success("✔ Use calçados fechados e confortáveis")
        st.success("✔ Nunca ande descalço")

        if st.button("➡️ Iniciar Avaliação"):
            st.session_state.etapa = 2
            st.rerun()

    # AVALIAÇÃO
    elif st.session_state.etapa == 2:

        p = st.session_state.dados_paciente
        idade = calcular_idade(p.get("Nascimento",""))

        st.markdown("## 🩺 Avaliação de Autocuidado")

        col1, col2 = st.columns([2,1])

        with col1:

            sexo = st.selectbox("Sexo", ["Masculino","Feminino","Outro"])
            st.text_input("Idade", value=idade, disabled=True)

            tempo = st.text_input("Tempo de Diabetes")

            calo = st.radio("Presença de calosidade?", ["Não","Sim"])
            ulcera = st.radio("Presença de úlcera/ferida?", ["Não","Sim"])
            amputacao = st.radio("Histórico de amputação?", ["Não","Sim"])

            local_amp = ""
            if amputacao == "Sim":
                local_amp = st.text_input("Local da amputação")

            obs = st.text_area("Observações clínicas")

            if st.button("Salvar avaliação"):

                if ulcera == "Sim":
                    risco = "ALTO"
                elif calo == "Sim":
                    risco = "MÉDIO"
                else:
                    risco = "BAIXO"

                df = conn.read(worksheet="avaliacoes")

                registro = {
                    "Nome": p['Nome'],
                    "Nascimento": p['Nascimento'],
                    "Idade": idade,
                    "Sexo": sexo,
                    "Cidade": p['Cidade'],
                    "Tempo Diabetes": tempo,
                    "Calosidade": calo,
                    "Úlcera": ulcera,
                    "Amputação": amputacao,
                    "Local Amputação": local_amp,
                    "Data/Hora": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "Observações": obs,
                    "Risco": risco
                }

                df = pd.concat([df, pd.DataFrame([registro])], ignore_index=True)
                conn.update(worksheet="avaliacoes", data=df)

                st.success(f"Avaliação salva! Risco: {risco}")

        with col2:

            st.markdown("### 💡 Orientações Clínicas")

            st.info("👀 Inspecione pés diariamente (feridas, bolhas, rachaduras)")
            st.info("🧴 Hidrate a pele (evite entre os dedos)")
            st.info("🧦 Use meias limpas e sem costura apertada")
            st.info("👟 Use sapatos fechados e confortáveis")
            st.info("🔥 Nunca use água muito quente")

            if ulcera == "Sim":
                st.error("🚨 ENCAMINHAR IMEDIATAMENTE PARA UPA OU SERVIÇO ESPECIALIZADO")

            elif calo == "Sim":
                st.warning("⚠️ Encaminhar para avaliação profissional (risco de lesão)")

        # HISTÓRICO
        st.markdown("### 📊 Histórico")

        df_hist = conn.read(worksheet="avaliacoes")
        df_p = df_hist[df_hist["Nome"] == p["Nome"]]

        if not df_p.empty:
            st.dataframe(df_p.tail(5))
        else:
            st.info("Sem histórico ainda")
