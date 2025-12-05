# View - tela_adm_plataforma.py
# Interface em Streamlit, recebe o input do usuário, chama o controller, mostra o feedback.

import streamlit as st

# Controladores inicializados uma vez
try:
    from controladores.controlador_plataforma import ControladorPlataforma
    from controladores.controlador_usuario import ControladorUsuario
    controlador_plataforma = ControladorPlataforma()
    controlador_usuario = ControladorUsuario()
except ImportError:
    controlador_plataforma = None
    controlador_usuario = None

# Cache para dados estáticos
def get_lavanderias_cache():
    """Cache otimizado para lista de lavanderias"""
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
    """Limpa cache de lavanderias"""
    if 'lavanderias_list' in st.session_state:
        del st.session_state.lavanderias_list
    if 'lavanderias_dict' in st.session_state:
        del st.session_state.lavanderias_dict

def get_estatisticas_cache():
    """Cache para estatísticas"""
    if 'estatisticas_plataforma' not in st.session_state:
        try:
            stats = controlador_plataforma.obter_estatisticas() if controlador_plataforma else {}
            st.session_state.estatisticas_plataforma = stats
        except:
            st.session_state.estatisticas_plataforma = {}
    return st.session_state.estatisticas_plataforma

def tela_adm_plataforma():
    # Verificação inicial do sistema
    if not controlador_plataforma or not controlador_usuario:
        st.error("⚠️ Sistema temporariamente indisponível. Tente novamente.")
        if st.button("🔄 Recarregar"):
            st.rerun()
        return
    
    st.title("🧺 Administração da Plataforma")

    # Sidebar otimizada
    with st.sidebar:
        st.title("Menu")
        if "usuario" in st.session_state:
            st.write(f"👤 Usuário: {st.session_state['usuario']}")
        
        st.markdown("---")
        if st.button("🔄 Atualizar Cache", help="Recarregar todos os dados"):
            clear_lavanderias_cache()
            if 'estatisticas_plataforma' in st.session_state:
                del st.session_state.estatisticas_plataforma
            st.rerun()
            
        if st.button("🚪 Sair"):
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
        
        with st.form("nova_lavanderia", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                nome = st.text_input("Nome da Lavanderia*", placeholder="Ex: Lavanderia do Edifício A")
                endereco = st.text_input("Endereço*", placeholder="Ex: Rua Principal, 123")
            
            with col2:
                id_adm_predio = st.number_input("ID do Administrador (opcional)", 
                                              min_value=1, 
                                              step=1,
                                              help="Deixe em branco se não houver administrador definido")
            
            st.caption("* Campos obrigatórios")
            
            if st.form_submit_button("🏢 Cadastrar Lavanderia", use_container_width=True):
                if not nome or not endereco:
                    st.error("❌ Nome e endereço são obrigatórios!")
                else:
                    try:
                        controlador_plataforma.cadastrar_lavanderia(
                            nome, 
                            endereco, 
                            id_adm_predio if id_adm_predio > 0 else None
                        )
                        st.success(f"✅ Lavanderia '{nome}' cadastrada com sucesso!")
                        # Limpar cache para refletir mudanças
                        clear_lavanderias_cache()
                    except Exception as e:
                        st.error(f"❌ Erro ao cadastrar lavanderia: {str(e)}")

        st.markdown("---")
        st.subheader("📋 Lavanderias Cadastradas")
        
        lavanderias, lavanderias_dict = get_lavanderias_cache()
        
        if not lavanderias:
            st.info("ℹ️ Nenhuma lavanderia cadastrada ainda.")
        else:
            st.success(f"🎯 Total: {len(lavanderias)} lavanderia(s) cadastrada(s)")
            
            # Filtro rápido
            col_search, col_stats = st.columns([2, 1])
            with col_search:
                filtro_nome = st.text_input("🔍 Filtrar por nome", placeholder="Digite para filtrar...")
            
            with col_stats:
                st.metric("Lavanderias", len(lavanderias))
            
            lavanderias_filtradas = [
                lav for lav in lavanderias 
                if not filtro_nome or filtro_nome.lower() in lav.nome.lower()
            ]
            
            for lav in lavanderias_filtradas:
                with st.expander(f"🏢 {lav.nome}", expanded=False):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**📍 Endereço:** {lav.endereco}")
                        st.write(f"**🆔 ID:** {lav.id_lavanderia}")
                        
                    with col2:
                        st.write(f"**🧺 Máquinas:** {lav.qtd_maquinas or 0}")
                        st.write(f"**👤 Admin (ID):** {lav.id_adm_predio or 'Não definido'}")
                    
                    # Ações rápidas
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        if st.button("📊 Ver Detalhes", key=f"detalhes_{lav.id_lavanderia}"):
                            st.info(f"Detalhes completos da lavanderia {lav.nome}")
                    
                    with col_btn2:
                        if st.button("🗑️ Excluir", key=f"excluir_{lav.id_lavanderia}"):
                            st.warning(f"Funcionalidade de exclusão para {lav.nome}")

    # ------------------------------------------------------------------
    # TAB 2 - Cadastrar Administrador de Prédio
    with tab2: 
        st.subheader("👨‍💼 Cadastrar Novo Administrador de Prédio")
        
        lavanderias, lavanderias_dict = get_lavanderias_cache()
        
        if not lavanderias:
            st.warning("⚠️ É necessário cadastrar uma lavanderia primeiro!")
            st.info("Vá para a aba '🏢 Cadastrar Lavanderia' para criar uma lavanderia.")
        else:
            with st.form("novo_admin_predio", clear_on_submit=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    nome = st.text_input("Nome Completo*", placeholder="Ex: João Silva")
                    email = st.text_input("E-mail*", placeholder="Ex: joao@email.com")
                
                with col2:
                    senha = st.text_input("Senha*", type="password")
                    telefone = st.text_input("Telefone", placeholder="Ex: (11) 99999-9999")
                
                lav_sel = st.selectbox(
                    "Lavanderia*", 
                    options=list(lavanderias_dict.keys()),
                    help="Selecione a lavanderia que este administrador irá gerenciar"
                )
                
                st.caption("* Campos obrigatórios")
                
                if st.form_submit_button("👨‍💼 Cadastrar Administrador", use_container_width=True):
                    if not all([nome, email, senha, lav_sel]):
                        st.error("❌ Todos os campos obrigatórios devem ser preenchidos!")
                    else:
                        try:
                            controlador_plataforma.cadastrar_admin_predio(
                                nome, email, senha, telefone, lavanderias_dict[lav_sel]
                            )
                            st.success(f"✅ Administrador '{nome}' cadastrado com sucesso!")
                            st.success(f"📧 E-mail: {email}")
                            st.success(f"🏢 Lavanderia: {lav_sel}")
                        except Exception as e:
                            st.error(f"❌ Erro ao cadastrar administrador: {str(e)}")

    # ------------------------------------------------------------------
    # TAB 3 - Cadastrar Morador
    with tab3:
        st.subheader("👥 Cadastrar Novo Morador")
        
        lavanderias, lavanderias_dict = get_lavanderias_cache()
        
        if not lavanderias:
            st.warning("⚠️ É necessário cadastrar uma lavanderia primeiro!")
        else:
            with st.form("novo_morador", clear_on_submit=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    nome = st.text_input("Nome completo*", placeholder="Ex: Maria Santos")
                    email = st.text_input("E-mail*", placeholder="Ex: maria@email.com")
                
                with col2:
                    senha = st.text_input("Senha*", type="password")
                    telefone = st.text_input("Telefone", placeholder="Ex: (11) 98888-8888")
                
                lav_sel = st.selectbox(
                    "Lavanderia*", 
                    options=list(lavanderias_dict.keys()),
                    key="morador_lavanderia"
                )
                
                st.caption("* Campos obrigatórios")
                
                if st.form_submit_button("👥 Cadastrar Morador", use_container_width=True):
                    if not all([nome, email, senha, lav_sel]):
                        st.error("❌ Todos os campos obrigatórios devem ser preenchidos!")
                    else:
                        try:
                            controlador_usuario.cadastrar_usuario(
                                nome=nome,
                                email=email,
                                senha=senha,
                                telefone=telefone,
                                tipo_usuario="morador",
                                id_lavanderia=lavanderias_dict[lav_sel]
                            )
                            st.success(f"✅ Morador '{nome}' cadastrado com sucesso!")
                            st.success(f"📧 E-mail: {email}")
                            st.success(f"🏢 Lavanderia: {lav_sel}")
                        except Exception as e:
                            st.error(f"❌ Erro ao cadastrar morador: {str(e)}")

    # ------------------------------------------------------------------
    # TAB 4 - Estatísticas da Plataforma
    with tab4:
        st.subheader("📊 Estatísticas da Plataforma")
        
        stats = get_estatisticas_cache()
        
        if not stats:
            st.info("ℹ️ Carregando estatísticas...")
        else:
            # Métricas principais
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
            
            # Estatísticas detalhadas
            col_detail1, col_detail2 = st.columns(2)
            
            with col_detail1:
                st.subheader("📈 Distribuição de Usuários")
                tipos_usuarios = stats.get("tipos_usuarios", {})
                
                if tipos_usuarios:
                    for tipo, quantidade in tipos_usuarios.items():
                        st.write(f"**{tipo.capitalize()}:** {quantidade}")
                else:
                    st.info("ℹ️ Sem dados de distribuição disponíveis")
            
            with col_detail2:
                st.subheader("🏆 Lavanderias Mais Ativas")
                lavanderias_ativas = stats.get("lavanderias_ativas", [])
                
                if lavanderias_ativas:
                    for i, lav in enumerate(lavanderias_ativas[:5], 1):
                        st.write(f"{i}. {lav.get('nome', 'N/A')} - {lav.get('reservas', 0)} reservas")
                else:
                    st.info("ℹ️ Sem dados de atividade disponíveis")
            
            # Botão para atualizar estatísticas
            if st.button("🔄 Atualizar Estatísticas", use_container_width=True):
                if 'estatisticas_plataforma' in st.session_state:
                    del st.session_state.estatisticas_plataforma
                st.rerun()

    # ------------------------------------------------------------------
    # TAB 5 - Meu Perfil
    with tab5:
        st.subheader("👤 Editar Informações do Perfil")

        usuario_logado = st.session_state.get("usuario_dados")
        if not usuario_logado:
            st.warning("⚠️ Não foi possível carregar suas informações. Faça login novamente.")
        else:
            with st.form("form_editar_perfil_adm_plataforma"):
                st.write("**Informações Pessoais**")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    nome = st.text_input("Nome*", value=usuario_logado.get("nome", ""))
                    email = st.text_input("Email*", value=usuario_logado.get("email", ""))
                
                with col2:
                    telefone = st.text_input("Telefone", value=usuario_logado.get("telefone", ""))
                
                st.markdown("---")
                st.write("**Alterar Senha**")
                
                senha_atual = st.text_input("Senha Atual*", type="password",
                                          help="Digite sua senha atual para confirmar as alterações")
                nova_senha = st.text_input("Nova Senha (opcional)", type="password",
                                         help="Deixe em branco se não quiser alterar a senha")
                confirmar_senha = st.text_input("Confirmar Nova Senha", type="password",
                                              help="Repita a nova senha")

                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    salvar = st.form_submit_button("💾 Salvar Alterações", use_container_width=True)
                with col_btn2:
                    cancelar = st.form_submit_button("❌ Cancelar", use_container_width=True)

                if salvar:
                    # Validações
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
                    st.info("ℹ️ Alterações canceladas.")
                    st.rerun()

            st.markdown("---")
            
            # Informações da sessão atual
            with st.expander("🔍 Informações da Sessão"):
                st.write(f"**ID do Usuário:** {usuario_logado.get('id_usuario', 'N/A')}")
                st.write(f"**Tipo de Usuário:** {st.session_state.get('tipo', 'N/A')}")
                st.write(f"**Login:** {st.session_state.get('usuario', 'N/A')}")

            if st.button("⬅️ Voltar para a tela principal", use_container_width=True):
                st.info("👈 Voltando para a tela inicial...")
                st.rerun()