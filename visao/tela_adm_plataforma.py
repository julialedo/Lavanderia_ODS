# View - tela_adm_plataforma.py
# Interface em Streamlit, recebe o input do usuário, chama o controller, mostra o feedback.

import streamlit as st
from controladores.controlador_plataforma import ControladorPlataforma

# Inicialização dos controladores:
controlador_plataforma = ControladorPlataforma()


# Tela inicial do Administrador da Plataforma:
def tela_adm_plataforma():
    
    st.title("🧺 Administração da Plataforma")

    st.sidebar.title("Menu")
    # Mostrar nome do usuário logado
    if "usuario" in st.session_state:
        st.sidebar.write(f"👤 Usuário: {st.session_state['usuario']}")
    # Botão de logout
    if st.sidebar.button("🚪 Sair"):
        st.session_state.clear()
        st.rerun()

    tab1, tab2, tab3 = st.tabs(["Cadastrar Lavanderia", "Cadastrar Administrador", "Estatísticas"])

    # Listar Lavanderias:
    lavanderias = controlador_plataforma.listar_lavanderias()
    st.subheader("Lavanderias Cadastradas")
    if not lavanderias:
        st.info("Nenhuma lavanderia cadastrada ainda.")
    else:
        for lav in lavanderias:
            with st.expander(f"🏢 {lav.nome}"):
                st.write(f"📍 Endereço: {lav.endereco}")
                st.write(f"🧺 Quantidade de Máquinas: {lav.qtd_maquinas}")
                st.write(f"👤 Administrador do Prédio (ID): {lav.id_adm_predio}")

    st.divider()  # linha separadora para estética

    # Cadatrar Lavanderia:
    with tab1:
        with st.form("nova_lavanderia"):
            nome = st.text_input("Nome")
            endereco = st.text_input("Endereço")
            id_adm_predio = st.number_input("ID do Administrador (opcional)")
            if st.form_submit_button("Cadastrar"):
                controlador_plataforma.cadastrar_lavanderia(nome, endereco, id_adm_predio or None)

    # Cadastrar Administrador de Prédio:
    with tab2: 
        lavanderias = controlador_plataforma.listar_lavanderias()
        lav_opts = {lav.nome: lav.id_lavanderia for lav in lavanderias}
        with st.form("novo_admin_predio"):
            nome = st.text_input("Nome")
            email = st.text_input("E-mail")
            senha = st.text_input("Senha", type="password")
            telefone = st.text_input("Telefone")
            lav_sel = st.selectbox("Lavanderia", list(lav_opts.keys()))
            if st.form_submit_button("Cadastrar"):
                controlador_plataforma.cadastrar_admin_predio(nome,email,senha,telefone, lav_opts[lav_sel])

    # Estatísticas da Plataforma (ex: quantidade de mlavanderias, usuarios)
    with tab3:
        stats = controlador_plataforma.obter_estatisticas()
        st.metric("Usuários Totais", stats["usuarios"])
        st.metric("Lavanderias Totais", stats["lavanderias"])
    