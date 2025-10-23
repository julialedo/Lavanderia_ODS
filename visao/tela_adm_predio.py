# View - tela_adm_predio.py
# Interface em Streamlit, recebe o input do usuário, chama o controller, mostra o feedback.

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from controladores.controlador_maquina import ControladorMaquina
from controladores.controlador_reserva import ControladorReserva

# Inicialização dos controladores:
controlador_maquina = ControladorMaquina()
controlador_reserva = ControladorReserva()


# Tela de Gerenciamento de Máquinas:
def gerenciar_maquinas():

    st.subheader("⚙️ Gerenciamento de Máquinas")
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
        st.session_state.subpagina_adm_predio = None
        st.rerun()


# Tela de Relatórios:
def abrir_relatorios():
    st.title("📊 Relatórios de Uso da Lavanderia")
    st.markdown("---")

    # Obtém o ID da lavanderia do usuário logado
    id_lavanderia = st.session_state.get("id_lavanderia")
    
    if not id_lavanderia:
        st.error("❌ ID da lavanderia não encontrado. Faça login novamente.")
        return

    # Container principal com fundo suave
    with st.container():
        st.subheader("📅 Filtro de Período")
        
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            data_inicial = st.date_input("**Data inicial**", help="Selecione a data de início do período")
        with col2:
            data_final = st.date_input("**Data final**", help="Selecione a data final do período")
        with col3:
            st.write("")  # Espaçamento
            gerar_btn = st.button("🚀 **Gerar Relatório**", use_container_width=True, type="primary")

    if gerar_btn:
        try:
            # Verificar se as datas são válidas
            if data_final < data_inicial:
                st.error("❌ A data final não pode ser anterior à data inicial.")
                return

            # Buscar máquinas da lavanderia
            maquinas = controlador_maquina.listar_por_lavanderia(id_lavanderia)
            
            if not maquinas:
                st.info("ℹ️ Nenhuma máquina cadastrada nesta lavanderia.")
                return

            # Buscar reservas no período
            with st.spinner("🔍 Buscando dados..."):
                todas_reservas = controlador_reserva.listar_reservas_periodo(
                    id_lavanderia,
                    data_inicial.strftime("%Y-%m-%d"),
                    data_final.strftime("%Y-%m-%d")
                )

            if not todas_reservas:
                st.info("📭 Nenhuma reserva encontrada nesse período.")
            else:
                # Criar DataFrame com os dados para análise
                dados = []
                for reserva in todas_reservas:
                    dados.append({
                        "ID Reserva": reserva.id_reserva,
                        "Máquina": reserva.id_maquina,
                        "Data": reserva.data_reserva,
                        "Hora Início": reserva.hora_inicio,
                        "Hora Fim": reserva.hora_fim,
                        "Usuário": reserva.id_usuario,
                        "Status": reserva.status_reserva
                    })
                
                df = pd.DataFrame(dados)
                
                # ===== SEÇÃO 1: CARDS DE ESTATÍSTICAS =====
                st.markdown("---")
                st.subheader("📈 Visão Geral")
                
                # Cards de estatísticas
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    total_reservas = len(df)
                    st.metric(
                        label="Total de Reservas", 
                        value=total_reservas,
                        delta=f"{total_reservas} agendamentos"
                    )
                
                with col2:
                    maquinas_ativas = df["Máquina"].nunique()
                    st.metric(
                        label="Máquinas Utilizadas", 
                        value=maquinas_ativas,
                        delta=f"de {len(maquinas)} disponíveis"
                    )
                
                with col3:
                    usuarios_unicos = df["Usuário"].nunique()
                    st.metric(
                        label="Usuários Únicos", 
                        value=usuarios_unicos
                    )
                
                with col4:
                    # Calcular taxa de utilização
                    dias_periodo = (data_final - data_inicial).days + 1
                    horas_por_dia = 12
                    horas_totais_disponiveis = dias_periodo * horas_por_dia * len(maquinas)
                    horas_reservadas = len(df)
                    
                    if horas_totais_disponiveis > 0:
                        taxa_utilizacao = (horas_reservadas / horas_totais_disponiveis) * 100
                    else:
                        taxa_utilizacao = 0
                    
                    st.metric(
                        label="Taxa de Utilização", 
                        value=f"{taxa_utilizacao:.1f}%"
                    )

                # ===== SEÇÃO 2: GRÁFICOS =====
                st.markdown("---")
                st.subheader("📊 Análise Visual")
                
                tab1, tab2, tab3 = st.tabs(["📋 Dados Detalhados", "📈 Gráficos", "🎯 Insights"])
                
                with tab1:
                    # Tabela de dados
                    st.markdown("### 📋 Reservas Detalhadas")
                    st.dataframe(
                        df, 
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "ID Reserva": st.column_config.NumberColumn(format="%d"),
                            "Data": st.column_config.DateColumn(),
                            "Status": st.column_config.TextColumn(
                                help="Status da reserva"
                            )
                        }
                    )
                    
                    # Botão de download
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Exportar para CSV",
                        data=csv,
                        file_name=f"relatorio_lavanderia_{data_inicial}_{data_final}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                
                with tab2:
                    # Gráfico de reservas por máquina
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### ⚙️ Reservas por Máquina")
                        if not df.empty:
                            reservas_por_maquina = df["Máquina"].value_counts()
                            fig1, ax1 = plt.subplots(figsize=(8, 6))
                            cores = plt.cm.Set3(range(len(reservas_por_maquina)))
                            bars = reservas_por_maquina.plot(kind="bar", ax=ax1, color=cores)
                            ax1.set_xlabel("Máquina")
                            ax1.set_ylabel("Número de Reservas")
                            ax1.set_title("Distribuição de Reservas por Máquina", fontsize=14, fontweight='bold')
                            plt.xticks(rotation=45)
                            
                            # Adicionar valores nas barras
                            for i, v in enumerate(reservas_por_maquina):
                                ax1.text(i, v + 0.1, str(v), ha='center', va='bottom')
                            
                            st.pyplot(fig1)
                    
                    with col2:
                        st.markdown("#### 📅 Reservas por Data")
                        if not df.empty:
                            reservas_por_data = df["Data"].value_counts().sort_index()
                            fig2, ax2 = plt.subplots(figsize=(10, 6))
                            reservas_por_data.plot(kind="line", ax=ax2, marker='o', color='#FF6B6B', linewidth=2)
                            ax2.set_xlabel("Data")
                            ax2.set_ylabel("Número de Reservas")
                            ax2.set_title("Evolução das Reservas ao Longo do Tempo", fontsize=14, fontweight='bold')
                            plt.xticks(rotation=45)
                            plt.grid(True, alpha=0.3)
                            st.pyplot(fig2)
                
                with tab3:
                    # Insights automáticos
                    st.markdown("#### 🎯 Insights do Período")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Máquina mais popular
                        if not df.empty:
                            maquina_mais_usada = df["Máquina"].mode()[0]
                            total_maquina_popular = (df["Máquina"] == maquina_mais_usada).sum()
                            
                            st.info(f"**🏆 Máquina mais popular:** {maquina_mais_usada}")
                            st.write(f"Total de reservas: **{total_maquina_popular}**")
                            
                            # Dia da semana com mais reservas
                            df['Data'] = pd.to_datetime(df['Data'])

                            dias_portugues = {
                                'Monday': 'Segunda-feira',
                                'Tuesday': 'Terça-feira', 
                                'Wednesday': 'Quarta-feira',
                                'Thursday': 'Quinta-feira',
                                'Friday': 'Sexta-feira',
                                'Saturday': 'Sábado',
                                'Sunday': 'Domingo'
                            }
                            df['Dia da Semana'] = df['Data'].dt.day_name().map(dias_portugues)
                            dia_mais_movimentado = df['Dia da Semana'].mode()[0]
                            
                            st.info(f"**📅 Dia mais movimentado:** {dia_mais_movimentado}")
                    
                    with col2:
                        # Horário mais popular
                        if not df.empty:
                            horario_mais_popular = df["Hora Início"].mode()[0]
                            total_horario_popular = (df["Hora Início"] == horario_mais_popular).sum()
                            
                            st.success(f"**⏰ Horário mais popular:** {horario_mais_popular}")
                            st.write(f"Total de reservas: **{total_horario_popular}**")
                            
                            # Estatística de uso
                            st.success(f"**📊 Média diária:** {len(df)/dias_periodo:.1f} reservas/dia")

                # ===== SEÇÃO 3: BARRA DE PROGRESSO ESTILIZADA =====
                st.markdown("---")
                st.subheader("⏰ Taxa de Utilização Detalhada")
                
                # Barra de progresso customizada
                progress_col1, progress_col2 = st.columns([3, 1])
                
                with progress_col1:
                    st.write(f"**Utilização:** {horas_reservadas} / {horas_totais_disponiveis} horas")
                    st.progress(int(taxa_utilizacao) / 100)
                    
                    # Interpretação da taxa
                    if taxa_utilizacao >= 80:
                        st.success("🎉 **Excelente utilização!** A lavanderia está sendo bem aproveitada.")
                    elif taxa_utilizacao >= 50:
                        st.info("💡 **Boa utilização!** Há espaço para mais reservas.")
                    elif taxa_utilizacao >= 20:
                        st.warning("📊 **Utilização moderada.** Considere promover a lavanderia.")
                    else:
                        st.error("📉 **Baixa utilização.** Avalie estratégias para aumentar o uso.")
                
                with progress_col2:
                    st.metric(
                        label="Taxa", 
                        value=f"{taxa_utilizacao:.1f}%"
                    )

        except Exception as e:
            st.error(f"❌ Erro ao gerar relatório: {str(e)}")
            st.info("💡 Verifique se as datas estão corretas e se há dados no período selecionado.")

    # Botão de voltar sempre visível
    st.markdown("---")
    col_voltar1, col_voltar2, col_voltar3 = st.columns([1, 2, 1])
    with col_voltar2:
        if st.button("⬅️ Voltar para o Menu Principal", use_container_width=True):
            st.session_state.subpagina_adm_predio = None
            st.rerun()


