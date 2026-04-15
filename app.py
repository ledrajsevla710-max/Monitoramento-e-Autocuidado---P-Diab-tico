import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

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
    email_login = st.text_input("E-mail:")
    senha_login = st.text_input("Senha:", type="password")

    if st.button("ACESSAR SISTEMA"):
        try:
            df = conn.read(worksheet="usuarios", ttl=0)
            df.columns = [str(c).strip().lower() for c in df.columns]

            # 🔥 FUNÇÃO CORRETA (INDENTAÇÃO CERTA)
            def limpar_valor(v):
                v = str(v).strip()
                return v[:-2] if v.endswith(".0") else v

            df['email_c'] = df['email'].astype(str).str.strip().str.lower()
            df['senha_c'] = df['senha'].apply(limpar_valor)

            email_digitado = email_login.strip().lower()
            senha_digitada = limpar_valor(senha_login)

            user = df[
                (df['email_c'] == email_digitado) &
                (df['senha_c'] == senha_digitada)
            ]

            if not user.empty:
                st.success("Login realizado!")
            else:
                st.error("Login inválido")

        except Exception as e:
            st.error(f"Erro: {e}")

df['email_c'] = df['email'].astype(str).str.strip().str.lower()
df['senha_c'] = df['senha'].apply(limpar_valor)

email_digitado = email_login.strip().lower()
senha_digitada = limpar_valor(senha_login)

                user = df[(df['email_c'] == email_login.lower().strip()) & (df['senha_c'] == senha_login.strip())]

                if not user.empty:
                    u = user.iloc[0]

                    cidade = "" if pd.isna(u.get('cidade')) else str(u.get('cidade')).strip()
                    uf = "" if pd.isna(u.get('uf')) else str(u.get('uf')).strip()

                    st.session_state.authenticated = True
                    st.session_state.usuario_nome = u.get('nome', '')

                    st.session_state.dados_paciente = {
                        "Nome": u.get('nome',''),
                        "Cidade": cidade,
                        "UF": uf,
                        "Telefone": u.get('telefone',''),
                        "Nascimento": u.get('nascimento','')
                    }

                    st.session_state.lembrete_ok = False
                    st.session_state.etapa = 2
                    st.rerun()
                else:
                    st.error("Login inválido")

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
                        "nome": nome,
                        "email": email.lower().strip(),
                        "senha": senha,
                        "cidade": cidade,
                        "uf": uf,
                        "telefone": telefone,
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

    st.markdown("""
    <style>
    .flashcard {padding:15px;border-radius:10px;background:#e3f2fd;margin:5px;font-weight:bold;}
    .alerta {background:#ffcdd2;padding:10px;border-radius:10px;font-weight:bold;}
    .lembrete {background:#ffeb3b;padding:10px;border-radius:10px;text-align:center;}
    </style>
    """, unsafe_allow_html=True)

    if 'etapa' not in st.session_state:
        st.session_state.etapa = 2

    st.sidebar.markdown(f"👤 {st.session_state.usuario_nome}")

    if st.sidebar.button("Editar Perfil"):
        st.session_state.etapa = 1
        st.rerun()

    if st.sidebar.button("Sair"):
        st.session_state.authenticated = False
        st.rerun()

    # 🔔 LEMBRETE
    if not st.session_state.lembrete_ok:
        st.markdown('<div class="lembrete">🔔 Já olhou seus pés hoje?</div>', unsafe_allow_html=True)
        if st.button("Sim, já olhei"):
            st.session_state.lembrete_ok = True
            st.success("Excelente autocuidado 👏")
            st.rerun()

    # --- EDITAR PERFIL ---
    if st.session_state.etapa == 1:
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
            st.success("Atualizado")
            st.session_state.etapa = 2
            st.rerun()

    # --- AVALIAÇÃO ---
    elif st.session_state.etapa == 2:
        p = st.session_state.dados_paciente

        cidade_fmt = f"{p['Cidade']}-{p['UF']}" if p['Cidade'] else "Não informada"

        st.markdown("## 🩺 Avaliação")
        st.write(f"Paciente: **{p['Nome']}** | Cidade: **{cidade_fmt}**")

        col1, col2 = st.columns([2,1])

        with col1:
            calo = st.radio("Calo?", ["Não","Sim"])
            ulcera = st.radio("Ferida?", ["Não","Sim"])

            if st.button("Salvar"):
                registro = {**p, "Calo": calo, "Ulcera": ulcera, "Data": datetime.now()}
                df = conn.read()
                df = pd.concat([df, pd.DataFrame([registro])])
                conn.update(data=df)
                st.success("Salvo!")

        # --- FLASHCARDS INTELIGENTES ---
        with col2:
            st.markdown("### 💡 Cuidados")

            st.markdown('<div class="flashcard">👀 Olhe seus pés todos os dias</div>', unsafe_allow_html=True)
            st.markdown('<div class="flashcard">🧴 Hidrate (não entre os dedos)</div>', unsafe_allow_html=True)
            st.markdown('<div class="flashcard">👟 Use calçado adequado</div>', unsafe_allow_html=True)

            # ⚠️ INTELIGENTE
            if ulcera == "Sim":
                st.markdown('<div class="alerta">⚠️ Procure uma UPA ou serviço de saúde IMEDIATAMENTE</div>', unsafe_allow_html=True)

            elif calo == "Sim":
                st.markdown('<div class="alerta">⚠️ Procure avaliação com enfermeiro ou centro de feridas</div>', unsafe_allow_html=True)
