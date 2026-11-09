# visao/tela_notificacao_adm_predio.py

import streamlit as st

# Importa o Controlador de Notificações
try:
    from controladores.controlador_notificacao import ControladorNotificacao
    controlador_notificacao = ControladorNotificacao()
except ImportError as e:
    st.error(f"Erro ao carregar o Controlador de Notificações: {e}")
    controlador_notificacao = None


def tela_notificacao_adm_predio():
    st.title("Central de Notificações")
    st.markdown("---")

    if not controlador_notificacao:
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


    try:
        notificacoes = controlador_notificacao.listar_notificacoes_do_usuario(id_usuario_logado)
        
    except Exception as e:
        st.error(f"Erro ao buscar notificações no banco de dados: {str(e)}")
        notificacoes = []

    
    # Separação das notificações
    nao_lidas = [n for n in notificacoes if n.get('status', '').lower() == 'nao_lido']
    lidas = [n for n in notificacoes if n.get('status', '').lower() == 'lido']

    st.info(f"Você tem **{len(nao_lidas)}** notificação(ões) não lida(s) de um total de {len(notificacoes)}.")

    if not notificacoes:
        st.success("Nenhuma notificação encontrada no momento.")
        st.markdown("---")
        
    st.subheader("Novas (Não Lidas)")
    st.markdown("---")

    # Exibição de Notificações NÃO LIDAS (com o botão de ação)
    if nao_lidas:
        for notif in nao_lidas:
            id_notif = notif['id_notificacao']
            
            # Container de destaque para não lidas
            with st.container(border=True):
                st.markdown(f"**{notif['mensagem']}**")
                st.caption(f"Enviada em: {notif['data_envio']}")
                
                # Botão de Ação para 'Marcar como Lida'
                # Usa o ID da notificação como chave para o botão
                if st.button("Marcar como Lida", key=f"lida_{id_notif}", use_container_width=False):
                    st.session_state.marcar_lida = id_notif
                    st.rerun()
    else:
        st.success("Nenhuma notificação nova.")

    st.subheader("Lidas")
    st.markdown("---")
    
    # Exibição de Notificações LIDAS (em um expansível)
    if lidas:
        for notif in lidas:
            data_envio = notif['data_envio'].split(' ')[0] # Pega só a data
            
            with st.expander(f"Notificação Lida - {data_envio}"):
                st.write(f"**Mensagem:** {notif['mensagem']}")
                st.caption(f"Status: Lida | Enviada em: {notif['data_envio']}")
    else:
        st.markdown("_Nenhuma notificação marcada como lida._")

    st.markdown("---")
    
    # Determina o botão de retorno
    pagina_retorno = st.session_state.get("pagina_anterior", "tela_adm_predio")
    
    if pagina_retorno == "tela_adm_predio":
        texto_botao = "Voltar para a Área do Administrador"
    elif pagina_retorno == "tela_morador":
        texto_botao = "Voltar para a Área do Morador"
    else:
        texto_botao = "Voltar"

    if st.button(texto_botao, use_container_width=True, key="voltar_principal"):
        st.session_state["pagina"] = pagina_retorno
        if "subpagina_adm_predio" in st.session_state:
            del st.session_state["subpagina_adm_predio"] 
        
        st.rerun()