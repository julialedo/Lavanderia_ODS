# View - tela_morador.py
# Interface em Streamlit, recebe o input do usuário, chama o controller, mostra o feedback.

import streamlit as st
from datetime import datetime
from controladores.controlador_reserva import ControladorReserva
from controladores.controlador_maquina import ControladorMaquina
from controladores.controlador_usuario import ControladorUsuario
from controladores.controlador_ocorrencia import ControladorOcorrencia 

# Inicialização dos controladores:
controlador_reserva = ControladorReserva()
controlador_maquina = ControladorMaquina()
controlador_usuario = ControladorUsuario()
controlador_ocorrencia = ControladorOcorrencia()


# Tela inicial do Morador:
def tela_morador():

    st.sidebar.title("Menu")
    usuario_id_logado = st.session_state["usuario_dados"]["id_usuario"]
    # Mostrar nome do usuário logado
    if "usuario" in st.session_state:
        st.sidebar.write(f"👤 Usuário: {st.session_state['usuario']}")
    # Botão de logout
    if st.sidebar.button("🚪 Sair"):
        st.session_state.clear()
        st.rerun()

    st.title("👤 Área do Morador")
    st.markdown("---")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📅 Visualizar Horários", 
        "⏰ Fazer Agendamento", 
        "📋 Minhas Reservas",
        "👤 Meu Perfil"
        "⚠️ Reportar Ocorrência"
    ])

    # ------------------------------------------------------------------
    # TAB 1 - VISUALIZAR HORÁRIOS
    with tab1:
        st.subheader("Horários Disponíveis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            maquinas = controlador_maquina.listar_por_lavanderia(1)  # Assumindo lavanderia ID 1
            if maquinas:
                opcoes_maquinas = []
                for maquina in maquinas:
                    if maquina.status_maquina != "manutencao":
                        descricao = f"Máquina {maquina.id_maquina} - {maquina.tipo_maquina}"
                        opcoes_maquinas.append(descricao)
                
                maquina_selecionada = st.selectbox("Selecione a máquina:", opcoes_maquinas)
                # Extrair ID da máquina da descrição selecionada
                maquina_id = maquina_selecionada.split(" ")[1]  
            else:

                maquinas = ["Máquina 1 - Lavadora", "Máquina 2 - Secadora", "Máquina 3 - Lavadora"]
                maquina_selecionada = st.selectbox("Selecione a máquina:", maquinas)
                maquina_id = "1" if "1" in maquina_selecionada else "2"
        
        with col2:
            data_selecionada = st.date_input("Selecione a data")
        
        if st.button("🔍 Ver Horários Disponíveis"):
            # Usar controlador real para buscar horários
            horarios_disponiveis = controlador_reserva.visualizar_horarios_disponiveis(
                maquina_id, 
                data_selecionada.strftime("%Y-%m-%d")
            )
            
            st.subheader(f"Horários disponíveis - {maquina_selecionada}")
            
            if horarios_disponiveis:
                cols = st.columns(4)
                for i, horario in enumerate(horarios_disponiveis):
                    with cols[i % 4]:
                        st.write(f"**{horario}**")
                        st.success("✅ Disponível")
            else:
                st.info("📭 Não há horários disponíveis para esta data/máquina.")
    
    # ------------------------------------------------------------------
    # TAB 2 - FAZER AGENDAMENTO
    with tab2:
        st.subheader("Fazer Agendamento")
        
        with st.form("agendamento_form"):
            col1, col2 = st.columns(2)
            
            maquina_id_para_agendar = None

            with col1:
                maquinas = controlador_maquina.listar_por_lavanderia(1)
                opcoes_maquinas_agendar = [] 
                if maquinas:
                    for maquina in maquinas:
                        if maquina.status_maquina != "manutencao":
                            descricao = f"Máquina {maquina.id_maquina} - {maquina.tipo_maquina} ({maquina.capacidade})"
                            opcoes_maquinas_agendar.append(descricao)
                
                if opcoes_maquinas_agendar:
                    maquina_selecionada_agendar = st.selectbox(
                        "Selecione a máquina",
                        opcoes_maquinas_agendar,
                        key="agendamento_maquina"
                    )

                    maquina_id_para_agendar = maquina_selecionada_agendar.split(" ")[1]
                else:
                    st.info("Nenhuma máquina disponível para agendamento.")

                data_agendamento = st.date_input("Data do agendamento", key="agendamento_data")
            
            with col2:
                # Horários disponíveis para seleção (mantendo o formato original)
                horarios = [f"{hora:02d}:00" for hora in range(8, 20)]
                hora_agendamento = st.selectbox("Horário de início", horarios)
                
            
            if st.form_submit_button("📅 Fazer Agendamento"):
            
                if maquina_id_para_agendar: 
                    # Usar controlador real para criar reserva
                    reserva = controlador_reserva.criar_reserva(
                        # --- CORREÇÃO 3 ---
                        # Passar a variável correta para o controlador
                        maquina_id_para_agendar,
                        usuario_id_logado, # Usando o ID da sessão
                        data_agendamento.strftime("%Y-%m-%d"),
                        hora_agendamento
                    )
                    
                    if reserva:
                        st.success(f"🎉 Reserva realizada com sucesso! ID: {reserva.id_reserva}")
                    else:
                        st.error("❌ Erro ao fazer reserva. Horário indisponível ou dados inválidos.")
                else:

                    st.error("❌ Nenhuma máquina selecionada para o agendamento.")
    # ------------------------------------------------------------------
    # TAB 3 - MINHAS RESERVAS
    with tab3:
        st.subheader("📋 Minhas Reservas")
        
        hoje = datetime.now().date()
        
        reservas_todas = controlador_reserva.obter_reservas_por_usuario(usuario_id_logado)
        
        # 2. Filtrar a lista aqui na view
        reservas_validas = []
        if reservas_todas:
            for r in reservas_todas:
                # Condição 1: Status deve ser 'ativa'
                if r.status_reserva != "ativa":
                    continue

                # Condição 2: A data não pode ter passado
                data_reserva = None
                if isinstance(r.data_reserva, str):
                    try:
                        # Converte a string da reserva para um objeto data
                        data_reserva = datetime.strptime(r.data_reserva, "%Y-%m-%d").date()
                    except ValueError:
                        print(f"DEBUG: Data inválida na reserva {r.id_reserva}: {r.data_reserva}")
                        continue # Pula data inválida
                else:
                    # Se já for um objeto 'date', apenas atribui
                    data_reserva = r.data_reserva 

                # Compara a data da reserva com a data de hoje
                if data_reserva and data_reserva >= hoje:
                    reservas_validas.append(r)
  

        # 3. Usar a nova lista filtrada 'reservas_validas'
        if reservas_validas:
            # Texto da mensagem atualizado
            st.success(f"📋 Você tem {len(reservas_validas)} reserva(s) ativa(s) (hoje ou no futuro)")
                    
            # Iterar sobre a lista filtrada
            for reserva in reservas_validas:
                # O restante do código permanece idêntico
                with st.expander(f"Reserva {reserva.id_reserva} - {reserva.data_reserva} às {reserva.hora_inicio}"):
                    col1, col2, col3 = st.columns([3, 1, 1])
                            
                    with col1:
                        st.write(f"**Máquina ID:** {reserva.id_maquina}")
                        st.write(f"**Data:** {reserva.data_reserva}")
                        st.write(f"**Horário:** {reserva.hora_inicio} - {reserva.hora_fim}")
                        st.write(f"**Status:** {reserva.status_reserva}")
                            
                    with col2:
                        # Botão Editar Reserva
                        if st.button("✏️ Editar", key=f"edit_{reserva.id_reserva}"):
                            st.session_state[f"editando_reserva_{reserva.id_reserva}"] = True
                            st.rerun()
                            
                    with col3:
                        # Botão Cancelar Reserva
                        if st.button("❌ Cancelar", key=f"cancel_{reserva.id_reserva}"):
                            if controlador_reserva.cancelar_reserva(reserva.id_reserva, usuario_id_logado):
                                st.success("Reserva cancelada com sucesso!")
                                st.rerun()
                            else:
                                st.error("Erro ao cancelar reserva.")
                            
                    # Formulário de Edição (aparece quando clica em Editar)
                    if st.session_state.get(f"editando_reserva_{reserva.id_reserva}"):
                        st.markdown("---")
                        st.subheader("✏️ Editar Reserva")
                            
                        with st.form(f"form_editar_{reserva.id_reserva}"):
                            col_edit1, col_edit2 = st.columns(2)
                                    
                            maquina_id_edit = None
                            with col_edit1:
                                # Buscar máquinas disponíveis
                                maquinas = controlador_maquina.listar_por_lavanderia(1)
                                opcoes_maquinas_editar = []
                                if maquinas:
                                    for maquina in maquinas:
                                        if maquina.status_maquina != "manutencao":
                                            descricao = f"Máquina {maquina.id_maquina} - {maquina.tipo_maquina} ({maquina.capacidade})"
                                            opcoes_maquinas_editar.append(descricao)
                                
                                if opcoes_maquinas_editar:
                                    # Encontrar a máquina atual na lista
                                    maquina_atual = f"Máquina {reserva.id_maquina}"
                                    try:
                                        index_atual = next(i for i, maq in enumerate(opcoes_maquinas_editar) if maquina_atual in maq)
                                    except:
                                        index_atual = 0
                                    
                                    maquina_edit_selecionada = st.selectbox(
                                        "Máquina",
                                        opcoes_maquinas_editar,
                                        index=index_atual,
                                        key=f"maquina_edit_{reserva.id_reserva}"
                                    )
                                    maquina_id_edit = maquina_edit_selecionada.split(" ")[1]
                                else:
                                    st.info("Nenhuma máquina disponível para edição.")
                                    maquina_id_edit = str(reserva.id_maquina) # Mantém o ID antigo se não houver opções
                            
                            with col_edit2:
                                # Converter a data da reserva para objeto date se necessário
                                if isinstance(reserva.data_reserva, str):
                                    data_valor = datetime.strptime(reserva.data_reserva, "%Y-%m-%d").date()
                                else:
                                    data_valor = reserva.data_reserva
                                
                                nova_data = st.date_input(
                                    "Nova Data",
                                    value=data_valor,
                                    key=f"data_edit_{reserva.id_reserva}"
                                )
                                    
                                # Horários disponíveis para a nova data
                                horarios_disponiveis = []
                                if maquina_id_edit: 
                                    horarios_disponiveis = controlador_reserva.visualizar_horarios_disponiveis(
                                        maquina_id_edit, 
                                        nova_data.strftime("%Y-%m-%d")
                                    )
                                    
                                hora_atual = reserva.hora_inicio
                                
                                if hora_atual not in horarios_disponiveis:
                                    horarios_disponiveis.insert(0, hora_atual)

                                try:
                                    index_hora = horarios_disponiveis.index(hora_atual)
                                except:
                                    index_hora = 0
                                    
                                nova_hora = st.selectbox(
                                    "Novo Horário",
                                    horarios_disponiveis if horarios_disponiveis else [hora_atual], 
                                    index=index_hora,
                                    key=f"hora_edit_{reserva.id_reserva}"
                                )
                            
                            col_btn1, col_btn2 = st.columns(2)
                            with col_btn1:
                                if st.form_submit_button("💾 Salvar Alterações", use_container_width=True):
                                    
                                    if not maquina_id_edit:
                                        st.error("❌ Erro: Nenhuma máquina selecionada para salvar.")
                                    else:
                                        try:
                                            data_reserva_str = reserva.data_reserva.strftime("%Y-%m-%d") if hasattr(reserva.data_reserva, 'strftime') else str(reserva.data_reserva)
                                            data_mudou = nova_data.strftime("%Y-%m-%d") != data_reserva_str
                                            hora_mudou = nova_hora != reserva.hora_inicio
                                            maquina_mudou = maquina_id_edit != str(reserva.id_maquina)
                                            
                                            if data_mudou or hora_mudou or maquina_mudou:
                                                if controlador_reserva.cancelar_reserva(reserva.id_reserva, usuario_id_logado):
                                                    nova_reserva = controlador_reserva.criar_reserva(
                                                        maquina_id_edit,
                                                        usuario_id_logado,
                                                        nova_data.strftime("%Y-%m-%d"),
                                                        nova_hora
                                                    )
                                                    if nova_reserva:
                                                        st.success("🎉 Reserva editada com sucesso!")
                                                        del st.session_state[f"editando_reserva_{reserva.id_reserva}"]
                                                        st.rerun()
                                                    else:
                                                        st.error("❌ Não foi possível criar a nova reserva. Horário pode estar ocupado.")
                                                        # Reverter o cancelamento em caso de erro
                                                        controlador_reserva.criar_reserva(
                                                            reserva.id_maquina,
                                                            usuario_id_logado,
                                                            reserva.data_reserva,
                                                            reserva.hora_inicio
                                                        )
                                                else:
                                                    st.error("❌ Erro ao cancelar reserva anterior.")
                                            else:
                                                st.info("ℹ️ Nenhuma alteração foi feita.")
                                        
                                        except Exception as e:
                                            st.error(f"❌ Erro ao editar reserva: {str(e)}")
                            
                            with col_btn2:
                                if st.form_submit_button("❌ Cancelar Edição", use_container_width=True):
                                    del st.session_state[f"editando_reserva_{reserva.id_reserva}"]
                                    st.rerun()
        else:
            # Texto da mensagem atualizado
            st.info("📭 Você não possui reservas ativas futuras ou para hoje.")

    # ------------------------------------------------------------------
    # TAB 4 - MEU PERFIL
    with tab4:
        st.subheader("👤 Editar Informações do Perfil")

        usuario_logado = st.session_state.get("usuario_dados")
        if not usuario_logado:
            st.warning("⚠️ Não foi possível carregar suas informações. Faça login novamente.")
        else:
            with st.form("form_editar_perfil_morador"):
                nome = st.text_input("Nome", value=usuario_logado["nome"])
                email = st.text_input("Email", value=usuario_logado["email"])
                telefone = st.text_input("Telefone", value=usuario_logado["telefone"])
                senha_atual = st.text_input("Senha Atual*", type="password")
                nova_senha = st.text_input("Nova Senha (opcional)", type="password")

                salvar = st.form_submit_button("💾 Salvar Alterações")

                if salvar:
                    try:
                        sucesso = controlador_usuario.editar_perfil(
                            id_usuario=usuario_logado["id_usuario"],
                            nome=nome,
                            email=email,
                            telefone=telefone,
                            senha_atual=senha_atual,
                            nova_senha=nova_senha if nova_senha else None
                        )
                        if sucesso:
                            st.success("✅ Perfil atualizado com sucesso!")
                            st.session_state["usuario_dados"]["nome"] = nome
                            st.session_state["usuario_dados"]["email"] = email
                            st.session_state["usuario_dados"]["telefone"] = telefone
                            st.rerun()
                    except Exception as e:
                        st.error(f"❌ Erro: {str(e)}")
    # --- ABA DE OCORRÊNCIA ---
    with tab4:
        st.subheader("⚠️ Reportar uma Ocorrência")
        st.write("Encontrou algo que não está funcionando? Nos avise.")

        with st.form("form_reportar_ocorrencia", clear_on_submit=True):
            
            maquinas = controlador_maquina.listar_por_lavanderia(1)
            
            # --- MUDANÇA 1: Adicionar a opção "Nenhuma" como padrão ---
            opcoes_maquinas_reporte = ["Nenhuma (Problema geral/Outro)"]
            
            if maquinas:
                for maquina in maquinas:
                    descricao = f"Máquina {maquina.id_maquina} - {maquina.tipo_maquina} ({maquina.status_maquina})"
                    opcoes_maquinas_reporte.append(descricao)
            
            # O selectbox agora tem a opção "Nenhuma" e sempre existe
            maquina_selecionada_reporte = st.selectbox(
                "Qual máquina apresentou a ocorrência? (Opcional)",
                opcoes_maquinas_reporte,
                key="reporte_maquina"
            )

            descricao_ocorrencia = st.text_area(
                "Descreva a ocorrência (ex: 'A máquina não está ligando', 'A secadora não está esquentando').",
                height=150
            )

            enviado = st.form_submit_button("✉️ Enviar Reporte")

            if enviado:
                id_maquina_reporte = None # Começa como None
                
                # --- MUDANÇA 2: Lógica para definir o ID ou None ---
                if maquina_selecionada_reporte != "Nenhuma (Problema geral/Outro)":
                    try:
                        id_maquina_reporte = maquina_selecionada_reporte.split(" ")[1]
                    except Exception as e:
                        print(f"Erro ao extrair ID da máquina para reporte: {e}")
                        st.error("Erro ao selecionar a máquina.")
                        return # Para a execução se o nome da máquina for inválido

                # --- MUDANÇA 3: Simplificar validação ---
                if not descricao_ocorrencia:
                    st.warning("Por favor, descreva a ocorrência antes de enviar.")
                else:
                    # Chamar o controlador (id_maquina_reporte pode ser str ou None)
                    nova_ocorrencia = controlador_ocorrencia.salvar_ocorrencia(
                        id_maquina_reporte,
                        descricao_ocorrencia,
                        nome_usuario_logado # Usar o nome salvo na sessão
                    )
                    
                    if nova_ocorrencia:
                        st.success(f"✅ Ocorrência reportada com sucesso (ID: {nova_ocorrencia.id_problema}). Obrigado!")
                    else:
                        st.error("❌ Erro ao reportar a ocorrência. Tente novamente.")