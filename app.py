# View - app.py - Inicia a aplicação.
# Interface em Streamlit, recebe o input do usuário, chama o controller, mostra o feedback.

import streamlit as st
from visao.tela_login import tela_login
from visao.tela_morador import tela_morador
from visao.tela_adm_predio import tela_adm_predio
from visao.tela_adm_plataforma import tela_adm_plataforma


# Header que irá aparecer no início da tela de login/cadastro:
def header():
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


# Execução Principal:
if "logado" not in st.session_state:
    st.session_state["logado"] = False
    st.session_state["dados_carregados"] = False

if not st.session_state["logado"]:    
    #se não tiver logado:
    header()
    tela_login()

else:   
    #se tiver logado:
    if st.session_state["dados_carregados"] is False and "id_usuario" in st.session_state:
        try:
            from controladores.controlador_usuario import ControladorUsuario
            controlador_usuario = ControladorUsuario()
            
            lista_ids = controlador_usuario.obter_lavanderias_usuario(st.session_state["id_usuario"])
            
            if lista_ids:
                st.session_state["lista_ids_lavanderia"] = lista_ids
        
            st.session_state["dados_carregados"] = True     
        except Exception as e:
            st.error(f"Erro ao carregar associações de lavanderia: {e}")

    if st.session_state.pagina == "tela_adm_plataforma":
        tela_adm_plataforma()
    elif st.session_state.pagina == "tela_adm_predio":
        tela_adm_predio()
    elif st.session_state.pagina == "tela_morador":
        tela_morador()
