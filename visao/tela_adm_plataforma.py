# View - tela_adm_plataforma.py
# Interface em Streamlit, recebe o input do usuário, chama o controller, mostra o feedback.

import streamlit as st

# Controladores inicializados e armazenados uma vez com cache:
@st.cache_resource
def get_controladores_plataforma():
    try:
        from controladores.controlador_plataforma import ControladorPlataforma
        from controladores.controlador_usuario import ControladorUsuario
        return {
            "plataforma": ControladorPlataforma(),
            "usuario": ControladorUsuario()
        }
    except ImportError as e:
        st.error(f"Erro ao carregar controladores: {e}")
        return None

CONTROLADORES = get_controladores_plataforma()
if CONTROLADORES:
    controlador_plataforma = CONTROLADORES["plataforma"]
    controlador_usuario = CONTROLADORES["usuario"]
else:
    controlador_plataforma = None
    controlador_usuario = None


# Funções para listar todas as lavanderias com cache e limpar a cache: OK 
def get_lavanderias_cache():
    if 'lavanderias_list' not in st.session_state:
        try:
            lavanderias = controlador_plataforma.listar_lavanderias() if controlador_plataforma else []
            st.session_state.lavanderias_list = lavanderias
            st.session_state.lavanderias_dict = {lav.nome: lav.id_lavanderia for lav in lavanderias}
        except Exception as e:
            st.error(f"Erro ao carregar lavanderias: {e}")
            st.session_state.lavanderias_list = []
            st.session_state.lavanderias_dict = {}
    return st.session_state.lavanderias_list, st.session_state.lavanderias_dict

def clear_lavanderias_cache():
    if 'lavanderias_list' in st.session_state:
        del st.session_state.lavanderias_list
    if 'lavanderias_dict' in st.session_state:
        del st.session_state.lavanderias_dict


# Função para listar estatisticas com cache: OK
def get_estatisticas_cache():
    if 'estatisticas_plataforma' not in st.session_state:
        try:
            if controlador_plataforma:
                stats = controlador_plataforma.obter_estatisticas() 
            else:
                st.warning("Erro ao acessar estatisticas do Controlador Plataforma")
                stats = {}
            st.session_state.estatisticas_plataforma = stats
        except Exception as e:
            st.error(f"Erro ao obter estatísticas: {e}") 
            st.session_state.estatisticas_plataforma = {}
    return st.session_state.estatisticas_plataforma


