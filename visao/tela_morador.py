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

    st.sidebar.title("Menu")
    # Mostrar nome do usuário logado
    if "usuario" in st.session_state:
        st.sidebar.write(f"👤 Usuário: {st.session_state['usuario']}")
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
            
            with col1:
                # Buscar máquinas reais
                maquinas = controlador_maquina.listar_por_lavanderia(1)
                if maquinas:
                    opcoes_maquinas = []
                    for maquina in maquinas:
                        if maquina.status_maquina != "manutencao":
                            descricao = f"Máquina {maquina.id_maquina} - {maquina.tipo_maquina} ({maquina.capacidade})"
                            opcoes_maquinas.append(descricao)
                    
                    maquina = st.selectbox(
                        "Selecione a máquina",
                        opcoes_maquinas,
                        key="agendamento_maquina"
                    )
                    # Extrair ID da descrição
                    maquina_id = maquina.split(" ")[1]
                else:
                    # Fallback para dados fictícios
                    maquina = st.selectbox(
                        "Selecione a máquina",
                        ["Máquina 1 - Lavadora (Térreo)", "Máquina 2 - Secadora (Térreo)", "Máquina 3 - Lavadora (1º Andar)"],
                        key="agendamento_maquina"
                    )
                    maquina_id = "1" if "1" in maquina else "2"
                
                data_agendamento = st.date_input("Data do agendamento", key="agendamento_data")
            
            with col2:
                # Horários disponíveis para seleção (mantendo o formato original)
                horarios = [f"{hora:02d}:00" for hora in range(8, 20)]
                hora_agendamento = st.selectbox("Horário de início", horarios)
                
                usuario = st.text_input("Seu ID*", placeholder="Digite seu ID")
            
            if st.form_submit_button("📅 Fazer Agendamento"):
                if usuario:
                    # Usar controlador real para criar reserva
                    usuario_id = usuario.lower().replace(" ", "")
                    reserva = controlador_reserva.criar_reserva(
                        maquina_id,
                        usuario_id,
                        data_agendamento.strftime("%Y-%m-%d"),
                        hora_agendamento
                    )
                    
                    if reserva:
                        st.success(f"🎉 Reserva realizada com sucesso! ID: {reserva.id_reserva}")
                    else:
                        st.error("❌ Erro ao fazer reserva. Tente novamente.")
                else:
                    st.warning("⚠️ Por favor, digite seu ID.")
    
    with tab3:
        st.subheader("📋 Minhas Reservas")
        
        usuario_consulta = st.text_input("Digite seu ID para ver suas reservas:", 
                                       placeholder="Seu ID", 
                                       key="minhas_reservas")
        
        if usuario_consulta:
            usuario_id = usuario_consulta.lower().replace(" ", "")
            reservas = controlador_reserva.obter_reservas_por_usuario(usuario_id)
            
            if reservas:
                st.success(f"📋 Você tem {len(reservas)} reserva(s) ativa(s)")
                
                for reserva in reservas:
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
                                if controlador_reserva.cancelar_reserva(reserva.id_reserva, usuario_id):
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
                                
                                with col_edit1:
                                    # Buscar máquinas disponíveis
                                    maquinas = controlador_maquina.listar_por_lavanderia(1)
                                    if maquinas:
                                        opcoes_maquinas = []
                                        for maquina in maquinas:
                                            if maquina.status_maquina != "manutencao":
                                                descricao = f"Máquina {maquina.id_maquina} - {maquina.tipo_maquina} ({maquina.capacidade})"
                                                opcoes_maquinas.append(descricao)
                                        
                                        # Encontrar a máquina atual na lista
                                        maquina_atual = f"Máquina {reserva.id_maquina}"
                                        try:
                                            index_atual = next(i for i, maq in enumerate(opcoes_maquinas) if maquina_atual in maq)
                                        except:
                                            index_atual = 0
                                        
                                        maquina_edit = st.selectbox(
                                            "Máquina",
                                            opcoes_maquinas,
                                            index=index_atual,
                                            key=f"maquina_edit_{reserva.id_reserva}"
                                        )
                                        maquina_id_edit = maquina_edit.split(" ")[1]
                                    else:
                                        st.info("Nenhuma máquina disponível")
                                        maquina_id_edit = reserva.id_maquina
                                
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
                                    horarios_disponiveis = controlador_reserva.visualizar_horarios_disponiveis(
                                        maquina_id_edit, 
                                        nova_data.strftime("%Y-%m-%d")
                                    )
                                    
                                    # Encontrar o horário atual na lista
                                    hora_atual = reserva.hora_inicio
                                    try:
                                        index_hora = horarios_disponiveis.index(hora_atual) if hora_atual in horarios_disponiveis else 0
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
                                        try:
                                            # Converter ambas as datas para string para comparar
                                            data_reserva_str = reserva.data_reserva.strftime("%Y-%m-%d") if hasattr(reserva.data_reserva, 'strftime') else str(reserva.data_reserva)
                                            data_mudou = nova_data.strftime("%Y-%m-%d") != data_reserva_str
                                            hora_mudou = nova_hora != reserva.hora_inicio
                                            maquina_mudou = maquina_id_edit != reserva.id_maquina
                                            
                                            if data_mudou or hora_mudou or maquina_mudou:
                                                # Para simplificar, vamos cancelar a reserva atual e criar uma nova
                                                if controlador_reserva.cancelar_reserva(reserva.id_reserva, usuario_id):
                                                    nova_reserva = controlador_reserva.criar_reserva(
                                                        maquina_id_edit,
                                                        usuario_id,
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
                                                            usuario_id,
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
                st.info("📭 Você não possui reservas ativas.")
