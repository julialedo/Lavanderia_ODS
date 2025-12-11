# View - tela_morador.py
# Interface em Streamlit, recebe o input do usuário, chama o controller, mostra o feedback.

import streamlit as st
from datetime import datetime

# --- CONTROLADORES: INICIALIZAÇÃO ÚNICA COM CACHE ---
@st.cache_resource
def get_controladores_morador():
    """Inicializa e armazena controladores complexos uma única vez."""
    try:
        from controladores.controlador_reserva import ControladorReserva
        from controladores.controlador_maquina import ControladorMaquina
        from controladores.controlador_usuario import ControladorUsuario
        from controladores.controlador_ocorrencia import ControladorOcorrencia
        from controladores.controlador_plataforma import ControladorPlataforma
        
        return {
            "reserva": ControladorReserva(),
            "maquina": ControladorMaquina(),
            "usuario": ControladorUsuario(),
            "ocorrencia": ControladorOcorrencia(),
            "plataforma": ControladorPlataforma()
        }
    except ImportError as e:
        # Apenas imprime o erro, para não quebrar a UI
        print(f"Erro ao carregar controladores: {e}") 
        return None

CONTROLADORES = get_controladores_morador()
if CONTROLADORES:
    controlador_reserva = CONTROLADORES["reserva"]
    controlador_maquina = CONTROLADORES["maquina"]
    controlador_usuario = CONTROLADORES["usuario"]
    controlador_ocorrencia = CONTROLADORES["ocorrencia"]
    controlador_plataforma = CONTROLADORES["plataforma"]
else:
    controlador_reserva = None
    controlador_maquina = None
    controlador_usuario = None
    controlador_ocorrencia = None
    controlador_plataforma = None

# --- FUNÇÕES DE CACHE OTIMIZADAS ---

@st.cache_data(ttl=3600) # Cache de 1 hora
def get_lavanderia_nome(_id_lavanderia):  
    """Cache do nome da lavanderia (Estático)"""
    if not _id_lavanderia or not controlador_plataforma:
        return "Sua Lavanderia"
    try:
        lavanderia_info = controlador_plataforma.obter_lavanderia_por_id(_id_lavanderia)
        return lavanderia_info.get("nome", "Sua Lavanderia") if lavanderia_info else "Sua Lavanderia"
    except:
        return "Sua Lavanderia"

@st.cache_data(ttl=60) # Cache de 1 minuto para máquinas (Semi-estático)
def get_maquinas_lavanderia(_id_lavanderia): 
    """Cache para máquinas da lavanderia"""
    if not _id_lavanderia or not controlador_maquina:
        return []
    try:
        maquinas = controlador_maquina.listar_por_lavanderia(_id_lavanderia)
        return maquinas
    except:
        return []

def clear_maquinas_cache(id_lavanderia): 
    """Limpar cache de maquinas"""
    get_maquinas_lavanderia.clear()
    
# Cache com TTL de 5 segundos para o status em tempo real
@st.cache_data(ttl=5) 
def get_status_em_tempo_real(_id_lavanderia, _id_usuario_logado):
    """Cache de 5s para evitar consultas massivas ao BD no Dashboard."""
    if not controlador_maquina:
        return []
    try:
        return controlador_maquina.obter_status_em_tempo_real(
            _id_lavanderia, _id_usuario_logado
        )
    except Exception as e:
        print(f"Erro ao carregar status em tempo real: {e}")
        return []


