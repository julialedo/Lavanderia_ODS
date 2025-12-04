# View - tela_morador.py
# Interface em Streamlit, recebe o input do usuário, chama o controller, mostra o feedback.

import streamlit as st
from datetime import datetime

# Controladores inicializados UMA VEZ no topo
try:
    from controladores.controlador_reserva import ControladorReserva
    from controladores.controlador_maquina import ControladorMaquina
    from controladores.controlador_usuario import ControladorUsuario
    from controladores.controlador_ocorrencia import ControladorOcorrencia
    
    controlador_reserva = ControladorReserva()
    controlador_maquina = ControladorMaquina()
    controlador_usuario = ControladorUsuario()
    controlador_ocorrencia = ControladorOcorrencia()
except ImportError:
    # Fallback para evitar quebras
    controlador_reserva = None
    controlador_maquina = None
    controlador_usuario = None
    controlador_ocorrencia = None

# Cache para dados frequentemente acessados
def get_lavanderia_nome(id_lavanderia):
    """Cache do nome da lavanderia"""
    if not id_lavanderia:
        return "Sua Lavanderia"
        
    cache_key = f"lavanderia_nome_{id_lavanderia}"
    if cache_key not in st.session_state:
        try:
            from controladores.controlador_plataforma import ControladorPlataforma
            controlador_plataforma = ControladorPlataforma()
            lavanderia_info = controlador_plataforma.obter_lavanderia_por_id(id_lavanderia)
            st.session_state[cache_key] = lavanderia_info.get("nome", "Sua Lavanderia") if lavanderia_info else "Sua Lavanderia"
        except:
            st.session_state[cache_key] = "Sua Lavanderia"
    return st.session_state[cache_key]

def get_maquinas_lavanderia(id_lavanderia):
    """Cache das máquinas da lavanderia"""
    if not id_lavanderia:
        return []
        
    cache_key = f"maquinas_{id_lavanderia}"
    if cache_key not in st.session_state:
        try:
            maquinas = controlador_maquina.listar_por_lavanderia(id_lavanderia) if controlador_maquina else []
            st.session_state[cache_key] = maquinas
        except:
            st.session_state[cache_key] = []
    return st.session_state[cache_key]

def clear_maquinas_cache(id_lavanderia):
    """Limpa cache de máquinas quando necessário"""
    if id_lavanderia:
        cache_key = f"maquinas_{id_lavanderia}"
        if cache_key in st.session_state:
            del st.session_state[cache_key]

