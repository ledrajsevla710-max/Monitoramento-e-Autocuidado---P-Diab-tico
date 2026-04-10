from streamlit_gsheets import GSheetsConnection

# Criando a conexão com a planilha
conn = st.connection("gsheets", type=GSheetsConnection)

def salvar_no_google(dados_paciente):
    # Lê os dados atuais da planilha
    df_existente = conn.read(worksheet="Página1")
    
    # Cria um novo DataFrame com os dados atuais
    novo_dado = pd.DataFrame([dados_paciente])
    
    # Junta o novo dado com os antigos
    df_atualizado = pd.concat([df_existente, novo_dado], ignore_index=True)
    
    # Envia de volta para o Google Sheets
    conn.update(worksheet="Página1", data=df_atualizado)
    st.success("Dados salvos com sucesso na planilha!")
