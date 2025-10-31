# View - tela_adm_plataforma.py
# Interface em Streamlit, recebe o input do usuário, chama o controller, mostra o feedback.

import streamlit as st
from controladores.controlador_plataforma import ControladorPlataforma
from controladores.controlador_usuario import ControladorUsuario

# Inicialização dos controladores:
controlador_plataforma = ControladorPlataforma()
controlador_usuario = ControladorUsuario()


# Tela inicial do Administrador da Plataforma:
def tela_adm_plataforma():
    
    st.title("🧺 Administração da Plataforma")

    st.sidebar.title("Menu")
    if "usuario" in st.session_state:
        st.sidebar.write(f"👤 Usuário: {st.session_state['usuario']}")
    if st.sidebar.button("🚪 Sair"):
        st.session_state.clear()
        st.rerun()

    # Abas principais
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏢 Cadastrar Lavanderia",
        "👨‍💼 Cadastrar Administrador",
        "👥 Cadastrar Morador",
        "📊 Estatísticas",
        "👤 Meu Perfil"
    ])

    # ------------------------------------------------------------------
    # TAB 1 - Cadastrar Lavanderia
    with tab1:
        st.subheader("🏢 Cadastrar Nova Lavanderia")
        with st.form("nova_lavanderia"):
            nome = st.text_input("Nome da Lavanderia")
            endereco = st.text_input("Endereço")
            id_adm_predio = st.number_input("ID do Administrador (opcional)", step=1)
            cadastrar = st.form_submit_button("Cadastrar Lavanderia")
            if cadastrar:
                try:
                    controlador_plataforma.cadastrar_lavanderia(nome, endereco, id_adm_predio or None)
                    st.success(f"✅ Lavanderia '{nome}' cadastrada com sucesso!")
                except Exception as e:
                    st.error(f"❌ Erro ao cadastrar lavanderia: {str(e)}")

        st.markdown("---")
        lavanderias = controlador_plataforma.listar_lavanderias()
        st.subheader("📋 Lavanderias Cadastradas")
        if not lavanderias:
            st.info("Nenhuma lavanderia cadastrada ainda.")
        else:
            for lav in lavanderias:
                with st.expander(f"🏢 {lav.nome}"):
                    st.write(f"📍 **Endereço:** {lav.endereco}")
                    st.write(f"🧺 **Máquinas:** {lav.qtd_maquinas}")
                    st.write(f"👤 **Administrador do Prédio (ID):** {lav.id_adm_predio or 'Não definido'}")

    # ------------------------------------------------------------------
    # TAB 2 - Cadastrar Administrador de Prédio
    with tab2: 
        st.subheader("👨‍💼 Cadastrar Novo Administrador de Prédio")
        lavanderias = controlador_plataforma.listar_lavanderias()
        lav_opts = {lav.nome: lav.id_lavanderia for lav in lavanderias}
        with st.form("novo_admin_predio"):
            nome = st.text_input("Nome")
            email = st.text_input("E-mail")
            senha = st.text_input("Senha", type="password")
            telefone = st.text_input("Telefone")
            lav_sel = st.selectbox("Lavanderia", list(lav_opts.keys()) if lav_opts else [])
            cadastrar = st.form_submit_button("Cadastrar Administrador")
            if cadastrar:
                try:
                    controlador_plataforma.cadastrar_admin_predio(
                        nome, email, senha, telefone, lav_opts[lav_sel]
                    )
                    st.success(f"✅ Administrador '{nome}' cadastrado com sucesso!")
                except Exception as e:
                    st.error(f"❌ Erro ao cadastrar administrador: {str(e)}")

    # ------------------------------------------------------------------
    # TAB 3 - Cadastrar Morador
    with tab3:
        st.subheader("👥 Cadastrar Novo Morador")
        lavanderias = controlador_plataforma.listar_lavanderias()
        lav_opts = {lav.nome: lav.id_lavanderia for lav in lavanderias}

        with st.form("novo_morador"):
            nome = st.text_input("Nome completo")
            email = st.text_input("E-mail")
            senha = st.text_input("Senha", type="password")
            telefone = st.text_input("Telefone")
            lav_sel = st.selectbox("Lavanderia", list(lav_opts.keys()) if lav_opts else [])
            cadastrar = st.form_submit_button("Cadastrar Morador")

            if cadastrar:
                try:
                    controlador_usuario.cadastrar_usuario(
                        nome=nome,
                        email=email,
                        senha=senha,
                        telefone=telefone,
                        tipo_usuario="morador",
                        id_lavanderia=lav_opts[lav_sel]
                    )
                    st.success(f"✅ Morador '{nome}' cadastrado com sucesso na lavanderia '{lav_sel}'!")
                except Exception as e:
                    st.error(f"❌ Erro ao cadastrar morador: {str(e)}")

    # ------------------------------------------------------------------
    # TAB 4 - Estatísticas da Plataforma
    with tab4:
        st.subheader("📊 Estatísticas da Plataforma")
        try:
            stats = controlador_plataforma.obter_estatisticas()
            col1, col2 = st.columns(2)
            with col1:
                st.metric("👥 Usuários Totais", stats.get("usuarios", 0))
            with col2:
                st.metric("🏢 Lavanderias Totais", stats.get("lavanderias", 0))
        except Exception as e:
            st.error(f"❌ Erro ao carregar estatísticas: {str(e)}")

    # ------------------------------------------------------------------
    # TAB 5 - Meu Perfil
    with tab5:
        st.subheader("👤 Editar Informações do Perfil")

        usuario_logado = st.session_state.get("usuario_dados")
        if not usuario_logado:
            st.warning("⚠️ Não foi possível carregar suas informações. Faça login novamente.")
        else:
            with st.form("form_editar_perfil_adm_plataforma"):
                nome = st.text_input("Nome", value=usuario_logado["nome"])
                email = st.text_input("Email", value=usuario_logado["email"])
                telefone = st.text_input("Telefone", value=usuario_logado["telefone"])
                senha_atual = st.text_input("Senha Atual*", type="password")
                nova_senha = st.text_input("Nova Senha (opcional)", type="password")

                salvar = st.form_submit_button("💾 Salvar Alterações", use_container_width=True)

                if salvar:
                    try:
                        sucesso = controlador_usuario.editar_perfil(
                            id_usuario=usuario_logado["id_usuario"],
                            nome=nome,
                            email=email,
                            telefone=telefone,
                            senha_atual=senha_atual,
                            nova_senha=nova_senha if nova_senha else None
                        )
                        if sucesso:
                            st.success("✅ Perfil atualizado com sucesso!")
                            st.session_state["usuario_dados"]["nome"] = nome
                            st.session_state["usuario_dados"]["email"] = email
                            st.session_state["usuario_dados"]["telefone"] = telefone
                            st.rerun()
                    except Exception as e:
                        st.error(f"❌ Erro: {str(e)}")

            st.markdown("---")
            if st.button("⬅️ Voltar para a tela principal", use_container_width=True):
                st.info("👈 Voltando para a tela inicial...")
                st.rerun()