def tela_morador():
    # Verificação inicial de controladores
    if not all([controlador_reserva, controlador_maquina, controlador_usuario, controlador_ocorrencia]):
        st.error("⚠️ Sistema temporariamente indisponível. Tente novamente.")
        if st.button("🔄 Recarregar"):
            st.rerun()
        return
    
    dados_usuario = st.session_state.get("usuario_dados")
    if not dados_usuario:
        st.error("Sessão expirada. Faça login novamente.")
        return
        
    usuario_id_logado = dados_usuario["id_usuario"]
    nome_usuario_logado = dados_usuario["nome"]
    id_lavanderia_logada = st.session_state.get("id_lavanderia")
    
    # 🔥 NOVO: Buscar nome da lavanderia
    nome_lavanderia = "Sua Lavanderia"
    if id_lavanderia_logada:
        from controladores.controlador_plataforma import ControladorPlataforma
        controlador_plataforma = ControladorPlataforma()
        lavanderia_info = controlador_plataforma.obter_lavanderia_por_id(id_lavanderia_logada)
        if lavanderia_info:
            nome_lavanderia = lavanderia_info.get("nome", "Sua Lavanderia")
    
    col_vazia, col_titulo, col_notificacao = st.columns([1, 8, 1])
    
    with col_titulo:
        st.title(f"👤 Área do Morador - {nome_lavanderia}") # O título agora fica dentro da coluna
    
    with col_notificacao:
        # Use um st.button que altera o estado para 'notificacao'
        if st.button("🔔", key="btn_notificacao"):
            st.session_state["pagina"] = "notificacao"
            st.rerun() # Recarrega para mudar de página

    st.markdown("---")
    
    
    st.sidebar.title("Menu")
  
    # Mostrar nome do usuário logado
    if "usuario" in st.session_state:
        st.sidebar.write(f"👤 Usuário: {st.session_state['usuario']}")
    
    # 🔥 NOVO: Mostrar lavanderia na sidebar
    st.sidebar.write(f"🏢 Lavanderia: {nome_lavanderia}")
    
    # Botão de logout
    if st.sidebar.button("🚪 Sair"):
        st.session_state.clear()
        st.rerun()

    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📅 Visualizar Horários", 
        "⏰ Fazer Agendamento", 
        "📋 Minhas Reservas",
        "👤 Meu Perfil",
        "⚠️ Reportar Ocorrência"
    ])

    # ------------------------------------------------------------------
    # TAB 1 - VISUALIZAR HORÁRIOS
    with tab1:
        st.subheader("Horários Disponíveis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            maquinas = get_maquinas_lavanderia(id_lavanderia_logada)
                
            if maquinas:
                opcoes_maquinas = []
                for maquina in maquinas:
                    if maquina.status_maquina != "manutencao":
                        descricao = f"Máquina {maquina.id_maquina} - {maquina.tipo_maquina}"
                        opcoes_maquinas.append(descricao)
                
                if opcoes_maquinas:
                    maquina_selecionada = st.selectbox("Selecione a máquina:", opcoes_maquinas)
                    maquina_id = maquina_selecionada.split(" ")[1]  
                else:
                    st.info("ℹ️ Nenhuma máquina disponível para visualização.")
                    maquina_id = None
            else:
                st.info("ℹ️ Nenhuma máquina cadastrada nesta lavanderia.")
                maquina_id = None
        
        with col2:
            data_selecionada = st.date_input("Selecione a data")
        
        if st.button("🔍 Ver Horários Disponíveis") and maquina_id:
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
        elif not maquina_id:
            st.warning("⚠️ Selecione uma máquina para ver os horários disponíveis.")
    
    # ------------------------------------------------------------------
    # TAB 2 - FAZER AGENDAMENTO
    with tab2:
        st.subheader("Fazer Agendamento")
        
        with st.form("agendamento_form"):
            col1, col2 = st.columns(2)
            
            maquina_id_para_agendar = None

            with col1:
                maquinas = get_maquinas_lavanderia(id_lavanderia_logada)
                    
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
                    st.info("ℹ️ Nenhuma máquina disponível para agendamento.")

                data_agendamento = st.date_input("Data do agendamento", key="agendamento_data")
            
            with col2:
                horarios = [f"{hora:02d}:00" for hora in range(8, 20)]
                hora_agendamento = st.selectbox("Horário de início", horarios)
                
            
            if st.form_submit_button("📅 Fazer Agendamento"):
                if maquina_id_para_agendar: 
                    reserva = controlador_reserva.criar_reserva(
                        maquina_id_para_agendar,
                        usuario_id_logado,
                        data_agendamento.strftime("%Y-%m-%d"),
                        hora_agendamento
                    )
                    
                    if reserva:
                        st.success(f"🎉 Reserva realizada com sucesso! ID: {reserva.id_reserva}")
                        # Limpa cache para refletir nova reserva
                        clear_maquinas_cache(id_lavanderia_logada)
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
        
        reservas_validas = []
        if reservas_todas:
            for r in reservas_todas:
                if r.status_reserva != "ativa":
                    continue

                data_reserva = None
                if isinstance(r.data_reserva, str):
                    try:
                        data_reserva = datetime.strptime(r.data_reserva, "%Y-%m-%d").date()
                    except ValueError:
                        continue
                else:
                    data_reserva = r.data_reserva 

                if data_reserva and data_reserva >= hoje:
                    reservas_validas.append(r)
  

        if reservas_validas:
            st.success(f"📋 Você tem {len(reservas_validas)} reserva(s) ativa(s) (hoje ou no futuro)")
                    
            for reserva in reservas_validas:
                with st.expander(f"Reserva {reserva.id_reserva} - {reserva.data_reserva} às {reserva.hora_inicio}"):
                    col1, col2, col3 = st.columns([3, 1, 1])
                            
                    with col1:
                        st.write(f"**Máquina ID:** {reserva.id_maquina}")
                        st.write(f"**Data:** {reserva.data_reserva}")
                        st.write(f"**Horário:** {reserva.hora_inicio} - {reserva.hora_fim}")
                        st.write(f"**Status:** {reserva.status_reserva}")
                            
                    with col2:
                        if st.button("✏️ Editar", key=f"edit_{reserva.id_reserva}"):
                            st.session_state[f"editando_reserva_{reserva.id_reserva}"] = True
                            st.rerun()
                            
                    with col3:
                        if st.button("❌ Cancelar", key=f"cancel_{reserva.id_reserva}"):
                            if controlador_reserva.cancelar_reserva(reserva.id_reserva, usuario_id_logado):
                                st.success("Reserva cancelada com sucesso!")
                                clear_maquinas_cache(id_lavanderia_logada)
                                st.rerun()
                            else:
                                st.error("Erro ao cancelar reserva.")
                            
                    if st.session_state.get(f"editando_reserva_{reserva.id_reserva}"):
                        st.markdown("---")
                        st.subheader("✏️ Editar Reserva")
                            
                        with st.form(f"form_editar_{reserva.id_reserva}"):
                            col_edit1, col_edit2 = st.columns(2)
                                    
                            maquina_id_edit = None
                            with col_edit1:
                                maquinas = get_maquinas_lavanderia(id_lavanderia_logada)
                                    
                                opcoes_maquinas_editar = []
                                if maquinas:
                                    for maquina in maquinas:
                                        if maquina.status_maquina != "manutencao":
                                            descricao = f"Máquina {maquina.id_maquina} - {maquina.tipo_maquina} ({maquina.capacidade})"
                                            opcoes_maquinas_editar.append(descricao)
                                
                                if opcoes_maquinas_editar:
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
                                    st.info("ℹ️ Nenhuma máquina disponível para edição.")
                                    maquina_id_edit = str(reserva.id_maquina)
                            
                            with col_edit2:
                                if isinstance(reserva.data_reserva, str):
                                    data_valor = datetime.strptime(reserva.data_reserva, "%Y-%m-%d").date()
                                else:
                                    data_valor = reserva.data_reserva
                                
                                nova_data = st.date_input(
                                    "Nova Data",
                                    value=data_valor,
                                    key=f"data_edit_{reserva.id_reserva}"
                                )
                                    
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
                                                        clear_maquinas_cache(id_lavanderia_logada)
                                                        del st.session_state[f"editando_reserva_{reserva.id_reserva}"]
                                                        st.rerun()
                                                    else:
                                                        st.error("❌ Não foi possível criar a nova reserva. Horário pode estar ocupado.")
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
    
    # ------------------------------------------------------------------
    # TAB 5 - REPORTAR OCORRÊNCIA
    with tab5:
        st.subheader("⚠️ Reportar uma Ocorrência")
        st.write("Encontrou algo que não está funcionando? Nos avise.")

        with st.form("form_reportar_ocorrencia", clear_on_submit=True):
            
            maquinas = get_maquinas_lavanderia(id_lavanderia_logada)
            
            opcoes_maquinas_reporte = ["Nenhuma (Problema geral/Outro)"]
            
            if maquinas:
                for maquina in maquinas:
                    descricao = f"Máquina {maquina.id_maquina} - {maquina.tipo_maquina} ({maquina.status_maquina})"
                    opcoes_maquinas_reporte.append(descricao)
            
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
                id_maquina_reporte = None
                
                if maquina_selecionada_reporte != "Nenhuma (Problema geral/Outro)":
                    try:
                        id_maquina_reporte = maquina_selecionada_reporte.split(" ")[1]
                    except Exception as e:
                        st.error("Erro ao selecionar a máquina.")
                        return

                if not descricao_ocorrencia:
                    st.warning("Por favor, descreva a ocorrência antes de enviar.")
                else:
                    nova_ocorrencia = controlador_ocorrencia.salvar_ocorrencia(
                        id_maquina_reporte,
                        descricao_ocorrencia,
                        nome_usuario_logado,
                        id_lavanderia_logada
                    )
                    
                    if nova_ocorrencia:
                        st.success(f"✅ Ocorrência reportada com sucesso (ID: {nova_ocorrencia.id_problema}). Obrigado!")
                    else:
                        st.error("❌ Erro ao reportar a ocorrência. Tente novamente.")
