# View - app.py - Inicia a aplicação.
# Interface em Streamlit, recebe o input do usuário, chama o controller, mostra o feedback.

import streamlit as st
from visao.tela_login import tela_login
from visao.tela_morador import tela_morador
from visao.tela_adm_predio import tela_adm_predio
from visao.tela_adm_plataforma import tela_adm_plataforma


#Header que irá aparecer no início da tela
def header_global():
    st.markdown("""
    <style>
        .block-container {
            padding-top: 1.5rem !important;
        }
    </style>
""", unsafe_allow_html=True)
    
    st.markdown(
        """
        <div style='text-align: center;'>
            <h1>🧺 Lavanderias Coletivas</h1>
            <p><em>Sistema de reservas e controle de uso de lavanderias.</em></p>
        </div>
        <hr>
        """,
        unsafe_allow_html=True
    )
    

def go_to_home():
    st.session_state.page = "home"


#Execução Principal:
if "logado" not in st.session_state:
    st.session_state["logado"] = False

header_global()
if not st.session_state["logado"]:
    tela_login()
else:
    # 🔥 ADICIONAR: Carregar ID da lavanderia se não estiver na session
    if "id_lavanderia" not in st.session_state and "id_usuario" in st.session_state:
        from controladores.controlador_usuario import ControladorUsuario
        controlador_usuario = ControladorUsuario()
        id_lavanderia = controlador_usuario.obter_lavanderia_usuario(st.session_state["id_usuario"])
        if id_lavanderia:
            st.session_state["id_lavanderia"] = id_lavanderia
    
    if st.session_state.pagina == "tela_adm_plataforma":
        tela_adm_plataforma()
    elif st.session_state.pagina == "tela_adm_predio":
        tela_adm_predio()
    elif st.session_state.pagina == "tela_morador":
        tela_morador()
