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
        nasc = pd.to_datetime(nascimento)
        hoje = datetime.today()
        return hoje.year - nasc.year - ((hoje.month, hoje.day) < (nasc.month, nasc.day))
    except:
        return ""

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

                try:
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
                        st.session_state.usuario_nome = u.get("nome", "")

                        st.session_state.dados_paciente = {
                            "Nome": u.get("nome", ""),
                            "Cidade": "" if pd.isna(u.get("cidade")) else str(u.get("cidade")),
                            "UF": "" if pd.isna(u.get("uf")) else str(u.get("uf")),
                            "Telefone": u.get("telefone", ""),
                            "Nascimento": u.get("nascimento", "")
                        }

                        st.session_state.etapa = 0
                        st.session_state.lembrete_ok = False
                        st.rerun()
                    else:
                        st.error("Login inválido")

                except Exception as e:
                    st.error(f"Erro: {e}")

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

                    try:
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
                    except Exception as e:
                        st.error(f"Erro: {e}")
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
        if st.button("Sim, já olhei", key="btn_lembrete"):
            st.session_state.lembrete_ok = True
            st.success("Ótimo autocuidado 👏")
            st.rerun()

    # HOME
    if st.session_state.etapa == 0:

        st.markdown("## 👣 Bem-vindo ao Passo Seguro")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 🩸 Diabetes")
            st.info("Controle glicemia regularmente")
            st.info("Use medicação corretamente")
            st.info("Pratique atividade física")

        with col2:
            st.markdown("### 🥗 Alimentação")
            st.info("Prefira alimentos naturais")
            st.info("Evite açúcar")
            st.info("Beba água")

        st.markdown("### 👣 Cuidados com os pés")
        st.info("Observe diariamente")
        st.info("Hidrate (não entre os dedos)")
        st.info("Use calçado adequado")

        if st.button("➡️ Iniciar Avaliação", key="btn_inicio"):
            st.session_state.etapa = 2
            st.rerun()

    # EDITAR PERFIL
    elif st.session_state.etapa == 1:

        p = st.session_state.dados_paciente

        nome = st.text_input("Nome", p["Nome"], key="edit_nome")
        telefone = st.text_input("Telefone", p["Telefone"], key="edit_tel")
        nascimento = st.text_input("Nascimento", p["Nascimento"], key="edit_nasc")
        cidade = st.text_input("Cidade", p["Cidade"], key="edit_cid")
        uf = st.text_input("UF", p["UF"], key="edit_uf")

        if st.button("Salvar", key="btn_save"):
            st.session_state.dados_paciente.update({
                "Nome": nome,
                "Telefone": telefone,
                "Nascimento": nascimento,
                "Cidade": cidade,
                "UF": uf
            })
            st.success("Atualizado!")
            st.session_state.etapa = 0
            st.rerun()

    # AVALIAÇÃO
    elif st.session_state.etapa == 2:

        p = st.session_state.dados_paciente
        idade = calcular_idade(p.get("Nascimento", ""))

        cidade_fmt = f"{p['Cidade']}-{p['UF']}" if p["Cidade"] else "Não informada"

        st.markdown("## 🩺 Avaliação")
        st.write(f"Paciente: **{p['Nome']}** | Cidade: **{cidade_fmt}**")

        col1, col2 = st.columns([2,1])

        with col1:

            sexo = st.selectbox("Sexo", ["Masculino","Feminino","Outro"], key="aval_sexo")
            st.text_input("Idade", value=idade, disabled=True, key="aval_idade")

            tempo = st.text_input("Tempo de Diabetes", key="aval_tempo")

            calo = st.radio("Calosidade?", ["Não","Sim"], key="aval_calo")
            ulcera = st.radio("Úlcera?", ["Não","Sim"], key="aval_ulcera")
            amputacao = st.radio("Amputação?", ["Não","Sim"], key="aval_amp")

            local_amp = ""
            if amputacao == "Sim":
                local_amp = st.text_input("Local da amputação", key="aval_local")

            obs = st.text_area("Observações", key="aval_obs")

            if st.button("Salvar avaliação", key="btn_salvar"):

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
                    "Observações": obs
                }

                df = conn.read()
                df = pd.concat([df, pd.DataFrame([registro])], ignore_index=True)
                conn.update(data=df)

                st.success("Avaliação salva!")

        with col2:

            st.markdown("### 💡 Cuidados")

            st.info("Olhe os pés diariamente")
            st.info("Hidrate (não entre os dedos)")
            st.info("Use calçado adequado")

            if ulcera == "Sim":
                st.error("🚨 Procure uma UPA imediatamente")

            elif calo == "Sim":
                st.warning("⚠️ Procure um profissional de saúde")
