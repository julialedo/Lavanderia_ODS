# View - app.py - Inicia a aplicação.
# Interface em Streamlit, recebe o input do usuário, chama o controller, mostra o feedback.

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from visao.tela_login import tela_login
from visao.tela_morador import tela_morador
from visao.tela_adm_predio import tela_adm_predio
from visao.tela_adm_plataforma import tela_adm_plataforma


def header_global():
    st.markdown(
        """
        <div style='text-align: center;'>
            <h1>🧺 Gerenciador de Lavanderias Coletivas</h1>
            <p><em>Sistema de reservas e controle de uso de lavanderias</em></p>
        </div>
        <hr>
        """,
        unsafe_allow_html=True
    )

def go_to_home():
    st.session_state.page = "home"



# Execução Principal:
if "logado" not in st.session_state:
    st.session_state["logado"] = False

header_global()
if not st.session_state["logado"]:
    tela_login()
else:
    if st.session_state.pagina == "tela_adm_plataforma":
        tela_adm_plataforma()
    elif st.session_state.pagina == "tela_adm_predio":
        tela_adm_predio()
    elif st.session_state.pagina == "tela_morador":
        tela_morador()
