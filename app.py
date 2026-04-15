import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Passo Seguro", page_icon="👣", layout="wide")

conn = st.connection("gsheets", type=GSheetsConnection)

# --- LIMPAR VALOR (.0 DO SHEETS) ---
def limpar_valor(v):
    v = str(v).strip()
    return v[:-2] if v.endswith(".0") else v


# --- LOGIN / CADASTRO ---
def auth_system():

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:

        st.markdown("<h1 style='text-align: center;'>👣 Passo Seguro</h1>", unsafe_allow_html=True)

        tab_login, tab_cadastro = st.tabs(["🔐 Login", "📝 Cadastro"])

        # -------- LOGIN --------
        with tab_login:

            email_login = st.text_input("E-mail")
            senha_login = st.text_input("Senha", type="password")

            if st.button("Entrar"):

                try:
                    df = conn.read(worksheet="usuarios", ttl=0)
                    df.columns = [str(c).strip().lower() for c in df.columns]

                    df["email_c"] = df["email"].astype(str).str.strip().str.lower()
                    df["senha_c"] = df["senha"].apply(limpar_valor)

                    email_digitado = email_login.strip().lower()
                    senha_digitada = limpar_valor(senha_login)

                    user = df[
                        (df["email_c"] == email_digitado) &
                        (df["senha_c"] == senha_digitada)
                    ]

                    if not user.empty:

                        u = user.iloc[0]

                        cidade = "" if pd.isna(u.get("cidade")) else str(u.get("cidade")).strip()
                        uf = "" if pd.isna(u.get("uf")) else str(u.get("uf")).strip()

                        st.session_state.authenticated = True
                        st.session_state.usuario_nome = u.get("nome", "")

                        st.session_state.dados_paciente = {
                            "Nome": u.get("nome", ""),
                            "Cidade": cidade,
                            "UF": uf,
                            "Telefone": u.get("telefone", ""),
                            "Nascimento": u.get("nascimento", "")
                        }

                        st.session_state.lembrete_ok = False
                        st.session_state.etapa = 0

                        st.rerun()

                    else:
                        st.error("Login inválido")

                except Exception as e:
                    st.error(f"Erro: {e}")

        # -------- CADASTRO --------
        with tab_cadastro:

            nome = st.text_input("Nome")
            email = st.text_input("Email")
            senha = st.text_input("Senha", type="password")
            telefone = st.text_input("Telefone")
            nascimento = st.date_input("Data de nascimento")
            cidade = st.text_input("Cidade")

            uf = st.selectbox("UF", ["AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS","MG","PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO"], index=17)

            if st.button("Cadastrar"):

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

    # -------- SIDEBAR --------
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

    # -------- LEMBRETE --------
    if not st.session_state.lembrete_ok:
        st.warning("🔔 Já olhou seus pés hoje?")
        if st.button("Sim, já olhei"):
            st.session_state.lembrete_ok = True
            st.success("Excelente autocuidado 👏")
            st.rerun()

    # -------- ETAPA 0: HOME --------
    if st.session_state.etapa == 0:

        st.markdown("## 👣 Bem-vindo ao Passo Seguro")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 🩸 Cuidados com Diabetes")
            st.info("Controle sua glicemia regularmente")
            st.info("Use corretamente sua medicação")
            st.info("Pratique atividade física")

        with col2:
            st.markdown("### 🥗 Alimentação")
            st.info("Prefira alimentos naturais")
            st.info("Evite açúcar e ultraprocessados")
            st.info("Beba bastante água")

        st.markdown("### 👣 Cuidados com os pés")
        st.info("Observe seus pés diariamente")
        st.info("Hidrate (não entre os dedos)")
        st.info("Use calçados adequados")

        if st.button("➡️ Iniciar Avaliação"):
            st.session_state.etapa = 2
            st.rerun()

    # -------- ETAPA 1: EDITAR PERFIL --------
    elif st.session_state.etapa == 1:

        p = st.session_state.dados_paciente

        nome = st.text_input("Nome", p["Nome"])
        telefone = st.text_input("Telefone", p["Telefone"])
        nascimento = st.text_input("Nascimento", p["Nascimento"])
        cidade = st.text_input("Cidade", p["Cidade"])
        uf = st.text_input("UF", p["UF"])

        if st.button("Salvar"):
            st.session_state.dados_paciente.update({
                "Nome": nome,
                "Telefone": telefone,
                "Nascimento": nascimento,
                "Cidade": cidade,
                "UF": uf
            })

            st.success("Perfil atualizado")
            st.session_state.etapa = 0
            st.rerun()

    # -------- ETAPA 2: AVALIAÇÃO --------
    elif st.session_state.etapa == 2:

        p = st.session_state.dados_paciente

        cidade_fmt = f"{p['Cidade']}-{p['UF']}" if p["Cidade"] else "Não informada"

        st.markdown("## 🩺 Avaliação de Autocuidado")
        st.write(f"Paciente: **{p['Nome']}** | Cidade: **{cidade_fmt}**")

        col1, col2 = st.columns([2,1])

        with col1:

            sexo = st.selectbox("Sexo", ["Masculino","Feminino","Outro"])
            idade = st.number_input("Idade", 0, 120)
            tempo = st.text_input("Tempo de Diabetes (anos)")

            calo = st.radio("Calosidade?", ["Não","Sim"])
            ulcera = st.radio("Úlcera?", ["Não","Sim"])
            amputacao = st.radio("Histórico de amputação?", ["Não","Sim"])

            local = st.text_input("Localização")
            obs = st.text_area("Observações")

            if st.button("Salvar avaliação"):

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
                    "Localização": local,
                    "Data/Hora": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "Observações": obs
                }

                df = conn.read()
                df = pd.concat([df, pd.DataFrame([registro])], ignore_index=True)
                conn.update(data=df)

                st.success("Avaliação salva!")

        with col2:

            st.markdown("### 💡 Cuidados")

            st.info("Olhe os pés todos os dias")
            st.info("Hidrate (não entre os dedos)")
            st.info("Use calçado adequado")

            if ulcera == "Sim":
                st.error("🚨 Procure uma UPA imediatamente")

            elif calo == "Sim":
                st.warning("⚠️ Procure um profissional de saúde")
