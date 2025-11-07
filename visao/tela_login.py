# View - tela_login.py
# Interface em Streamlit, recebe o input do usuário, chama o controller, mostra o feedback.

import streamlit as st  # 👈 IMPORT PRECISA VIR PRIMEIRO!
from controladores.controlador_usuario import ControladorUsuario

# Inicialização do controlador:
controlador_usuario = ControladorUsuario()


# Tela de Login:
def tela_login():
    # Inicializar session_state se não existir
    if "mostrar_cadastro" not in st.session_state:
        st.session_state.mostrar_cadastro = False
    
    # Verificar se deve mostrar cadastro - AGORA DEPOIS DO IMPORT
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
    
    # Seção de Login normal
    st.title("🔐 Login - Sistema de Lavanderia")
    st.markdown("---")

    col1, col2 = st.columns([2, 1])
    
    with col1:
        email = st.text_input("E-mail")
        senha = st.text_input("Senha", type="password")

        if st.button("Entrar", use_container_width=True):              
            try:
                usuario = controlador_usuario.login(email, senha)

                st.session_state["logado"] = True
                st.session_state["usuario"] = usuario["nome"]
                st.session_state["usuario_dados"] = usuario
                st.session_state["tipo"] = usuario["tipo_usuario"]
                st.session_state["id_lavanderia"] = usuario.get("id_lavanderia")

                st.success(f"Bem-vindo, {usuario['nome']}!")

                if usuario["tipo_usuario"] == "adm_plataforma":
                    st.session_state["pagina"] = "tela_adm_plataforma"
                elif usuario["tipo_usuario"] == "adm_predio":
                    st.session_state["pagina"] = "tela_adm_predio"
                else:
                    st.session_state["pagina"] = "tela_morador"

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
