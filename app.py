import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Passo Seguro", page_icon="👣", layout="centered")

# --- SISTEMA DE LOGIN COM PERSISTÊNCIA ---
def check_password():
    # Verifica se já existe um login salvo nos parâmetros da URL
    if "auth_key" in st.query_params and st.query_params["auth_key"] == "passo_confirmado":
        st.session_state.authenticated = True
        if "avaliador" not in st.session_state:
            st.session_state.avaliador = st.query_params.get("user", "Avaliador")
        return True

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.markdown("<h1 style='text-align: center; color: #007bff;'>🔐 Acesso ao Sistema</h1>", unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div style="padding: 20px; border-radius: 15px; background-color: #ffffff; border: 1px solid #ddd;">', unsafe_allow_html=True)
            
            usuario = st.selectbox("Selecione o Avaliador:", [
                "Avaliador 01", 
                "Avaliador 02", 
                "Coordenador",
                "Outro"
            ])
            
            senha = st.text_input("Senha de Acesso:", type="password")
            manter_conectado = st.checkbox("Manter conectado neste dispositivo")
            
            if st.button("ENTRAR"):
                if senha == "passo2026":
                    st.session_state.authenticated = True
                    st.session_state.avaliador = usuario
                    
                    if manter_conectado:
                        # Salva o estado na URL para persistência
                        st.query_params["auth_key"] = "passo_confirmado"
                        st.query_params["user"] = usuario
                    st.rerun()
                else:
                    st.error("Senha incorreta.")
            st.markdown('</div>', unsafe_allow_html=True)
        return False
    return True

if check_password():
    # Estilo Visual Personalizado
    st.markdown("""
        <style>
        .stButton>button { width: 100%; border-radius: 10px; background-color: #007bff; color: white; font-weight: bold; height: 3em; }
        .card { padding: 20px; border-radius: 15px; background-color: #ffffff; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; border-left: 5px solid #007bff; color: black; }
        </style>
        """, unsafe_allow_html=True)

    # Conexão com Google Sheets (Certifique-se que o st.secrets esteja configurado)
    conn = st.connection("gsheets", type=GSheetsConnection)

    if 'etapa' not in st.session_state:
        st.session_state.etapa = 1
    if 'dados' not in st.session_state:
        st.session_state.dados = {}

    # --- TELA 1: PERFIL DO PACIENTE ---
    if st.session_state.etapa == 1:
        st.markdown(f"<p style='text-align: right; color: gray;'>👤 Usuário: {st.session_state.avaliador}</p>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; color: #007bff;'>👣 Passo Seguro</h1>", unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="card"><h3>👤 Identificação</h3>', unsafe_allow_html=True)
            nome = st.text_input("Nome Completo")
            
            col_nasc, col_sexo = st.columns(2)
            with col_nasc:
                nasc = st.date_input("Data de Nascimento", min_value=datetime(1920, 1, 1), format="DD/MM/YYYY")
            with col_sexo:
                sexo = st.selectbox("Sexo", ["Masculino", "Feminino", "Outro"])
            
            col_cid, col_uf = st.columns([3, 1])
            with col_cid:
                cidade = st.text_input("Cidade")
            with col_uf:
                uf = st.selectbox("UF", ["PI", "MA", "CE", "PE", "BA", "TO", "Outro"], index=0)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("PRÓXIMO ➡"):
            if nome and cidade:
                st.session_state.dados.update({
                    "Data Registro": datetime.now().strftime('%d/%m/%Y %H:%M'),
                    "Avaliador": st.session_state.avaliador,
                    "Nome": nome, 
                    "Data Nasc.": nasc.strftime('%d/%m/%Y'),
                    "Idade": datetime.now().year - nasc.year, 
                    "Sexo": sexo, 
                    "Cidade": cidade,
                    "Estado": uf
                })
                st.session_state.etapa = 2
                st.rerun()
            else:
                st.warning("Preencha os campos obrigatórios (Nome e Cidade).")

    # --- TELA 2: DADOS CLÍNICOS ---
    elif st.session_state.etapa == 2:
        st.markdown("<h2>🩺 Avaliação Clínica</h2>", unsafe_allow_html=True)
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            tempo = st.text_input("Tempo de Diagnóstico (anos)")
            calo = st.radio("Presença de calosidade?", ["Não", "Sim"])
            ulcera = st.radio("Ferida/Úlcera ativa?", ["Não", "Sim"])
            amp = st.radio("Histórico de amputação?", ["Não", "Sim"])
            local = st.text_area("Observações/Localização")
            st.markdown('</div>', unsafe_allow_html=True)

        col_voltar, col_salvar = st.columns(2)
        with col_voltar:
            if st.button("⬅ VOLTAR"):
                st.session_state.etapa = 1
                st.rerun()
        
        with col_salvar:
            if st.button("FINALIZAR E SALVAR ✔"):
                st.session_state.dados.update({
                    "Tempo Diabetes": tempo, 
                    "Calosidade": calo, 
                    "Úlcera": ulcera, 
                    "Amputação": amp, 
                    "Localização": local
                })
                
                try:
                    # Tenta ler os dados existentes, se falhar ou estiver vazio, cria novo DF
                    try:
                        df_existente = conn.read()
                    except:
                        df_existente = pd.DataFrame()

                    novo_registro = pd.DataFrame([st.session_state.dados])
                    df_final = pd.concat([df_existente, novo_registro], ignore_index=True)
                    
                    conn.update(data=df_final)
                    st.balloons()
                    st.session_state.etapa = 3
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao salvar na planilha: {e}")

    # --- TELA 3: CONCLUSÃO ---
    elif st.session_state.etapa == 3:
        st.success("✅ Os dados foram registrados com sucesso!")
        
        if st.button("NOVO REGISTRO 🔄"):
            st.session_state.etapa = 1
            st.session_state.dados = {}
            st.rerun()
            
        if st.button("SAIR DO SISTEMA (LOGOUT)"):
            st.session_state.authenticated = False
            # Limpa parâmetros de consulta um por um para garantir
            for key in list(st.query_params.keys()):
                del st.query_params[key]
            st.rerun()
