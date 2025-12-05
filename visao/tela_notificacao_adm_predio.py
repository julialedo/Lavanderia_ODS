# visao/tela_notificacao_adm_predio.py

import streamlit as st
# ... (outros imports, se houver)

def tela_notificacao_adm_predio():
    st.title("🔔 Central de Notificações")
    st.markdown("---")
    st.write("Esta é a sua página de notificações.")

    if st.button("⬅️ Voltar para a Área do Administrador"):
        st.session_state["pagina"] = "tela_adm_predio" # Altera a chave CORRETA
        st.rerun()