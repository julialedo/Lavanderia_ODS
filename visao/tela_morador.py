# View - tela_morador.py
# Interface em Streamlit, recebe o input do usuário, chama o controller, mostra o feedback.

import streamlit as st
from datetime import datetime
from controladores.controlador_reserva import ControladorReserva
from controladores.controlador_maquina import ControladorMaquina

# Inicialização dos controladores:
controlador_reserva = ControladorReserva()
controlador_maquina = ControladorMaquina()


# Tela inicial do Morador:
def tela_morador():
    # 1. Obter o ID do usuário logado diretamente da sessão
    if "id_usuario" not in st.session_state or not st.session_state["logado"]:
        st.error("🔒 Sessão inválida. Por favor, faça o login novamente.")
        st.session_state["pagina"] = "tela_login" # Força volta para login
        st.rerun()
        return # Para a execução
        
    usuario_id_logado = st.session_state["id_usuario"]

    st.sidebar.title("Menu")
    # Mostrar nome do usuário logado
    if "nome" in st.session_state:
        st.sidebar.write(f"👤 Usuário: {st.session_state['nome']}")
    # Botão de logout
    if st.sidebar.button("🚪 Sair"):
        st.session_state.clear()
        st.rerun()

    st.title("👤 Área do Morador")
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["📅 Visualizar Horários", "⏰ Fazer Agendamento", "📋 Minhas Reservas"])

    with tab1:
        st.subheader("Horários Disponíveis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Buscar máquinas reais do banco (substituindo os dados fictícios)
            maquinas = controlador_maquina.listar_por_lavanderia(1)  # Assumindo lavanderia ID 1
            if maquinas:
                # Criar lista no formato antigo
                opcoes_maquinas = []
                for maquina in maquinas:
                    if maquina.status_maquina != "manutencao":
                        descricao = f"Máquina {maquina.id_maquina} - {maquina.tipo_maquina}"
                        opcoes_maquinas.append(descricao)
                
                maquina_selecionada = st.selectbox("Selecione a máquina:", opcoes_maquinas)
                # Extrair ID da máquina da descrição selecionada
                maquina_id = maquina_selecionada.split(" ")[1]  # Pega o número após "Máquina "
            else:
                # Fallback para dados fictícios se não houver máquinas
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
            
            # Mostrar horários em colunas (mantendo o formato original)
            if horarios_disponiveis:
                cols = st.columns(4)
                for i, horario in enumerate(horarios_disponiveis):
                    with cols[i % 4]:
                        st.write(f"**{horario}**")
                        st.success("✅ Disponível")
            else:
                st.info("📭 Não há horários disponíveis para esta data/máquina.")
    
    with tab2:
        st.subheader("Fazer Agendamento")
        
        with st.form("agendamento_form"):
            col1, col2 = st.columns(2)
            
            # Inicializar a variável como None AQUI
            maquina_id_para_agendar = None

            with col1:
                # Buscar máquinas reais
                maquinas = controlador_maquina.listar_por_lavanderia(1)
                # Renomeado para 'opcoes_maquinas_agendar' para evitar conflito com tab1
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
                    # --- CORREÇÃO 1 ---
                    # Atribuir o ID à variável correta 'maquina_id_para_agendar'
                    maquina_id_para_agendar = maquina_selecionada_agendar.split(" ")[1]
                else:
                    st.info("Nenhuma máquina disponível para agendamento.")

                data_agendamento = st.date_input("Data do agendamento", key="agendamento_data")
            
            with col2:
                # Horários disponíveis para seleção (mantendo o formato original)
                horarios = [f"{hora:02d}:00" for hora in range(8, 20)]
                hora_agendamento = st.selectbox("Horário de início", horarios)
                
                # O campo de texto para ID foi removido
            
            if st.form_submit_button("📅 Fazer Agendamento"):
                
                # --- CORREÇÃO 2 ---
                # A verificação agora funciona, pois 'maquina_id_para_agendar' 
                # receberá o ID ou será None
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
                    # --- CORREÇÃO 4 ---
                    # Mudar a mensagem de erro para fazer sentido
                    st.error("❌ Nenhuma máquina selecionada para o agendamento.")
    # --- FIM DO BLOCO TAB2 ---

    # --- BLOCO TAB3 MODIFICADO ---
    with tab3:
        st.subheader("📋 Minhas Reservas")
        
        # --- MUDANÇA ADICIONADA ---
        hoje = datetime.now().date()
        
        # 1. Obter TODAS as reservas do usuário (o controlador apenas busca por ID)
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
        # --- FIM DA MUDANÇA ---

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

