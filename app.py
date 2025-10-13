import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from controladores.controlador_reserva import ControladorReserva

controlador_reserva = ControladorReserva()

st.set_page_config(
    page_title="Gerenciador de Lavanderia Compartilhada",
    page_icon="🧺",
    layout="wide"
)
# Tela inicial
def tela_inicial():
    st.title("🧺 Gerenciador de Lavanderia Compartilhada")
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("👨‍💼 Área do Administrador")
        st.write("Cadastre, edite ou exclua máquinas da lavanderia")
        if st.button("Gerenciar Máquinas", key="admin_btn", use_container_width=True):
            st.session_state.pagina = "admin"
    
    with col2:
        st.subheader("👤 Área dos Moradores")
        st.write("Visualize horários disponíveis e agende sua máquina")
        if st.button("Visualizar Horários", key="user_btn", use_container_width=True):
            st.session_state.pagina = "usuario"

    with col3:
        st.subheader("📊 Relatórios")
        st.write("Visualize estatísticas e relatórios de uso")
        if st.button("Gerar Relatórios", key="report_btn", use_container_width=True):
            st.session_state.pagina = "relatorios"


def tela_admin():
    st.title("👨‍💼 Gerenciamento de Máquinas")
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["📋 Lista de Máquinas", "➕ Nova Máquina"])
    
    with tab1:
        st.subheader("Máquinas Cadastradas")
        
        # Máquinas de exemplo
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
                    st.write(f"**Localização:** {maquina['localizacao']}")
                
                with col2:
                    st.button("✏️ Editar", key=f"edit_{maquina['nome']}")
                
                with col3:
                    st.button("🗑️ Excluir", key=f"del_{maquina['nome']}")
    
    with tab2:
        st.subheader("Cadastrar Nova Máquina")
        
        with st.form("nova_maquina"):
            nome = st.text_input("Nome da Máquina*", placeholder="Ex: Máquina 1 - Lavadora")
            localizacao = st.text_input("Localização*", placeholder="Ex: Térreo, 1º Andar")
            status = st.selectbox("Status", ["Disponível", "Manutenção", "Indisponível"])
            
            if st.form_submit_button("💾 Salvar Máquina"):
                st.success("Máquina cadastrada com sucesso! (Simulação)")

    st.markdown("---")
    if st.button("⬅️ Voltar para Tela Inicial"):
        st.session_state.pagina = "inicial"



# Tela do usuário
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

                
# Tela de Relatorios
def tela_relatorios():
    st.title("👤 Relatorios de uso da Lavanderia")
    st.markdown("---")

    dados = {
        "Máquina": ["Lava-01", "Seca-01", "Lava-02", "Seca-01", "Lava-01"],
        "Usuário": ["Ana", "Marcus", "Thalia", "Gustavo", "Ana"],
        "Data": ["2025-09-10", "2025-09-11", "2025-09-12", "2025-09-12", "2025-09-13"],
        "Duração (min)": [45, 60, 50, 55, 40]
    }
    df = pd.DataFrame(dados)
    df["Data"] = pd.to_datetime(df["Data"])
    
    st.sidebar.header("Filtros")
    data_inicio = st.sidebar.date_input("Data inicial", df["Data"].min())
    data_fim = st.sidebar.date_input("Data final", df["Data"].max())
    maquina = st.sidebar.selectbox("Selecionar máquina", ["Todas"] + df["Máquina"].unique().tolist())
    
    df_filtrado = df[(df["Data"] >= pd.to_datetime(data_inicio)) & (df["Data"] <= pd.to_datetime(data_fim))]
    if maquina != "Todas":
        df_filtrado = df_filtrado[df_filtrado["Máquina"] == maquina]
    
    st.subheader("📋 Dados filtrados")
    st.dataframe(df_filtrado)
    
    st.subheader("📈 Estatísticas")
    if not df_filtrado.empty:
        st.write(f"✅ Total de registros: {len(df_filtrado)}")
        st.write(f"⏱️ Tempo médio de uso: {df_filtrado['Duração (min)'].mean():.2f} minutos")
    else:
        st.warning("Nenhum dado encontrado para os filtros selecionados.")
    
    if not df_filtrado.empty:
        st.subheader("📊 Gráfico de uso por máquina")
        fig, ax = plt.subplots()
        df_filtrado.groupby("Máquina")["Duração (min)"].sum().plot(kind="bar", ax=ax, color="skyblue")
        ax.set_ylabel("Tempo total (min)")
        st.pyplot(fig)
    
    st.download_button(
        label="📥 Baixar Relatório em CSV",
        data=df_filtrado.to_csv(index=False),
        file_name="relatorio_lavanderia.csv",
        mime="text/csv"
    )

    st.markdown("---")
    if st.button("⬅️ Voltar para Tela Inicial"):
        st.session_state.pagina = "inicial"

             
if 'pagina' not in st.session_state:
    st.session_state.pagina = "inicial"

if st.session_state.pagina == "inicial":
    tela_inicial()

elif st.session_state.pagina == "admin":
    tela_admin()

elif st.session_state.pagina == "usuario":
    tela_usuario()

elif st.session_state.pagina == "relatorios":
    tela_relatorios()
