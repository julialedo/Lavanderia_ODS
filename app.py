""" View app.py
Interface em Streamlit: formulários para cadastrar e ditar maquinas e reservas, listagem, botões. 
Recebe o input do usuário, chama o controller, mostra o feedback."""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from controladores.controlador_reserva import ControladorReserva
from controladores.controlador_maquina import ControladorMaquina
from controladores.controlador_plataforma import ControladorPlataforma

#DEPOIS TIRAR, PORQUE A VIEW NÃO ACESSA O BANCO DE DADOS
from banco_de_dados.conexao_bd import conectar

# Inicialização dos controladores:
controlador_reserva = ControladorReserva()
controlador_maquina = ControladorMaquina()
controlador_plataforma = ControladorPlataforma()

# Configurações Gerais:
st.set_page_config(
    page_title="Gerenciador de Lavanderia Compartilhada",
    page_icon="🧺",
    layout="wide"
)


# Tela de Login:
def tela_login():
    st.title("🔐 Login - Sistema de Lavanderia")
    st.markdown("---")

    st.info("Para testar o aplicativo sem o MySQL, use:\n- Admin de Prédio: Email: `admin@predio.com`, Senha: `123`\n- Morador: Email: `morador@predio.com`, Senha: `123`\n- Admin de Plataforma: Email: `plataforma@admin.com`, Senha: `123`")

    usuario = st.text_input("E-mail")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar", use_container_width=True):
        
        # Simulação de Login (Mock)
        if usuario in ["admin@predio.com", "morador@predio.com", "plataforma@admin.com"] and senha == "123":
            if usuario == "admin@predio.com":
                st.session_state["logado"] = True
                st.session_state["usuario"] = "Admin Predial"
                st.session_state["tipo"] = "adm_predio"
                st.session_state["id_lavanderia"] = 1 # Mock ID
                st.session_state.pagina = "inicial"
            elif usuario == "morador@predio.com":
                st.session_state["logado"] = True
                st.session_state["usuario"] = "Morador Apto 101"
                st.session_state["tipo"] = "morador"
                st.session_state["id_lavanderia"] = 1 # Mock ID
                st.session_state.pagina = "usuario"
            elif usuario == "plataforma@admin.com":
                st.session_state["logado"] = True
                st.session_state["usuario"] = "Admin Plataforma"
                st.session_state["tipo"] = "adm_plataforma"
                st.session_state["id_lavanderia"] = None
                st.session_state.pagina = "adm_plataforma"
                
            st.success(f"Bem-vindo, {st.session_state['usuario']}! (Modo Simulação)")
            st.rerun()
            return
            
        # Lógica original de Login (com Conexão ao Banco)
        conexao = conectar()
        if conexao:
            try:
                cursor = conexao.cursor(dictionary=True)
                query = "SELECT * FROM usuario WHERE email=%s AND senha=%s"
                cursor.execute(query, (usuario, senha))
                resultado = cursor.fetchone()

                if resultado:
                    st.session_state["logado"] = True
                    st.session_state["usuario"] = resultado["nome"]
                    st.session_state["tipo"] = resultado["tipo_usuario"]
                    st.session_state["id_lavanderia"] = resultado.get("id_lavanderia")

                    st.success(f"Bem-vindo, {resultado['nome']}!")
                    if resultado["tipo_usuario"] == "adm_plataforma":
                        st.session_state.pagina = "adm_plataforma"
                        st.rerun()
                    else:
                        st.session_state.pagina = "inicial"
                        st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")
            except Exception as e:
                st.error(f"Erro ao tentar logar com o banco de dados: {e}")
            finally:
                conexao.close()
        else:
             st.warning("Falha na conexão com o banco. Tentando login de simulação...")



