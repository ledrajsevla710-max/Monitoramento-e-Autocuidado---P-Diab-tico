# --- ETAPA 2: AVALIAÇÃO CLÍNICA ---
    elif st.session_state.etapa == 2:
        p = st.session_state.dados_paciente
        st.markdown(f"### 🩺 Avaliando: {p['Nome']}")
        
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            tempo = st.text_input("Tempo de Diabetes (anos)")
            calo = st.radio("Possui calosidade?", ["Não", "Sim"])
            ulcera = st.radio("Possui úlcera ativa?", ["Não", "Sim"])
            amp = st.radio("Histórico de amputação?", ["Não", "Sim"])
            obs = st.text_area("Localização da Ferida / Observações Clínicas")
            st.markdown('</div>', unsafe_allow_html=True)

            # Lógica de Alertas e Travas
            bloqueio_critico = False
            
            if ulcera == "Sim":
                st.markdown('<div class="alerta-card">⚠️ <b>ALERTA CRÍTICO:</b> Úlcera ativa detectada. É obrigatório o encaminhamento médico especializado imediato.</div>', unsafe_allow_html=True)
                
                # Checkbox de confirmação que atua como trava
                confirmou_atendimento = st.checkbox("Confirmo que o paciente foi orientado e encaminhado para atendimento médico.")
                
                if not confirmou_atendimento:
                    st.warning("🔒 O salvamento está bloqueado até que a orientação médica seja confirmada acima.")
                    bloqueio_critico = True
            
            if calo == "Sim":
                st.markdown('<div class="orientacao-card">💡 <b>ORIENTAÇÃO:</b> Calosidades indicam pontos de pressão. Recomendar hidratação e calçados adequados.</div>', unsafe_allow_html=True)

        # O BOTÃO DE SALVAR
        if st.button("SALVAR REGISTRO ✔"):
            if bloqueio_critico:
                st.error("Você não pode finalizar o registro sem confirmar o encaminhamento médico para a úlcera detectada.")
            else:
                # 1. Criamos os dados para salvar
                registro_final = {
                    "Data/Hora": datetime.now().strftime('%d/%m/%Y %H:%M'),
                    **st.session_state.dados_paciente,
                    "Tempo Diabetes": tempo, 
                    "Calo": calo, 
                    "Ulcera": ulcera, 
                    "Amputação": amp, 
                    "Observações": obs,
                    "Encaminhamento Medico": "Confirmado" if ulcera == "Sim" else "N/A",
                    "Avaliador": st.session_state.usuario_nome
                }
                
                try:
                    # 2. Tentamos salvar na planilha
                    df_atual = conn.read()
                    df_novo = pd.concat([df_atual, pd.DataFrame([registro_final])], ignore_index=True)
                    conn.update(data=df_novo)
                    
                    # 3. MUDANÇA DE ESTADO
                    st.session_state.etapa = 3
                    st.rerun() 
                    
                except Exception as e:
                    st.error(f"Erro ao salvar: {e}")

    # --- ETAPA 3: TELA DE CONFIRMAÇÃO ---
    elif st.session_state.etapa == 3:
        st.balloons()
        st.success("✅ Registro realizado com sucesso na planilha!")
        
        st.markdown('<div class="card"><h3>O que deseja fazer agora?</h3>', unsafe_allow_html=True)
        col_mesmo, col_outro = st.columns(2)
        
        with col_mesmo:
            if st.button("Nova Avaliação (Mesmo Paciente)"):
                st.session_state.etapa = 2
                st.rerun()
        
        with col_outro:
            if st.button("Trocar de Paciente"):
                st.session_state.etapa = 1
                st.session_state.dados_paciente = {}
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
