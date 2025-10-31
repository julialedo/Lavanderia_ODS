# View - tela_login.py
# Interface em Streamlit, recebe o input do usuário, chama o controller, mostra o feedback.

import streamlit as st
from controladores.controlador_usuario import ControladorUsuario

# Inicialização do controlador:
controlador_usuario = ControladorUsuario()


# Tela de Login:
def tela_login():
    st.title("🔐 Login - Sistema de Lavanderia")
    st.markdown("---")

    email = st.text_input("E-mail")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar", use_container_width=True):              
        try:
            usuario = controlador_usuario.login(email, senha)   # chama login no controlador

            # ✅ Armazena todos os dados do usuário logado
            st.session_state["logado"] = True
            st.session_state["usuario"] = usuario["nome"]
            st.session_state["usuario_dados"] = usuario  # 👈 agora o sistema inteiro tem acesso
            st.session_state["tipo"] = usuario["tipo_usuario"]
            st.session_state["id_lavanderia"] = usuario.get("id_lavanderia")

            st.success(f"Bem-vindo, {usuario['nome']}!")

            # Redirecionamento automático com base no tipo de usuário
            if usuario["tipo_usuario"] == "adm_plataforma":
                st.session_state["pagina"] = "tela_adm_plataforma"
            elif usuario["tipo_usuario"] == "adm_predio":
                st.session_state["pagina"] = "tela_adm_predio"
            else:
                st.session_state["pagina"] = "tela_morador"

            st.rerun()

        except Exception as e:
            st.error(str(e))
