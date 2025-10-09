import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

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
    
    tab1, tab2 = st.tabs(["📅 Visualizar Horários", "⏰ Fazer Agendamento"])
    
    with tab1:
        st.subheader("Horários Disponíveis")
        
        # Seleção de data
        data_selecionada = st.date_input("Selecione a data")
        
        # Máquinas de exemplo
        st.subheader("Máquina 1 - Lavadora (Térreo)")
        
        # Horários de exemplo
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.write("**08:00**")
            st.success("✅ Disponível")
            
            st.write("**12:00**")
            st.error("❌ Ocupado")
            
            st.write("**16:00**")
            st.success("✅ Disponível")
        
        with col2:
            st.write("**09:00**")
            st.error("❌ Ocupado")
            
            st.write("**13:00**")
            st.success("✅ Disponível")
            
            st.write("**17:00**")
            st.error("❌ Ocupado")
        
        with col3:
            st.write("**10:00**")
            st.success("✅ Disponível")
            
            st.write("**14:00**")
            st.success("✅ Disponível")
            
            st.write("**18:00**")
            st.success("✅ Disponível")
        
        with col4:
            st.write("**11:00**")
            st.error("❌ Ocupado")
            
            st.write("**15:00**")
            st.success("✅ Disponível")
            
            st.write("**19:00**")
            st.success("✅ Disponível")
    
    with tab2:
        st.subheader("Agendar Máquina")
        
        with st.form("agendamento_form"):
            maquina = st.selectbox(
                "Selecione a máquina",
                ["Máquina 1 - Lavadora (Térreo)", "Máquina 2 - Secadora (Térreo)", "Máquina 3 - Lavadora (1º Andar)"]
            )
            
            data_agendamento = st.date_input("Data do agendamento")
            hora_agendamento = st.time_input("Hora de início")
            usuario = st.text_input("Seu nome*", placeholder="Digite seu nome")
            
            if st.form_submit_button("📅 Fazer Agendamento"):
                st.success("Agendamento realizado com sucesso! (Simulação)")
                
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
