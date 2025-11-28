# View - tela_login.py
import streamlit as st 

# Controladores inicializados uma vez
try:
    from controladores.controlador_usuario import ControladorUsuario
    controlador_usuario = ControladorUsuario()
except ImportError:
    controlador_usuario = None

def tela_login():
    # Inicialização simplificada
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
                    "id_lavanderia": usuario.get("id_lavanderia")
                })

                st.success(f"Bem-vindo, {usuario['nome']}!")

                # Determinar página baseada no tipo de usuário
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
        
        if st.button("📝 Criar Conta", use_container_width=True):
            st.session_state.mostrar_cadastro = True
            st.rerun()