# Tela Inicial:
def tela_inicial():
    st.title("🧺 Gerenciador de Lavanderia Compartilhada")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("👨‍💼 Área do Administrador")
        if st.button("Gerenciar Máquinas", use_container_width=True):
            st.session_state.pagina = "admin"

    with col2:
        st.subheader("👤 Área dos Moradores")
        if st.button("Visualizar Horários", use_container_width=True):
            st.session_state.pagina = "usuario"

    with col3:
        st.subheader("📊 Relatórios")
        if st.button("Gerar Relatórios", use_container_width=True):
            st.session_state.pagina = "relatorios"

    st.markdown("---")
    if st.sidebar.button("🚪 Sair"):
        st.session_state.clear()
        st.experimental_rerun()


# Tela do Administrador:
def tela_admin():
    st.title("👨‍💼 Gerenciamento de Máquinas")
    st.markdown("---")
    

    # Cadastrar Máquinas - Formulário
    with st.expander("➕ Cadastrar Nova Máquina"):
        with st.form("nova_maquina"):
            codigo = st.text_input("Código da Máquina (ex: LAV-01, SEC-07)")
            tipo = st.selectbox("Tipo da Máquina", ["lavadora", "secadora"])
            capacidade = st.text_input("Capacidade (ex: 8kg)")
            status = st.selectbox("Status Inicial", ["livre", "em_uso", "manutencao"])
            btn = st.form_submit_button("Cadastrar")
            if btn:
                try:
                    new_id = controlador_maquina.cadastrar_maquina(st.session_state["id_lavanderia"], codigo, tipo, capacidade, status)
                    st.success(f"Máquina cadastrada com sucesso!")
                except Exception as e:
                    st.error(str(e))

    st.markdown("---")


    # Listar as Maquinas Cadastradas
    st.subheader("📋 Máquinas cadastradas")

    maquinas = controlador_maquina.listar_por_lavanderia(st.session_state["id_lavanderia"])
    if not maquinas:
        st.info("Nenhuma máquina cadastrada para esta Lavanderia!")
    else:
        for maq in maquinas:
            with st.expander(f"⚙️ {maq.codigo_maquina} - {maq.tipo_maquina.capitalize()} ({maq.capacidade})"):
                st.write(f"**Status atual:** {maq.status_maquina}")
                st.write(f"**Tipo:** {maq.tipo_maquina}")
                st.write(f"**Capacidade:** {maq.capacidade}")
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button(f"✏️ Editar", key=f"edit_{maq.id_maquina}"):
                        st.session_state["editar_maquina"] = maq.id_maquina
                        st.rerun()
                with col2:
                    if st.button(f"🗑️ Excluir", key=f"del_{maq.id_maquina}"):
                        try:
                            ok = controlador_maquina.remover_maquina(maq.id_maquina)
                            if ok:
                                st.success("Máquina removida com sucesso!")
                                st.rerun()
                            else:
                                st.error("Erro ao remover máquina.")
                        except Exception as e:
                            st.error(str(e))
    

    # Caso tenha clicado em Editar, mostra o formulário:
    if "editar_maquina" in st.session_state:
        maq_id = st.session_state["editar_maquina"]
        maquina = controlador_maquina.obter(maq_id)

        st.markdown("### ✏️ Editar Máquina")
        with st.form("form_editar_maquina"):
            codigo_novo = st.text_input("Código Novo", maquina.codigo_maquina)
            tipo_novo = st.selectbox("Tipo", ["lavadora", "secadora"], index=["lavadora", "secadora"].index(maquina.tipo_maquina))
            capacidade_nova = st.text_input("Capacidade", maquina.capacidade)
            status_novo = st.selectbox("Status", ["livre", "em_uso", "manutencao"], index=["livre", "em_uso", "manutencao"].index(maquina.status_maquina))
            btn_salvar = st.form_submit_button("💾 Salvar alterações")

            if btn_salvar:
                campos = {
                    "codigo_maquina": codigo_novo,
                    "tipo_maquina": tipo_novo,
                    "capacidade": capacidade_nova,
                    "status_maquina": status_novo
                }
                try:
                    ok = controlador_maquina.editar_maquina(maq_id, campos)
                    if ok:
                        st.success("Máquina atualizada com sucesso!")
                        del st.session_state["editar_maquina"]
                        st.rerun()
                    else:
                        st.warning("Nenhuma alteração detectada.")
                except Exception as e:
                    st.error(str(e))

        if st.button("⬅️ Cancelar edição"):
            del st.session_state["editar_maquina"]
            st.rerun()
            
    if st.button("⬅️ Voltar"):
        st.session_state.pagina = "inicial"



