# visao/tela_notificacao_morador.py

import streamlit as st

# Importa o Controlador de Notificações
try:
    from controladores.controlador_notificacao import ControladorNotificacao
    controlador_notificacao = ControladorNotificacao()
except ImportError as e:
    st.error(f"Erro ao carregar o Controlador de Notificações: {e}")
    controlador_notificacao = None


def tela_notificacao_morador():
    st.title("Minhas Notificações")
    st.markdown("---")

    if not controlador_notificacao:
        st.warning("Sistema de notificações indisponível no momento.")
        return

    id_usuario_logado = None
    
    if st.session_state.get("id_usuario"):
        id_usuario_logado = st.session_state.get("id_usuario")
    elif st.session_state.get("usuario_dados") and st.session_state.usuario_dados.get("id_usuario"):
        id_usuario_logado = st.session_state.usuario_dados.get("id_usuario")
    elif st.session_state.get("usuario") and st.session_state.usuario.get("id_usuario"):
        id_usuario_logado = st.session_state.usuario.get("id_usuario") 
    
    if not id_usuario_logado:
        st.error("Usuário não logado. Por favor, retorne para o Login.")
        st.markdown("---")
        if st.button("Retornar ao Login", use_container_width=True):
            st.session_state["pagina"] = "tela_login"
            st.rerun()
        return

    # Lógica de Ação: Marcar como Lida (Chamada do Controlador)
    if 'marcar_lida' in st.session_state:
        id_notificacao_lida = st.session_state.marcar_lida
        if controlador_notificacao.marcar_como_lida(id_notificacao_lida):
            st.toast("Notificação marcada como lida!", icon='')
        else:
            st.error("Erro ao marcar a notificação como lida.")
            
        del st.session_state.marcar_lida # Limpa o estado e força o rerun para recarregar a lista
        st.rerun()

    # Botão para marcar todas como lidas
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("Marcar Todas como Lidas", type="secondary", use_container_width=True):
            # Implementar lógica para marcar todas como lidas
            st.info("Funcionalidade em desenvolvimento")
            # Para implementar: criar função no controlador para marcar todas como lidas

    try:
        notificacoes = controlador_notificacao.listar_notificacoes_do_usuario(id_usuario_logado)
        
    except Exception as e:
        st.error(f"Erro ao buscar notificações no banco de dados: {str(e)}")
        notificacoes = []

    
    # Separação das notificações
    nao_lidas = [n for n in notificacoes if n.get('status', '').lower() == 'nao_lido']
    lidas = [n for n in notificacoes if n.get('status', '').lower() == 'lido']

    # Estatísticas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Novas", len(nao_lidas))
    with col2:
        st.metric("Lidas", len(lidas))
    with col3:
        st.metric("Total", len(notificacoes))

    st.markdown("---")
    
    if not notificacoes:
        st.success("Nenhuma notificação encontrada no momento.")
        st.markdown("---")
        
    # Seção de Notificações NÃO LIDAS
    if nao_lidas:
        st.subheader("Novas Notificações")
        st.markdown("---")
        
        for notif in nao_lidas:
            id_notif = notif['id_notificacao']
            
            # Container com destaque visual para não lidas
            with st.container(border=True):
                col_icon, col_content, col_action = st.columns([0.5, 4, 1.5])
                
                with col_icon:
                    st.markdown("<div style='text-align: center; padding-top: 10px;'></div>", unsafe_allow_html=True)
                
                with col_content:
                    st.markdown(f"**{notif['mensagem']}**")
                    st.caption(f"Enviada em: {notif['data_envio']}")
                
                with col_action:
                    if st.button("Lida", key=f"lida_{id_notif}", use_container_width=True):
                        st.session_state.marcar_lida = id_notif
                        st.rerun()
    elif notificacoes:
        st.success("Todas as notificações foram lidas!")
        st.markdown("---")
    
    # Seção de Notificações LIDAS
    if lidas:
        st.subheader("Notificações Lidas")
        st.markdown("---")
        
        # Opção para mostrar/esconder notificações lidas
        with st.expander(f"Ver histórico ({len(lidas)} notificações lidas)", expanded=False):
            for i, notif in enumerate(lidas):
                data_envio = notif['data_envio']
                
                with st.container(border=True):
                    col_icon, col_content = st.columns([0.5, 5.5])
                    
                    with col_icon:
                        st.markdown("<div style='text-align: center; padding-top: 10px;'></div>", unsafe_allow_html=True)
                    
                    with col_content:
                        st.markdown(f"**{notif['mensagem']}**")
                        st.caption(f"Lida em: {data_envio}")
                
                if i < len(lidas) - 1:
                    st.markdown("<hr style='margin: 5px 0;'>", unsafe_allow_html=True)

    st.markdown("---")
    
    # Botões de ação
    col1, col2 = st.columns(2)
    
    with col1:
        # Botão para atualizar a lista
        if st.button("Atualizar Notificações", use_container_width=True):
            st.rerun()
    
    with col2:
        # Botão de retorno
        pagina_retorno = st.session_state.get("pagina_anterior", "tela_morador")
        texto_botao = "Voltar para Área do Morador"
        
        if st.button(texto_botao, use_container_width=True, key="voltar_morador"):
            st.session_state["pagina"] = pagina_retorno
            st.rerun()

