import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import mysql.connector
from mysql.connector import Error
from controladores.controlador_reserva import ControladorReserva

# --- Inicialização do controlador ---
controlador_reserva = ControladorReserva()

# --- Configurações gerais ---
st.set_page_config(
    page_title="Gerenciador de Lavanderia Compartilhada",
    page_icon="🧺",
    layout="wide"
)


# 🔑 TELA DE LOGIN
def tela_login():
    st.title("🔐 Login - Sistema de Lavanderia")
    st.markdown("---")

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar", use_container_width=True):
        conexao = conectar_banco()
        if conexao:
            cursor = conexao.cursor(dictionary=True)
            query = "SELECT * FROM usuarios WHERE nome_usuario=%s AND senha=%s"
            cursor.execute(query, (usuario, senha))
            resultado = cursor.fetchone()

            if resultado:
                st.session_state["logado"] = True
                st.session_state["usuario"] = resultado["nome_usuario"]
                st.session_state["tipo"] = resultado["tipo"]

                st.success(f"Bem-vindo, {resultado['nome_usuario']}!")
                st.session_state.pagina = "inicial"
                st.experimental_rerun()
            else:
                st.error("Usuário ou senha incorretos.")
            conexao.close()


# 🏠 TELA INICIAL
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

# ⚙️ TELA DO ADMINISTRADOR
def tela_admin():
    st.title("👨‍💼 Gerenciamento de Máquinas")
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["📋 Lista de Máquinas", "➕ Nova Máquina"])
    
    with tab1:
        maquinas = [
            {"nome": "Máquina 1 - Lavadora", "localizacao": "Térreo", "status": "Disponível"},
            {"nome": "Máquina 2 - Secadora", "localizacao": "Térreo", "status": "Em Manutenção"},
            {"nome": "Máquina 3 - Lavadora", "localizacao": "Térreo", "status": "Disponível"}
        ]
        
        for maquina in maquinas:
            with st.expander(f"{maquina['nome']} - {maquina['localizacao']}"):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"**Status:** {maquina['status']}")
                with col2:
                    st.button("✏️ Editar", key=f"edit_{maquina['nome']}")
                with col3:
                    st.button("🗑️ Excluir", key=f"del_{maquina['nome']}")
    
    with tab2:
        with st.form("nova_maquina"):
            nome = st.text_input("Nome da Máquina*")
            localizacao = st.text_input("Localização*")
            status = st.selectbox("Status", ["Disponível", "Manutenção", "Indisponível"])
            if st.form_submit_button("💾 Salvar Máquina"):
                st.success("Máquina cadastrada com sucesso! (Simulação)")
    
    if st.button("⬅️ Voltar"):
        st.session_state.pagina = "inicial"



# 👤 TELA DO USUÁRIO
def tela_usuario():
    st.title("👤 Área do Morador")
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["📅 Visualizar Horários", "⏰ Fazer Agendamento", "📋 Minhas Reservas"])
    
    with tab1:
        st.subheader("Horários Disponíveis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Máquinas de exemplo (depois vem do banco)
            maquinas = ["Máquina 1 - Lavadora", "Máquina 2 - Secadora", "Máquina 3 - Lavadora"]
            maquina_selecionada = st.selectbox("Selecione a máquina:", maquinas)
        
        with col2:
            data_selecionada = st.date_input("Selecione a data")
        
        if st.button("🔍 Ver Horários Disponíveis"):
            # Converter para ID da máquina (mock)
            maquina_id = "M001" if "1" in maquina_selecionada else "M002"
            
            # Usar SEU controlador para buscar horários reais
            horarios_disponiveis = controlador_reserva.visualizar_horarios_disponiveis(
                maquina_id, 
                data_selecionada.strftime("%Y-%m-%d")
            )
            
            st.subheader(f"Horários disponíveis - {maquina_selecionada}")
            
            # Mostrar horários em colunas
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
                maquina = st.selectbox(
                    "Selecione a máquina",
                    ["Máquina 1 - Lavadora (Térreo)", "Máquina 2 - Secadora (Térreo)", "Máquina 3 - Lavadora (1º Andar)"],
                    key="agendamento_maquina"
                )
                
                data_agendamento = st.date_input("Data do agendamento", key="agendamento_data")
            
            with col2:
                # Horários disponíveis para seleção
                horarios = [f"{hora:02d}:00" for hora in range(8, 20)]
                hora_agendamento = st.selectbox("Horário de início", horarios)
                
                usuario = st.text_input("Seu nome*", placeholder="Digite seu nome")
            
            if st.form_submit_button("📅 Fazer Agendamento"):
                if usuario:
                    # Converter para IDs (mock)
                    maquina_id = "M001" if "1" in maquina else "M002"
                    usuario_id = usuario.lower().replace(" ", "")
                    
                    # Usar SEU controlador para fazer reserva real
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
                    st.warning("⚠️ Por favor, digite seu nome.")
    
    with tab3:
        st.subheader("Minhas Reservas")
        
        usuario_consulta = st.text_input("Digite seu nome para ver suas reservas:", 
                                       placeholder="Seu nome", 
                                       key="minhas_reservas")
        
        if usuario_consulta:
            usuario_id = usuario_consulta.lower().replace(" ", "")
            reservas = controlador_reserva.obter_reservas_por_usuario(usuario_id)
            
            if reservas:
                st.success(f"📋 Você tem {len(reservas)} reserva(s) ativa(s)")
                
                for reserva in reservas:
                    with st.expander(f"Reserva {reserva.id_reserva} - {reserva.data} às {reserva.hora_inicio}"):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.write(f"**Máquina ID:** {reserva.maquina_id}")
                            st.write(f"**Data:** {reserva.data}")
                            st.write(f"**Horário:** {reserva.hora_inicio} - {reserva.hora_fim}")
                            st.write(f"**Status:** {reserva.status}")
                        
                        with col2:
                            if st.button("❌ Cancelar", key=f"cancel_{reserva.id_reserva}"):
                                if controlador_reserva.cancelar_reserva(reserva.id_reserva, usuario_id):
                                    st.success("Reserva cancelada com sucesso!")
                                    st.rerun()
            else:
                st.info("📭 Você não possui reservas ativas.")

# 📊 TELA DE RELATÓRIOS
def tela_relatorios():
    st.title("📊 Relatórios de Uso da Lavanderia")
    st.markdown("---")
    # (Mantém seu conteúdo original da função tela_relatorios)
    if st.button("⬅️ Voltar"):
        st.session_state.pagina = "inicial"

# 🚀 EXECUÇÃO PRINCIPAL
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