# Exibe ciclo ativo se houver
def exibir_status_usuario_topo(maquinas_status: list):
    
    ciclo_ativo = next((m for m in maquinas_status if m.get('is_my_reservation')), None)
    st.subheader("Seu Ciclo de Lavagem:")
    
    if ciclo_ativo:
        status = ciclo_ativo['status']
        etapa = ciclo_ativo['etapa_ciclo']
        progresso = ciclo_ativo['progresso'] / 100
        tempo_restante = ciclo_ativo['tempo_restante']
        codigo_maquina = ciclo_ativo['codigo_maquina']

        st.info(f"✨ **Máquina {codigo_maquina}** está **{etapa}** (Status: {status})")
        
        # Display Progress Bar (RF3)
        st.progress(progresso, text=f"**{int(progresso * 100)}% concluído**")
        st.write(f"Tempo restante: **{tempo_restante}**")
        
        # Link rápido para editar a reserva (opcional)
        if st.button("Gerenciar Minha Reserva", key="btn_gerenciar_ciclo"):
             st.session_state["subpagina_morador"] = "minhas_reservas" 
             st.rerun()

    else:
        st.info("Você **não** está utilizando nenhuma máquina no momento ou seu ciclo já terminou.")
        st.caption("Abaixo, você pode selecionar uma máquina livre para reservar.")


def exibir_grid_maquinas(maquinas_status: list): #Exibe todas as máquinas e os status delas
    
    st.subheader("Todas as Máquinas da Lavanderia")
    
    # Criar um layout em colunas para uma melhor visualização (3 colunas por linha)
    N_COLS = 3
    cols = st.columns(N_COLS) 
    
    for i, maquina in enumerate(maquinas_status):
        col = cols[i % N_COLS]
        
        with col:
            # Usar st.container para dar um visual de 'card'
            with st.container(border=True):
                st.markdown(f"**{maquina['tipo_maquina']}** {maquina['codigo_maquina']}", 
                            unsafe_allow_html=True)
                
                status = maquina['status']
                
                if status == "Livre" or "Livre" in status:
                    st.success(f"✅ Status: **Livre**")
                    # Opção de escolher/reservar (RF1)
                    button_key = f"reserva_{maquina['id_maquina']}_{i}"
                    if st.button("Reservar", key=button_key, use_container_width=True):
                        st.session_state["subpagina_morador"] = "reserva" 
                        st.session_state["maquina_selecionada_reserva"] = maquina['id_maquina']
                        st.rerun()

                elif status == "Em Uso":
                    # Marca a reserva do próprio morador com um destaque
                    if maquina['is_my_reservation']:
                        st.warning("🌟 **Em Uso (Seu Ciclo)**")
                        st.caption(f"Fim em: {maquina['tempo_restante']}")
                    else:
                        st.warning("🔴 **Em Uso**")
                        st.caption(f"Fim em breve...")

                elif status == "Em Manutenção":
                    st.error("🔧 **Em Manutenção**")
                    
                else: # Outros status, como Agendada
                    st.info(f"⏳ **{status}**")
                    
                st.caption(f"Capacidade: {maquina['capacidade']}")


