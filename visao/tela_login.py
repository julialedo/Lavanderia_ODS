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
            usuario = controlador_usuario.login(email, senha)   #chama login em controlador

            #salva nome, tipo... em estados
            st.session_state["logado"] = True
            st.session_state["nome"] = usuario["nome"]
            st.session_state["tipo"] = usuario["tipo_usuario"]
            st.session_state["id_lavanderia"] = usuario.get("id_lavanderia")

            if "id_usuario" in usuario:
                st.session_state["id_usuario"] = usuario["id_usuario"]
            else:
                st.error("Erro: Não obteve o ID do usuário")
                return

            st.success(f"Bem-vindo, {usuario['nome']}!")

            if usuario["tipo_usuario"] == "adm_plataforma":
                st.session_state["pagina"] = "tela_adm_plataforma"  #salva estado de qual pagina deve ir
            elif usuario["tipo_usuario"] == "adm_predio":
                st.session_state["pagina"] = "tela_adm_predio"
            else:
                st.session_state["pagina"] = "tela_morador"

            st.rerun()
        except Exception as e:
            st.error(str(e))