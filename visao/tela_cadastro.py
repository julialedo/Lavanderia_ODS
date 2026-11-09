# View - tela_cadastro.py
# Interface em Streamlit, recebe o input do usuário e chama o controller.

import streamlit as st

# Controlador inicializado e armazenado uma única vez:
@st.cache_resource
def get_controlador_usuario():
    try:
        from controladores.controlador_usuario import ControladorUsuario
        return ControladorUsuario()
    except ImportError as e:
        st.error(f"Erro Crítico: Falha ao carregar ControladorUsuario na Tela de Cadastro. Detalhes: {e}")
        return None

controlador_usuario = get_controlador_usuario()


# Tela para morador se cadastrar:
def tela_cadastro():
    st.title("Cadastro de Morador")
    st.info("Preencha os dados abaixo para se cadastrar no sistema de Lavanderias Coletivas.")
    
    # Cache da lista de lavanderias:
    if 'lavanderias_cache' not in st.session_state:
        try:
            lavanderias = controlador_usuario.listar_lavanderias()
            st.session_state.lavanderias_cache = {
                lav.nome: lav.id_lavanderia for lav in lavanderias
            }
        except Exception as e:
            st.error(f"Não foi possível carregar a lista de lavanderias. Detalhes: {e}")
            st.session_state.lavanderias_cache = {}
    
    opcoes = st.session_state.lavanderias_cache
    
    with st.form("form_cadastro"):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome Completo*")
        with col2:
            telefone = st.text_input("Telefone*") 

        email = st.text_input("Email*")
       
        col1, col2 = st.columns(2)
        with col1:
            senha = st.text_input("Senha*", type="password")
        with col2:
            confirmar_senha = st.text_input("Confirmar Senha*", type="password")
        
        lavanderia_nome = st.selectbox(
            "Lavanderia*",
            options=list(opcoes.keys()),
            index=None,
            placeholder="Selecione uma opção."
        )
        id_lavanderia = opcoes.get(lavanderia_nome)
        
        st.caption(" *Campos obrigatórios.")
        
        if st.form_submit_button("Cadastrar", use_container_width=True):
            if not controlador_usuario:
                st.error("Sistema temporariamente indisponível")
                return
                
            if senha != confirmar_senha:
                st.error("As senhas não coincidem!")
                return
        
            sucesso, mensagem = controlador_usuario.cadastrar_morador(
                nome=nome,
                email=email,
                senha=senha,
                telefone=telefone,
                id_lavanderia=id_lavanderia
            )
            
            if sucesso:
                st.success(mensagem)
                st.balloons()
                # Limpa cache após cadastro bem-sucedido:
                if 'lavanderias_cache' in st.session_state:
                    del st.session_state.lavanderias_cache
            else:
                st.error(f"Erro no cadastro: {mensagem}")   