# Tela inicial do Administrador do Predio:
def tela_adm_predio():

    st.title("👨‍💼 Área do Administrador do Prédio")
    st.markdown("---")

    st.sidebar.title("Menu")
    # Mostrar nome do usuário logado
    if "usuario" in st.session_state:
        st.sidebar.write(f"👤 Usuário: {st.session_state['usuario']}")
    # Botão de logout
    if st.sidebar.button("🚪 Sair"):
        st.session_state.clear()
        st.rerun()

    # Exibe o código/nome da lavanderia se estiver na session_state
    codigo_lavanderia = st.session_state.get("codigo_lavanderia", "Não Definido")
    st.subheader(f"Lavanderia: **{codigo_lavanderia}**")
    st.markdown("---")
    # ----------------------------------------------------

    # VERIFICAÇÃO PRINCIPAL DA SUBPÁGINA - DEVE VIR ANTES DOS BOTÕES
    if st.session_state.get("subpagina_adm_predio") == "gerenciar_maquinas":
        gerenciar_maquinas()
        return  # IMPORTANTE: return para não mostrar o resto
    
    elif st.session_state.get("subpagina_adm_predio") == "abrir_relatorios":
        abrir_relatorios()
        return  # IMPORTANTE: return para não mostrar o resto

    # SE CHEGOU AQUI, MOSTRA A TELA PRINCIPAL COM OS BOTÕES
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("⚙️ Gerenciar Máquinas")
        if st.button("Gerenciar Máquinas", use_container_width=True, key="btn_maquinas"):
            st.session_state["subpagina_adm_predio"] = "gerenciar_maquinas"
            st.rerun()

    with col2:
        st.subheader("📊 Relatórios")
        if st.button("Abrir Relatórios", use_container_width=True, key="btn_relatorios"):
            st.session_state["subpagina_adm_predio"] = "abrir_relatorios"
            st.rerun()

    st.markdown("---")


# Execução Principal
tela_adm_predio()