def tela_morador():
    # Verificação inicial de controladores
    if not CONTROLADORES:
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
    
    # Otimizado: Busca nome da lavanderia com cache
    nome_lavanderia = get_lavanderia_nome(id_lavanderia_logada)
    
    # NOVO: SIDEBAR (Barra Lateral Esquerda)
    with st.sidebar:
        st.title("Menu do Morador")
        st.write(f"👤 **{st.session_state.get('usuario', 'Morador')}**")
        st.write(f"🏢 {nome_lavanderia}")
        st.markdown("---")
        
        if st.button("🚪 Sair"):
            st.session_state.clear()
            st.rerun()

    # Cabeçalho Principal (sem Sidebar)
    col_vazia, col_titulo, col_notificacao = st.columns([1, 8, 1])
    
    with col_titulo:
        st.title(f"👤 Área do Morador")
    
    with col_notificacao:
        # Usa um st.button que altera o estado para 'notificacao'
        if st.button("🔔", key="btn_notificacao"):
            st.session_state["pagina"] = "tela_notificacao_morador"
            st.rerun() 

    st.markdown("---")
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🏠 Home",
        "📅 Visualizar Horários", 
        "⏰ Fazer Agendamento", 
        "📋 Minhas Reservas",
        "👤 Meu Perfil",
        "⚠️ Reportar Ocorrência"
    ])

    # ------------------------------------------------------------------
    # TAB 1 - HOME / STATUS
    with tab1:
        st.title("🧺 Dashboard da Lavanderia")
        id_lavanderia = st.session_state.get("id_lavanderia")
        id_usuario_logado = st.session_state.get("usuario_dados", {}).get("id_usuario")
        
        # OTIMIZAÇÃO DE DESEMPENHO: Usa cache de 5s para o status dinâmico
        maquinas_status = get_status_em_tempo_real(
            id_lavanderia, id_usuario_logado
        )

        exibir_status_usuario_topo(maquinas_status)
        st.markdown("---") 
        exibir_grid_maquinas(maquinas_status)
       
    # ------------------------------------------------------------------
    # TAB 2 - VISUALIZAR HORÁRIOS
    with tab2:
        st.subheader("Horários Disponíveis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            maquinas = get_maquinas_lavanderia(id_lavanderia_logada) # Otimizado: Usa função de cache
                
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
            # Não usa cache, deve ser dinâmico
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
    # TAB 3 - FAZER AGENDAMENTO
    with tab3:
        st.subheader("Fazer Agendamento")
        
        with st.form("agendamento_form"):
            col1, col2 = st.columns(2)
            
            maquina_id_para_agendar = None

            with col1:
                maquinas = get_maquinas_lavanderia(id_lavanderia_logada) # Otimizado: Usa função de cache
                    
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
                        clear_maquinas_cache(id_lavanderia_logada) # Otimizado: Limpa cache após mudança de estado
                    else:
                        st.error("❌ Erro ao fazer reserva. Horário indisponível ou dados inválidos.")
                else:
                    st.error("❌ Nenhuma máquina selecionada para o agendamento.")
    
    # ------------------------------------------------------------------
    # TAB 4 - MINHAS RESERVAS
    with tab4:
        st.subheader("📋 Minhas Reservas")
        
        hoje = datetime.now().date()
        
        # Não usa cache, deve ser dinâmico
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
                                clear_maquinas_cache(id_lavanderia_logada) # Otimizado: Limpa cache
                                st.rerun()
                            else:
                                st.error("Erro ao cancelar reserva.")
                            
                    if st.session_state.get(f"editando_reserva_{reserva.id_reserva}"):
                        with st.form(f"form_editar_{reserva.id_reserva}"):
                            col_edit1, col_edit2 = st.columns(2)
                                    
                            maquina_id_edit = None
                            with col_edit1:
                                maquinas = get_maquinas_lavanderia(id_lavanderia_logada) # Otimizado: Usa função de cache
                                    
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
                                    # Não usa cache, deve ser dinâmico
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
                                                        clear_maquinas_cache(id_lavanderia_logada) # Otimizado: Limpa cache
                                                        del st.session_state[f"editando_reserva_{reserva.id_reserva}"]
                                                        st.rerun()
                                                    else:
                                                        st.error("❌ Não foi possível criar a nova reserva. Horário pode estar ocupado.")
                                                        # Tenta recriar a reserva original se a nova falhar
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
    # TAB 5 - MEU PERFIL
    with tab5:
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
                            # Atualiza a sessão
                            st.session_state["usuario_dados"]["nome"] = nome
                            st.session_state["usuario_dados"]["email"] = email
                            st.session_state["usuario_dados"]["telefone"] = telefone
                            st.rerun()
                    except Exception as e:
                        st.error(f"❌ Erro: {str(e)}")
    
    # ------------------------------------------------------------------
    # TAB 6 - REPORTAR OCORRÊNCIA
    with tab6:
        st.subheader("⚠️ Reportar uma Ocorrência")
        st.write("Encontrou algo que não está funcionando? Nos avise.")

        with st.form("form_reportar_ocorrencia", clear_on_submit=True):
            
            maquinas = get_maquinas_lavanderia(id_lavanderia_logada) # Otimizado: Usa função de cache
            
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