# Tela do Usuário
def tela_usuario():
    st.title("👤 Área do Morador")
    st.markdown("---")
    
    # Inicializar controladores
    controlador_maquina = ControladorMaquina()
    
    tab1, tab2, tab3 = st.tabs(["📅 Visualizar Horários", "⏰ Fazer Agendamento", "📋 Minhas Reservas"])
    
    with tab1:
        st.subheader("Horários Disponíveis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Buscar máquinas reais do banco (substituindo os dados fictícios)
            maquinas = controlador_maquina.listar_por_lavanderia(1)  # Assumindo lavanderia ID 1
            if maquinas:
                # Criar lista no formato antigo
                opcoes_maquinas = []
                for maquina in maquinas:
                    if maquina.status_maquina != "manutencao":
                        descricao = f"Máquina {maquina.id_maquina} - {maquina.tipo_maquina}"
                        opcoes_maquinas.append(descricao)
                
                maquina_selecionada = st.selectbox("Selecione a máquina:", opcoes_maquinas)
                # Extrair ID da máquina da descrição selecionada
                maquina_id = maquina_selecionada.split(" ")[1]  # Pega o número após "Máquina "
            else:
                # Fallback para dados fictícios se não houver máquinas
                maquinas = ["Máquina 1 - Lavadora", "Máquina 2 - Secadora", "Máquina 3 - Lavadora"]
                maquina_selecionada = st.selectbox("Selecione a máquina:", maquinas)
                maquina_id = "1" if "1" in maquina_selecionada else "2"
        
        with col2:
            data_selecionada = st.date_input("Selecione a data")
        
        if st.button("🔍 Ver Horários Disponíveis"):
            # Usar controlador real para buscar horários
            horarios_disponiveis = controlador_reserva.visualizar_horarios_disponiveis(
                maquina_id, 
                data_selecionada.strftime("%Y-%m-%d")
            )
            
            st.subheader(f"Horários disponíveis - {maquina_selecionada}")
            
            # Mostrar horários em colunas (mantendo o formato original)
            if horarios_disponiveis:
                cols = st.columns(4)
                for i, horario in enumerate(horarios_disponiveis):
                    with cols[i % 4]:
                        st.write(f"**{horario}**")
                        st.success("✅ Disponível")
            else:
                st.info("📭 Não há horários disponíveis para esta data/máquina.")
    
    with tab2:
        st.subheader("Fazer Agendamento")
        
        with st.form("agendamento_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Buscar máquinas reais
                maquinas = controlador_maquina.listar_por_lavanderia(1)
                if maquinas:
                    opcoes_maquinas = []
                    for maquina in maquinas:
                        if maquina.status_maquina != "manutencao":
                            descricao = f"Máquina {maquina.id_maquina} - {maquina.tipo_maquina} ({maquina.capacidade})"
                            opcoes_maquinas.append(descricao)
                    
                    maquina = st.selectbox(
                        "Selecione a máquina",
                        opcoes_maquinas,
                        key="agendamento_maquina"
                    )
                    # Extrair ID da descrição
                    maquina_id = maquina.split(" ")[1]
                else:
                    # Fallback para dados fictícios
                    maquina = st.selectbox(
                        "Selecione a máquina",
                        ["Máquina 1 - Lavadora (Térreo)", "Máquina 2 - Secadora (Térreo)", "Máquina 3 - Lavadora (1º Andar)"],
                        key="agendamento_maquina"
                    )
                    maquina_id = "1" if "1" in maquina else "2"
                
                data_agendamento = st.date_input("Data do agendamento", key="agendamento_data")
            
            with col2:
                # Horários disponíveis para seleção (mantendo o formato original)
                horarios = [f"{hora:02d}:00" for hora in range(8, 20)]
                hora_agendamento = st.selectbox("Horário de início", horarios)
                
                usuario = st.text_input("Seu ID*", placeholder="Digite seu ID")
            
            if st.form_submit_button("📅 Fazer Agendamento"):
                if usuario:
                    # Usar controlador real para criar reserva
                    usuario_id = usuario.lower().replace(" ", "")
                    print("DEBUG : {data_agendamento.strftime('%Y-%m-%d')}")
                    reserva = controlador_reserva.criar_reserva(
                        maquina_id,
                        usuario_id,
                        data_agendamento.strftime("%Y-%m-%d"),
                        hora_agendamento
                    )
                    
                    if reserva:
                        st.success(f"🎉 Reserva realizada com sucesso! ID: {reserva.id_reserva}")
                    else:
                        st.error("❌ Erro ao fazer reserva. Tente novamente.")
                else:
                    st.warning("⚠️ Por favor, digite seu ID.")
    
    with tab3:
        st.subheader("Minhas Reservas")
        
        usuario_consulta = st.text_input("Digite seu ID para ver suas reservas:", 
                                       placeholder="Seu ID", 
                                       key="minhas_reservas")
        
        if usuario_consulta:
            usuario_id = usuario_consulta.lower().replace(" ", "")
            reservas = controlador_reserva.obter_reservas_por_usuario(usuario_id)
            
            if reservas:
                st.success(f"📋 Você tem {len(reservas)} reserva(s) ativa(s)")
                
                for reserva in reservas:
                    with st.expander(f"Reserva {reserva.id_reserva} - {reserva.data_reserva} às {reserva.hora_inicio}"):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.write(f"**Máquina ID:** {reserva.id_maquina}")
                            st.write(f"**Data:** {reserva.data_reserva}")
                            st.write(f"**Horário:** {reserva.hora_inicio} - {reserva.hora_fim}")
                            st.write(f"**Status:** {reserva.status_reserva}")
                        
                        with col2:
                            if st.button("❌ Cancelar", key=f"cancel_{reserva.id_reserva}"):
                                if controlador_reserva.cancelar_reserva(reserva.id_reserva, usuario_id):
                                    st.success("Reserva cancelada com sucesso!")
                                    st.rerun()
            else:
                st.info("📭 Você não possui reservas ativas.")
                



# Tela de Relatórios:
def tela_relatorios():
    st.title("📊 Relatórios de Uso da Lavanderia")
    st.markdown("---")
    # (Mantém seu conteúdo original da função tela_relatorios)
    if st.button("⬅️ Voltar"):
        st.session_state.pagina = "inicial"


# Tela de Administrador de Plataforma:
def tela_adm_plataforma():
    tab1, tab2, tab3 = st.tabs(["Cadastrar Lavanderia", "Cadastrar Administrador", "Estatísticas"])

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


# Execução Principal:
if "logado" not in st.session_state:
    st.session_state["logado"] = False
if "pagina" not in st.session_state:
    st.session_state.pagina = "login"

if not st.session_state["logado"]:
    tela_login()
else:
    if st.session_state.pagina == "inicial":
        tela_inicial()
    elif st.session_state.pagina == "admin":
        tela_admin()
    elif st.session_state.pagina == "usuario":
        tela_usuario()
    elif st.session_state.pagina == "relatorios":
        tela_relatorios()
    elif st.session_state.pagina == "adm_plataforma":
        tela_adm_plataforma()
