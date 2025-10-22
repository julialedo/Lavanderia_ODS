# View - tela_morador.py
# Interface em Streamlit, recebe o input do usuário, chama o controller, mostra o feedback.

import streamlit as st
from controladores.controlador_reserva import ControladorReserva
from controladores.controlador_maquina import ControladorMaquina

# Inicialização dos controladores:
controlador_reserva = ControladorReserva()
controlador_maquina = ControladorMaquina()


# Tela inicial do Morador:
def tela_morador():
    
    st.title("👤 Área do Morador")
    st.markdown("---")
    
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
                