# Tela Inicial do adm_plataforma: OK
def tela_adm_plataforma():
    # Verificação inicial do sistema
    if not controlador_plataforma or not controlador_usuario:
        st.error("⚠️ Sistema temporariamente indisponível. Tente novamente.")
        if st.button("🔄 Recarregar"):
            st.rerun()
        return

    # Sidebar otimizada
    with st.sidebar:
        if "usuario" in st.session_state:
            st.subheader(f" 👤 Bem-vindo(a) {st.session_state['usuario']}!")
        
        st.markdown("---")
        if st.button("Limpar Cache", use_container_width=True, help="Recarregar todos os dados"):
            clear_lavanderias_cache()
            if 'estatisticas_plataforma' in st.session_state:
                del st.session_state.estatisticas_plataforma
            st.rerun()
            
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    # TELA PRINCIPAL:
    st.header("Área de Administração da Plataforma")
    # Abas principais:
    tab1, tab2, tab3, tab4, tab5, = st.tabs([
        "🏠 Lavanderias Cadastradas",
        "🏢 Cadastrar Lavanderia",
        "👨‍💼 Cadastrar Administrador",
        "📊 Estatísticas",
        "👤 Meu Perfil"
    ])

    with tab1:
        st.subheader("📋 Lavanderias Cadastradas")
        
        lavanderias, lavanderias_dict = get_lavanderias_cache()
        if not lavanderias:
            st.info("Nenhuma lavanderia cadastrada ainda.")
        else:
            st.success(f"Total: {len(lavanderias)} lavanderia(s) cadastrada(s)")
            # Filtro rápido
            filtro_nome = st.text_input("**Filtrar por Nome:**", placeholder="Digite para filtrar...")
            
            lavanderias_filtradas = [
                lav for lav in lavanderias 
                if not filtro_nome or filtro_nome.lower() in lav.nome.lower()
            ]
            for lav in lavanderias_filtradas:
                with st.expander(f"🏢 {lav.nome}", expanded=False):                    
                    
                    col1, col2 = st.columns([3,1])
                    with col1:
                        st.write(f"**📍 Endereço:** {lav.endereco}")
                        qtd_maquinas = controlador_plataforma.contar_maquinas(lav.id_lavanderia)
                        st.write(f"**🧺 Máquinas:** {qtd_maquinas}")
                        adm = controlador_usuario.obter_usuario_por_id(lav.id_adm_predio)
                        nome_adm = adm["nome"] if adm else "Não definido"
                        st.write(f"**👤 Admin (ID):** {nome_adm}")

                    with col2:
                        if lav.id_adm_predio is not None:
                            if st.button("Remover Adm", use_container_width=True, key=f"detalhes_{lav.id_lavanderia}"):
                                removido = controlador_plataforma.remover_administrador_lavanderia(lav.id_lavanderia, lav.id_adm_predio)
                                if removido:
                                    st.success(f"✅ Lavanderia '{lav.nome}' e dados dependentes excluídos (Máquinas, Reservas e Associações de Usuários).")
                                    clear_lavanderias_cache()
                                    st.rerun()
                                else:
                                    st.error("❌ Falha ao remover administrador da lavanderia. ")

                        if st.button("🗑️ Excluir", use_container_width=True, key=f"excluir_{lav.id_lavanderia}"):
                            exclusao = controlador_plataforma.excluir_lavanderia_e_dependentes(lav.id_lavanderia)
                            if exclusao:
                                st.success(f"✅ Lavanderia '{lav.nome}' e dados dependentes excluídos (Máquinas, Reservas e Associações de Usuários).")
                                clear_lavanderias_cache()
                                st.rerun()
                            else:
                                st.error("❌ Falha ao excluir a lavanderia. ")
    
    with tab2:
        st.subheader("🏢 Cadastrar Nova Lavanderia")
        
        with st.form("nova_lavanderia", clear_on_submit=True):
            nome = st.text_input("Nome da Lavanderia*", placeholder="Ex: Lavanderia do Edifício São João")
            endereco = st.text_input("Endereço*", placeholder="Ex: Rua Principal, 123, bairro, cidade")
            st.caption("*Campos obrigatórios")
            
            if st.form_submit_button("Cadastrar Lavanderia", use_container_width=True):
                if not nome or not endereco:
                    st.error("❌ Nome e endereço são obrigatórios!")
                else:
                    try:
                        controlador_plataforma.cadastrar_lavanderia(
                            nome, 
                            endereco
                        )
                        st.success(f"✅ Lavanderia '{nome}' cadastrada com sucesso!")
                        clear_lavanderias_cache()
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Erro ao cadastrar lavanderia: {str(e)}")

    with tab3: 
        st.subheader("👨‍💼 Cadastrar Novo Administrador de Prédio")
        
        lavanderias, lavanderias_dict = get_lavanderias_cache()
        if not lavanderias:
            st.warning("⚠️ É necessário cadastrar uma lavanderia primeiro!")
            st.info("Vá para a aba 'Cadastrar Lavanderia' para criar uma lavanderia.")
        else:
            with st.form("novo_admin_predio", clear_on_submit=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    nome = st.text_input("Nome Completo*", placeholder="Ex: João Silva")
                    email = st.text_input("E-mail*", placeholder="Ex: joao@email.com")
                with col2:
                    telefone = st.text_input("Telefone*", placeholder="Ex: (11) 99999-9999")
                    senha = st.text_input("Senha*", type="password")
                lav_sel = st.selectbox(
                    "Lavanderia*", 
                    options=list(lavanderias_dict.keys()),
                    help="Selecione a lavanderia que este administrador irá gerenciar",
                    index=None,
                    placeholder="Seleciona uma Lavanderia"
                )
                st.caption("*Campos obrigatórios")
                
                if st.form_submit_button("Cadastrar Administrador", use_container_width=True):
                    if not all([nome, email, telefone, senha, lav_sel]):
                        st.error("❌ Todos os campos obrigatórios devem ser preenchidos!")
                    else:
                        try:
                            controlador_plataforma.cadastrar_admin_predio(
                                nome, email, senha, telefone, lavanderias_dict[lav_sel]
                            )
                            st.success(f"✅ Administrador '{nome}' cadastrado com sucesso!")
                            st.success(f"🏢 Lavanderia: {lav_sel}")
                            clear_lavanderias_cache()
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Erro ao cadastrar administrador: {str(e)}")

    with tab4:          
        st.subheader("📊 Estatísticas da Plataforma")
        stats = get_estatisticas_cache()
        
        # Métricas principais:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("👥 Usuários Totais", stats.get("usuarios", 0))
        with col2:
            st.metric("🏢 Lavanderias Totais", stats.get("lavanderias", 0))
        with col3:
            st.metric("⚙️ Máquinas Totais", stats.get("maquinas", 0))
        with col4:
            st.metric("📅 Reservas Hoje", stats.get("reservas_hoje", 0))
    
        st.markdown("---")
        # Estatísticas detalhadas:
        st.subheader("🏆 Lavanderias Mais Ativas:")
        lavanderias_ativas = stats.get("lavanderias_ativas", [])
        if lavanderias_ativas:
            for i, lav in enumerate(lavanderias_ativas[:5], 1):
                st.write(f"{i}. {lav.get('nome', 'N/A')} - {lav.get('reservas', 0)} reservas")
        else:
            st.info("Sem dados de atividade disponíveis")
    
        st.markdown("---")
        st.subheader("Distribuição de Usuários:")
        tipos_usuarios = stats.get("tipos_usuarios", {})
        if tipos_usuarios:
            for tipo, quantidade in tipos_usuarios.items():
                st.write(f"**{tipo.capitalize()}:** {quantidade}")
        else:
            st.info("Sem dados de distribuição disponíveis")
    
        st.markdown("---")
        # Botão para atualizar estatísticas
        if st.button("🔄 Atualizar Estatísticas", use_container_width=True):
            if 'estatisticas_plataforma' in st.session_state:
                del st.session_state.estatisticas_plataforma
            st.rerun()

    with tab5:
        st.subheader("👤 Editar Informações do Perfil")
        usuario_logado = st.session_state.get("usuario_dados")
        if not usuario_logado:
            st.warning("⚠️ Não foi possível carregar suas informações. Faça login novamente.")
        else:
            with st.form("form_editar_perfil_adm_plataforma"):
                st.write("**Informações Pessoais**")
                nome = st.text_input("Nome Completo*", value=usuario_logado.get("nome", ""))
                email = st.text_input("Email*", value=usuario_logado.get("email", ""))
                telefone = st.text_input("Telefone", value=usuario_logado.get("telefone", ""))

                st.markdown("---")
                st.write("**Alterar Senha**")

                senha_atual = st.text_input("Senha Atual*", type="password",
                                          help="Digite sua senha atual para confirmar as alterações")
                nova_senha = st.text_input("Nova Senha (opcional)", type="password",
                                         help="Deixe em branco se não quiser alterar a senha")
                confirmar_senha = st.text_input("Confirmar Nova Senha", type="password",
                                              help="Repita a nova senha")

                st.text("*Campos obrigatórios.")
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    salvar = st.form_submit_button("Salvar Alterações", use_container_width=True)
                with col_btn2:
                    cancelar = st.form_submit_button("Cancelar", use_container_width=True)

                if salvar:
                    if not nome or not email:
                        st.error("❌ Nome e email são obrigatórios.")
                        return

                    if not senha_atual:
                        st.error("❌ A senha atual é obrigatória para confirmar as alterações.")
                        return

                    if nova_senha and nova_senha != confirmar_senha:
                        st.error("❌ As senhas não coincidem.")
                        return

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
                            st.session_state["usuario"] = nome
                            st.rerun()
                        else:
                            st.error("❌ Falha ao atualizar perfil. Verifique os dados e tente novamente.")
                    except Exception as e:
                        st.error(f"❌ Erro: {str(e)}")

                if cancelar:
                    st.info("Alterações canceladas.")
                    st.rerun()

            st.markdown("---")
        
            if st.button("⬅️ Voltar para a tela principal", use_container_width=True):
                st.rerun()