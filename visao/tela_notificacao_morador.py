# visao/tela_notificacao_morador.py

import streamlit as st
# ... (outros imports, se houver)

def tela_notificacao_morador():
    st.title("🔔 Central de Notificações")
    st.markdown("---")
    st.write("Esta é a sua página de notificações.")
    
    # 🚨 MUDANÇA ESSENCIAL AQUI:
    # O app.py usa st.session_state.pagina para rotear.
    # A tela de destino para o Morador é "tela_morador".
    if st.button("⬅️ Voltar para a Área do Morador"):
        st.session_state["pagina"] = "tela_morador" # Altera a chave CORRETA
        st.rerun()