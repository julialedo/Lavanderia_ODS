# View - tela_login.py
# Interface em Streamlit, recebe o input do usuário e chama o controller.

import streamlit as st 

# --- CONTROLADORES: INICIALIZAÇÃO ÚNICA COM CACHE ---
@st.cache_resource
def get_controlador_usuario():
    """Inicializa e armazena o ControladorUsuario uma única vez."""
    try:
        from controladores.controlador_usuario import ControladorUsuario
        return ControladorUsuario()
    except ImportError as e:
        # st.error(f"❌ Erro Crítico: Falha ao carregar ControladorUsuario. Detalhes: {e}")
        return None

controlador_usuario = get_controlador_usuario()


# Tela de login: OK
def tela_login():
    
    if not controlador_usuario:
        st.error("❌ Sistema Crítico Indisponível. Tente novamente mais tarde.")
        return

    if "mostrar_cadastro" not in st.session_state:
        st.session_state.mostrar_cadastro = False
        
    if st.session_state.mostrar_cadastro:
        try:
            from visao.tela_cadastro import tela_cadastro
            tela_cadastro()
            if st.button("← Voltar para Login"):
                st.session_state.mostrar_cadastro = False
                st.rerun()
            return
        except ImportError:
            st.error("Erro: Tela de cadastro não encontrada")
            st.session_state.mostrar_cadastro = False
            st.rerun()
    
    # Seção de Login
    st.title("🔐 Login - Sistema de Lavanderia")
    st.markdown("---")

    col1, col2 = st.columns([2, 1])
    with col1:
        email = st.text_input("E-mail")
        senha = st.text_input("Senha", type="password")

        if st.button("Entrar", use_container_width=True):              
            if not controlador_usuario:
                st.error("Sistema temporariamente indisponível")
                return
            try:
                usuario = controlador_usuario.login(email, senha)
                st.session_state.update({
                    "logado": True,
                    "usuario": usuario["nome"],
                    "usuario_dados": usuario,
                    "tipo": usuario["tipo_usuario"],
                })

                if usuario["tipo_usuario"] == "adm_predio":
                    lista_ids = controlador_usuario.obter_lavanderias_usuario(usuario["id_usuario"])
                    
                    st.session_state["lista_ids_lavanderia"] = lista_ids
                    
                    if lista_ids:
                        st.session_state["id_lavanderia_ativa"] = lista_ids[0]
                    else:
                        st.session_state["id_lavanderia_ativa"] = None
                elif usuario["tipo_usuario"] == "morador":
                       lista_ids = controlador_usuario.obter_lavanderias_usuario(usuario["id_usuario"])
                       st.session_state["id_lavanderia"] = lista_ids[0] if lista_ids else None

                st.success(f"Bem-vindo, {usuario['nome']}!")

                # Determinar página baseada no tipo de usuário:
                paginas = {
                    "adm_plataforma": "tela_adm_plataforma",
                    "adm_predio": "tela_adm_predio"
                }
                st.session_state["pagina"] = paginas.get(
                    usuario["tipo_usuario"], "tela_morador"
                )
                st.rerun()

            except Exception as e:
                st.error(str(e))
    
    with col2:
        st.markdown("---")
        st.subheader("Novo por aqui?")
        st.write("Cadastre-se como morador")
        
        if st.button("Criar Conta", use_container_width=True):
            st.session_state.mostrar_cadastro = True
            st.rerun()
