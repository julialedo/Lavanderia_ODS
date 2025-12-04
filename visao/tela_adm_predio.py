# View - tela_adm_predio.py
# Interface em Streamlit, recebe o input do usuário, chama o controller, mostra o feedback.
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from controladores.controlador_maquina import ControladorMaquina
from controladores.controlador_reserva import ControladorReserva
from controladores.controlador_usuario import ControladorUsuario
from controladores.controlador_ocorrencia import ControladorOcorrencia

# Inicialização dos controladores:
controlador_maquina = ControladorMaquina()
controlador_reserva = ControladorReserva()
controlador_usuario = ControladorUsuario()
controlador_ocorrencia = ControladorOcorrencia()

# Tela de Aprovação de Moradores:


def aprovar_moradores():
    st.subheader("👥 Aprovar Moradores Cadastrados")
    st.markdown("---")

    # Obter ID da lavanderia do admin logado
    id_lavanderia_admin = st.session_state.get("id_lavanderia")
    if not id_lavanderia_admin:
        st.error("❌ ID da lavanderia não encontrado.")
        return

    st.info("Aqui você pode aprovar ou rejeitar cadastros de novos moradores.")

    # Buscar moradores pendentes
    try:
        moradores_pendentes = controlador_usuario.listar_moradores_pendentes(
            id_lavanderia_admin)

        if not moradores_pendentes:
            st.success("🎉 Não há moradores aguardando aprovação!")

            # Botão para atualizar lista
            if st.button("🔄 Atualizar Lista", key="atualizar_lista_moradores"):
                st.rerun()
        else:
            st.warning(
                f"📋 {len(moradores_pendentes)} morador(es) aguardando aprovação")

            # Exibir em formato de cards
            for i, morador in enumerate(moradores_pendentes):
                with st.container():
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.markdown(f"### 👤 {morador['nome']}")
                        st.write(f"**📧 Email:** {morador['email']}")
                        st.write(f"**📞 Telefone:** {morador['telefone']}")
                        st.write(
                            f"**📅 Data do Cadastro:** {morador['data_cadastro_usuario']}")

                    with col2:
                        st.markdown("### Ações")
                        col_aprovar, col_rejeitar = st.columns(2)

                        with col_aprovar:
                            if st.button("✅ Aprovar", key=f"aprovar_{morador['id_usuario']}",
                                         use_container_width=True, type="primary"):
                                try:
                                    if controlador_usuario.aprovar_morador(morador['id_usuario']):
                                        st.success(
                                            f"🎉 Morador **{morador['nome']}** aprovado com sucesso!")
                                        st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Erro: {str(e)}")

                        with col_rejeitar:
                            if st.button("❌ Rejeitar", key=f"rejeitar_{morador['id_usuario']}",
                                         use_container_width=True, type="secondary"):
                                try:
                                    if controlador_usuario.rejeitar_morador(morador['id_usuario']):
                                        st.success(
                                            f"🗑️ Morador **{morador['nome']}** rejeitado")
                                        st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Erro: {str(e)}")

                    if i < len(moradores_pendentes) - 1:
                        st.markdown("---")

    except Exception as e:
        st.error(f"❌ Erro ao carregar moradores pendentes: {str(e)}")

    st.markdown("---")
    if st.button("⬅️ Voltar ao Menu Principal"):
        st.session_state.subpagina_adm_predio = None
        st.rerun()

# Tela de Gerenciamento de Máquinas:


def gerenciar_maquinas():
    st.subheader("⚙️ Gerenciamento de Máquinas")
    st.markdown("---")

    # Verifica se está editando uma máquina específica
    if "editar_maquina" in st.session_state:
        editar_maquina_screen()
        return

    # Cadastrar Máquinas - Formulário
    with st.expander("➕ Cadastrar Nova Máquina"):
        with st.form("nova_maquina"):
            codigo = st.text_input("Código da Máquina (ex: LAV-01, SEC-07)")
            tipo = st.selectbox("Tipo da Máquina", ["lavadora", "secadora"])
            capacidade = st.text_input("Capacidade (ex: 8kg)")
            status = st.selectbox(
                "Status Inicial", ["livre", "em_uso", "manutencao"])
            btn = st.form_submit_button("Cadastrar")
            if btn:
                if not codigo:
                    st.error("❌ O código da máquina é obrigatório!")
                elif not capacidade:
                    st.error("❌ A capacidade da máquina é obrigatória!")
                else:
                    try:
                        new_id = controlador_maquina.cadastrar_maquina(
                            st.session_state["id_lavanderia"],
                            codigo, tipo, capacidade, status
                        )
                        st.success(
                            f"✅ Máquina cadastrada com sucesso! ID: {new_id}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Erro ao cadastrar máquina: {str(e)}")

    st.markdown("---")

    # Listar as Máquinas Cadastradas
    st.subheader("📋 Máquinas cadastradas")
    try:
        maquinas = controlador_maquina.listar_por_lavanderia(
            st.session_state["id_lavanderia"])

        if not maquinas:
            st.info("ℹ️ Nenhuma máquina cadastrada para esta Lavanderia!")
        else:
            for maq in maquinas:
                with st.expander(f"⚙️ {maq.codigo_maquina} - {maq.tipo_maquina.capitalize()} ({maq.capacidade})"):
                    col1, col2, col3 = st.columns([3, 1, 1])

                    with col1:
                        st.write(f"**Status atual:** {maq.status_maquina}")
                        st.write(f"**Tipo:** {maq.tipo_maquina}")
                        st.write(f"**Capacidade:** {maq.capacidade}")
                        st.write(f"**ID:** {maq.id_maquina}")

                    with col2:
                        if st.button("✏️ Editar", key=f"edit_{maq.id_maquina}", use_container_width=True):
                            st.session_state["editar_maquina"] = maq.id_maquina
                            st.rerun()

                    with col3:
                        if st.button("🗑️ Excluir", key=f"del_{maq.id_maquina}", use_container_width=True):
                            try:
                                ok = controlador_maquina.remover_maquina(
                                    maq.id_maquina)
                                if ok:
                                    st.success(
                                        "✅ Máquina removida com sucesso!")
                                    st.rerun()
                                else:
                                    st.error("❌ Erro ao remover máquina.")
                            except Exception as e:
                                st.error(f"❌ Erro: {str(e)}")
    except Exception as e:
        st.error(f"❌ Erro ao carregar máquinas: {str(e)}")

    st.markdown("---")
    if st.button("⬅️ Voltar ao Menu Principal"):
        st.session_state.subpagina_adm_predio = None
        st.rerun()

# Tela de Edição de Máquina (seguindo o padrão do Editar Perfil)


def editar_maquina_screen():
    st.subheader("✏️ Editar Máquina")
    st.markdown("---")

    maq_id = st.session_state["editar_maquina"]

    try:
        maquina = controlador_maquina.obter(maq_id)

        if not maquina:
            st.error("❌ Máquina não encontrada!")
            if st.button("⬅️ Voltar"):
                del st.session_state["editar_maquina"]
                st.rerun()
            return

        with st.form("form_editar_maquina"):
            st.write("**Informações da Máquina**")

            col1, col2 = st.columns(2)

            with col1:
                codigo_novo = st.text_input(
                    "Código da Máquina*",
                    value=maquina.codigo_maquina,
                    help="Código único para identificação (ex: LAV-01, SEC-07)"
                )

                tipo_novo = st.selectbox(
                    "Tipo da Máquina*",
                    options=["lavadora", "secadora"],
                    index=0 if maquina.tipo_maquina == "lavadora" else 1
                )

            with col2:
                capacidade_nova = st.text_input(
                    "Capacidade*",
                    value=maquina.capacidade,
                    help="Capacidade em kg (ex: 8kg, 12kg)"
                )

                status_novo = st.selectbox(
                    "Status*",
                    options=["livre", "em_uso", "manutencao"],
                    index=["livre", "em_uso", "manutencao"].index(
                        maquina.status_maquina)
                )

            st.caption("* Campos obrigatórios")

            st.markdown("---")

            col_btn1, col_btn2 = st.columns([1, 1])

            with col_btn1:
                salvar = st.form_submit_button(
                    "💾 Salvar Alterações",
                    use_container_width=True,
                    type="primary"
                )

            with col_btn2:
                cancelar = st.form_submit_button(
                    "❌ Cancelar",
                    use_container_width=True
                )

            if salvar:
                # Validações
                if not codigo_novo:
                    st.error("❌ O código da máquina é obrigatório!")
                    return

                if not capacidade_nova:
                    st.error("❌ A capacidade da máquina é obrigatória!")
                    return

                # Preparar campos para atualização
                campos = {
                    "codigo_maquina": codigo_novo,
                    "tipo_maquina": tipo_novo,
                    "capacidade": capacidade_nova,
                    "status_maquina": status_novo
                }

                try:
                    ok = controlador_maquina.editar_maquina(maq_id, campos)
                    if ok:
                        st.success("✅ Máquina atualizada com sucesso!")
                        del st.session_state["editar_maquina"]
                        st.rerun()
                    else:
                        st.warning(
                            "⚠️ Nenhuma alteração detectada ou máquina não encontrada.")

                except Exception as e:
                    st.error(f"❌ Erro ao atualizar máquina: {str(e)}")

            if cancelar:
                st.info("ℹ️ Alterações canceladas.")
                del st.session_state["editar_maquina"]
                st.rerun()

    except Exception as e:
        st.error(f"❌ Erro ao carregar dados da máquina: {str(e)}")

        st.markdown("---")
        if st.button("⬅️ Voltar", use_container_width=True):
            del st.session_state["editar_maquina"]
            st.rerun()

# Tela de Gerenciamento de Manutenções:


def gerenciar_manutencoes():
    """Tela de gerenciamento de manutenções"""
    st.subheader("🔧 Gerenciamento de Manutenções")
    st.markdown("---")

    # Inicializar controlador
    from controladores.controlador_manutencao import ControladorManutencao
    controlador_manutencao = ControladorManutencao()

    id_lavanderia = st.session_state.get("id_lavanderia")
    if not id_lavanderia:
        st.error("❌ ID da lavanderia não encontrado.")
        return

    # Obter nome do admin logado
    nome_adm = st.session_state.get("usuario", "Administrador")

    # Abas para diferentes funcionalidades
    tab1, tab2, tab3 = st.tabs(
        ["📅 Agendar Preventiva", "🔧 Registrar Realizada", "📋 Histórico"])

    with tab1:
        st.subheader("📅 Agendar Manutenção Preventiva")

        # Buscar máquinas da lavanderia
        from controladores.controlador_maquina import ControladorMaquina
        controlador_maquina = ControladorMaquina()
        maquinas = controlador_maquina.listar_por_lavanderia(id_lavanderia)

        if not maquinas:
            st.info("ℹ️ Nenhuma máquina cadastrada para agendar manutenção.")
        else:
            with st.form("form_agendar_manutencao"):
                # Selecionar máquina
                opcoes_maquinas = {
                    f"{maq.codigo_maquina} - {maq.tipo_maquina}": maq.id_maquina for maq in maquinas}
                maquina_selecionada = st.selectbox(
                    "Máquina*", list(opcoes_maquinas.keys()))

                col1, col2 = st.columns(2)
                with col1:
                    # Data de agendamento
                    data_agendada = st.date_input(
                        "Data de Agendamento*", min_value=datetime.now().date())
                with col2:
                    # Hora de agendamento
                    hora_agendada = st.time_input(
                        "Hora de Agendamento*", value=datetime.now().time())

                # Descrição
                descricao = st.text_area("Descrição da Manutenção*",
                                         placeholder="Descreva os serviços de manutenção preventiva a serem realizados...",
                                         height=100)

                # Nome do admin (pré-preenchido)
                nome_adm_input = st.text_input(
                    "Nome do Administrador*", value=nome_adm)

                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.form_submit_button("📅 Agendar Manutenção", use_container_width=True):
                        # DEBUG NO STREAMLIT
                        st.write(f"🔍 DEBUG STREAMLIT:")
                        st.write(
                            f"Data selecionada: {data_agendada} (tipo: {type(data_agendada)})")
                        st.write(
                            f"Hora selecionada: {hora_agendada} (tipo: {type(hora_agendada)})")
                        st.write(
                            f"Data formatada: {data_agendada.strftime('%Y-%m-%d')}")
                        st.write(
                            f"Hora formatada: {hora_agendada.strftime('%H:%M:%S')}")

                        try:
                            id_maquina = opcoes_maquinas[maquina_selecionada]
                            manutencao_id = controlador_manutencao.agendar_manutencao_preventiva(
                                id_maquina=id_maquina,
                                data_agendada=data_agendada.strftime(
                                    "%Y-%m-%d"),
                                hora_agendada=hora_agendada,  # ENVIAR O OBJETO TIME DIRETO
                                descricao=descricao,
                                nome_adm=nome_adm_input
                            )
                            st.success(
                                f"✅ Manutenção preventiva agendada com sucesso! ID: {manutencao_id}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Erro ao agendar manutenção: {str(e)}")
                with col2:
                    if st.form_submit_button("🔄 Limpar", use_container_width=True):
                        st.rerun()

    with tab2:
        st.subheader("🔧 Registrar Manutenção Realizada")

        maquinas = controlador_maquina.listar_por_lavanderia(id_lavanderia)

        if not maquinas:
            st.info("ℹ️ Nenhuma máquina cadastrada.")
        else:
            with st.form("form_registrar_manutencao"):
                # Selecionar máquina
                opcoes_maquinas = {
                    f"{maq.codigo_maquina} - {maq.tipo_maquina}": maq.id_maquina for maq in maquinas}
                maquina_selecionada = st.selectbox(
                    "Máquina*", list(opcoes_maquinas.keys()), key="corretiva")

                # Data de realização
                data_realizada = st.date_input(
                    "Data de Realização*", value=datetime.now().date(), key="data_realizada")

                # Descrição do problema/reparo
                descricao = st.text_area("Descrição do Reparo/Manutenção*",
                                         placeholder="Descreva o problema encontrado e o reparo realizado...",
                                         height=100)

                # Nome do admin
                nome_adm_input = st.text_input(
                    "Nome do Administrador*", value=nome_adm, key="nome_adm_corretiva")

                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.form_submit_button("💾 Registrar Manutenção", use_container_width=True):
                        try:
                            id_maquina = opcoes_maquinas[maquina_selecionada]
                            # CORREÇÃO: função sem acento
                            manutencao_id = controlador_manutencao.registrar_manutencao_realizada(
                                id_maquina=id_maquina,
                                descricao=descricao,
                                nome_adm=nome_adm_input,
                                data_realizada=data_realizada.strftime(
                                    "%Y-%m-%d")
                            )
                            st.success(
                                f"✅ Manutenção registrada com sucesso! ID: {manutencao_id}")
                            st.rerun()
                        except Exception as e:
                            st.error(
                                f"❌ Erro ao registrar manutenção: {str(e)}")
                with col2:
                    if st.form_submit_button("🔄 Limpar", use_container_width=True):
                        st.rerun()

    with tab3:
        st.subheader("📋 Histórico de Manutenções")

        # Mostrar manutenções pendentes primeiro
        st.markdown("#### 🔔 Manutenções Pendentes")
        try:
            manutencoes_pendentes = controlador_manutencao.listar_manutencoes_pendentes(
                id_lavanderia)

            if not manutencoes_pendentes:
                st.success("🎉 Nenhuma manutenção pendente!")
            else:
                st.warning(
                    f"⚠️ Você tem {len(manutencoes_pendentes)} manutenção(ões) pendente(s)")

                for manutencao in manutencoes_pendentes:
                    # CORREÇÃO: Formatar data e hora para exibição correta
                    data_formatada = manutencao.data_agendada
                    if isinstance(data_formatada, str) and ' ' in data_formatada:
                        # Se data_agendada contém data e hora
                        data_parts = data_formatada.split(' ')
                        data_str = data_parts[0]
                        hora_str = data_parts[1] if len(data_parts) > 1 else ''

                        # Formatar a data para exibição (DD/MM/AAAA)
                        try:
                            data_obj = datetime.strptime(data_str, "%Y-%m-%d")
                            data_formatada_br = data_obj.strftime("%d/%m/%Y")

                            # Formatar a hora (remover segundos se existirem)
                            if hora_str and ':' in hora_str:
                                hora_parts = hora_str.split(':')
                                if len(hora_parts) >= 2:
                                    hora_formatada = f"{hora_parts[0]}:{hora_parts[1]}"
                                    data_formatada = f"{data_formatada_br} {hora_formatada}"
                                else:
                                    data_formatada = f"{data_formatada_br} {hora_str}"
                            else:
                                data_formatada = f"{data_formatada_br} {hora_str}"
                        except:
                            data_formatada = f"{data_str} {hora_str}"

                    with st.expander(f"📅 Manutenção #{manutencao.id_manutencao} - Agendada: {data_formatada}"):
                        col1, col2 = st.columns([3, 1])

                        with col1:
                            st.write(
                                f"**Máquina ID:** {manutencao.id_maquina}")
                            st.write(
                                f"**Data Agendada:** {data_formatada}")
                            st.write(
                                f"**Agendado por:** {manutencao.nome_adm}")
                            st.write(f"**Descrição:** {manutencao.descricao}")

                        with col2:
                            if st.button("✅ Marcar como Realizada", key=f"realizar_{manutencao.id_manutencao}"):
                                if controlador_manutencao.marcar_como_realizada(manutencao.id_manutencao):
                                    st.success(
                                        "Manutenção marcada como realizada!")
                                    st.rerun()
                                else:
                                    st.error("Erro ao marcar como realizada")
        except Exception as e:
            st.error(f"❌ Erro ao carregar manutenções pendentes: {str(e)}")

        st.markdown("---")
        st.markdown("#### 📊 Todas as Manutenções")

        try:
            todas_manutencoes = controlador_manutencao.listar_manutencoes(
                id_lavanderia)

            if not todas_manutencoes:
                st.info("ℹ️ Nenhuma manutenção registrada.")
            else:
                # Filtros
                col1, col2 = st.columns(2)
                with col1:
                    filtro_tipo = st.selectbox("Filtrar por Status", [
                                               "Todas", "Pendentes", "Realizadas"])

                # Aplicar filtros
                if filtro_tipo == "Pendentes":
                    manutencoes_filtradas = [
                        m for m in todas_manutencoes if m.data_realizada is None]
                elif filtro_tipo == "Realizadas":
                    manutencoes_filtradas = [
                        m for m in todas_manutencoes if m.data_realizada is not None]
                else:
                    manutencoes_filtradas = todas_manutencoes

                st.info(
                    f"📊 Mostrando {len(manutencoes_filtradas)} manutenção(ões)")

                for manutencao in manutencoes_filtradas:
                    # Determinar ícone e cor
                    if manutencao.data_realizada:
                        icone = "✅"
                        status = "Realizada"
                    else:
                        icone = "📅"
                        status = "Pendente"

                    # CORREÇÃO: Formatar data e hora para exibição correta
                    data_formatada = manutencao.data_agendada
                    if isinstance(data_formatada, str) and ' ' in data_formatada:
                        # Se data_agendada contém data e hora
                        data_parts = data_formatada.split(' ')
                        data_str = data_parts[0]
                        hora_str = data_parts[1] if len(data_parts) > 1 else ''

                        # Formatar a data para exibição (DD/MM/AAAA)
                        try:
                            data_obj = datetime.strptime(data_str, "%Y-%m-%d")
                            data_formatada_br = data_obj.strftime("%d/%m/%Y")

                            # Formatar a hora (remover segundos se existirem)
                            if hora_str and ':' in hora_str:
                                hora_parts = hora_str.split(':')
                                if len(hora_parts) >= 2:
                                    hora_formatada = f"{hora_parts[0]}:{hora_parts[1]}"
                                    data_formatada = f"{data_formatada_br} {hora_formatada}"
                                else:
                                    data_formatada = f"{data_formatada_br} {hora_str}"
                            else:
                                data_formatada = f"{data_formatada_br} {hora_str}"
                        except:
                            data_formatada = f"{data_str} {hora_str}"

                    with st.expander(f"{icone} Manutenção #{manutencao.id_manutencao} - {status}"):
                        col1, col2 = st.columns(2)

                        with col1:
                            st.write(
                                f"**Máquina ID:** {manutencao.id_maquina}")
                            st.write(
                                f"**Data Agendada:** {data_formatada}")
                            st.write(
                                f"**Agendado por:** {manutencao.nome_adm}")

                        with col2:
                            if manutencao.data_realizada:
                                st.write(
                                    f"**Data Realizada:** {manutencao.data_realizada}")
                                st.success("✅ Concluída")
                            else:
                                st.warning("📅 Pendente")
                                if st.button("✅ Marcar como Realizada", key=f"realizar_hist_{manutencao.id_manutencao}"):
                                    if controlador_manutencao.marcar_como_realizada(manutencao.id_manutencao):
                                        st.success(
                                            "Manutenção marcada como realizada!")
                                        st.rerun()

                        st.write(f"**Descrição:** {manutencao.descricao}")

        except Exception as e:
            st.error(f"❌ Erro ao carregar histórico: {str(e)}")

    st.markdown("---")
    if st.button("⬅️ Voltar ao Menu Principal"):
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
            data_inicial = st.date_input(
                "**Data inicial**", help="Selecione a data de início do período")

        with col2:
            data_final = st.date_input(
                "**Data final**", help="Selecione a data final do período")

        with col3:
            st.write("")  # Espaçamento
            gerar_btn = st.button("🚀 **Gerar Relatório**",
                                  use_container_width=True, type="primary")

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
                    horas_totais_disponiveis = dias_periodo * \
                        horas_por_dia * len(maquinas)
                    horas_reservadas = len(df)

                    if horas_totais_disponiveis > 0:
                        taxa_utilizacao = (
                            horas_reservadas / horas_totais_disponiveis) * 100
                    else:
                        taxa_utilizacao = 0

                    st.metric(
                        label="Taxa de Utilização",
                        value=f"{taxa_utilizacao:.1f}%"
                    )

                # ===== SEÇÃO 2: GRÁFICOS =====
                st.markdown("---")
                st.subheader("📊 Análise Visual")

                tab1, tab2, tab3 = st.tabs(
                    ["📋 Dados Detalhados", "📈 Gráficos", "🎯 Insights"])

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
                            cores = plt.cm.Set3(
                                range(len(reservas_por_maquina)))
                            bars = reservas_por_maquina.plot(
                                kind="bar", ax=ax1, color=cores)
                            ax1.set_xlabel("Máquina")
                            ax1.set_ylabel("Número de Reservas")
                            ax1.set_title(
                                "Distribuição de Reservas por Máquina", fontsize=14, fontweight='bold')
                            plt.xticks(rotation=45)
                            # Adicionar valores nas barras
                            for i, v in enumerate(reservas_por_maquina):
                                ax1.text(i, v + 0.1, str(v),
                                         ha='center', va='bottom')
                            st.pyplot(fig1)

                    with col2:
                        st.markdown("#### 📅 Reservas por Data")
                        if not df.empty:
                            reservas_por_data = df["Data"].value_counts(
                            ).sort_index()
                            fig2, ax2 = plt.subplots(figsize=(10, 6))
                            reservas_por_data.plot(
                                kind="line", ax=ax2, marker='o', color='#FF6B6B', linewidth=2)
                            ax2.set_xlabel("Data")
                            ax2.set_ylabel("Número de Reservas")
                            ax2.set_title(
                                "Evolução das Reservas ao Longo do Tempo", fontsize=14, fontweight='bold')
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
                            total_maquina_popular = (
                                df["Máquina"] == maquina_mais_usada).sum()
                            st.info(
                                f"**🏆 Máquina mais popular:** {maquina_mais_usada}")
                            st.write(
                                f"Total de reservas: **{total_maquina_popular}**")

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
                        df['Dia da Semana'] = df['Data'].dt.day_name().map(
                            dias_portugues)
                        dia_mais_movimentado = df['Dia da Semana'].mode()[0]
                        st.info(
                            f"**📅 Dia mais movimentado:** {dia_mais_movimentado}")

                    with col2:
                        # Horário mais popular
                        if not df.empty:
                            horario_mais_popular = df["Hora Início"].mode()[0]
                            total_horario_popular = (
                                df["Hora Início"] == horario_mais_popular).sum()
                            st.success(
                                f"**⏰ Horário mais popular:** {horario_mais_popular}")
                            st.write(
                                f"Total de reservas: **{total_horario_popular}**")

                        # Estatística de uso
                        st.success(
                            f"**📊 Média diária:** {len(df)/dias_periodo:.1f} reservas/dia")

                # ===== SEÇÃO 3: BARRA DE PROGRESSO ESTILIZADA =====
                st.markdown("---")
                st.subheader("⏰ Taxa de Utilização Detalhada")

                # Barra de progresso customizada
                progress_col1, progress_col2 = st.columns([3, 1])

                with progress_col1:
                    st.write(
                        f"**Utilização:** {horas_reservadas} / {horas_totais_disponiveis} horas")
                    st.progress(int(taxa_utilizacao) / 100)

                    # Interpretação da taxa
                    if taxa_utilizacao >= 80:
                        st.success(
                            "🎉 **Excelente utilização!** A lavanderia está sendo bem aproveitada.")
                    elif taxa_utilizacao >= 50:
                        st.info(
                            "💡 **Boa utilização!** Há espaço para mais reservas.")
                    elif taxa_utilizacao >= 20:
                        st.warning(
                            "📊 **Utilização moderada.** Considere promover a lavanderia.")
                    else:
                        st.error(
                            "📉 **Baixa utilização.** Avalie estratégias para aumentar o uso.")

                with progress_col2:
                    st.metric(
                        label="Taxa",
                        value=f"{taxa_utilizacao:.1f}%"
                    )

        except Exception as e:
            st.error(f"❌ Erro ao gerar relatório: {str(e)}")
            st.info(
                "💡 Verifique se as datas estão corretas e se há dados no período selecionado.")

    # Botão de voltar sempre visível
    st.markdown("---")
    col_voltar1, col_voltar2, col_voltar3 = st.columns([1, 2, 1])
    with col_voltar2:
        if st.button("⬅️ Voltar para o Menu Principal", use_container_width=True):
            st.session_state.subpagina_adm_predio = None
            st.rerun()


def visualizar_ocorrencias():
    """Renderiza a página de gerenciamento de ocorrências."""
    st.subheader("⚠️ Gerenciamento de Ocorrências")
    st.markdown("---")
    id_lavanderia_admin = st.session_state.get("id_lavanderia")
    if not id_lavanderia_admin:
        st.error("❌ ID da lavanderia do admin não encontrado na sessão.")
        st.markdown("---")
        if st.button("⬅️ Voltar ao Menu Principal"):
            st.session_state.subpagina_adm_predio = None
            st.rerun()
        return  # Para a execução

    try:
        # Busca todas as ocorrências
        ocorrencias = controlador_ocorrencia.listar_ocorrencias_para_admin(
            id_lavanderia_admin)

        if not ocorrencias:
            st.info("🎉 Nenhuma ocorrência reportada. Tudo em ordem!")
            st.markdown("---")
        else:
            # Separar em abertas e resolvidas
            abertas = ocorrencias

            # --- Seção de Ocorrências Abertas ---
            st.markdown("### 🔔 Ocorrências Abertas")
            if not abertas:
                st.success("✅ Nenhuma ocorrência aberta no momento.")
            else:
                st.error(f"Você tem {len(abertas)} ocorrência(s) ")
                for oc in abertas:
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        with st.expander(f"ID #{oc.id_problema} - Data: {oc.data_problema}"):
                            st.write(f"**Reportado por:** {oc.nome_usuario}")
                            st.write(
                                f"**Máquina:** {oc.id_maquina if oc.id_maquina else 'N/A'}")
                            st.write(f"**Descrição:**")
                            st.warning(f"_{oc.descricao}_")

    except Exception as e:
        st.error(f"❌ Erro ao carregar ocorrências: {e}")

    st.markdown("---")
    if st.button("⬅️ Voltar ao Menu Principal"):
        st.session_state.subpagina_adm_predio = None
        st.rerun()

# Função para carregar dados do usuário


def carregar_dados_usuario():
    """Carrega os dados do usuário logado na session_state se não existirem"""
    if "usuario_dados" not in st.session_state and "id_usuario" in st.session_state:
        try:
            usuario_dados = controlador_usuario.obter_usuario_por_id(
                st.session_state["id_usuario"])
            if usuario_dados:
                st.session_state["usuario_dados"] = {
                    "id_usuario": usuario_dados.id_usuario,
                    "nome": usuario_dados.nome,
                    "email": usuario_dados.email,
                    "telefone": usuario_dados.telefone
                }
        except Exception as e:
            st.error(f"❌ Erro ao carregar dados do usuário: {str(e)}")

# Tela de Edição de Perfil


def editar_perfil():
    st.subheader("👤 Editar Informações do Perfil")

    # Carrega dados do usuário se necessário
    carregar_dados_usuario()

    usuario_logado = st.session_state.get("usuario_dados")

    if not usuario_logado:
        st.warning(
            "⚠️ Não foi possível carregar suas informações. Faça login novamente.")
        if st.button("🔄 Tentar Novamente"):
            carregar_dados_usuario()
            st.rerun()
        return

    with st.form("form_editar_perfil_adm_predio"):
        st.write("**Informações Pessoais**")
        nome = st.text_input(
            "Nome Completo*", value=usuario_logado.get("nome", ""))
        email = st.text_input("Email*", value=usuario_logado.get("email", ""))
        telefone = st.text_input(
            "Telefone", value=usuario_logado.get("telefone", ""))

        st.markdown("---")
        st.write("**Alterar Senha**")
        senha_atual = st.text_input("Senha Atual*", type="password",
                                    help="Digite sua senha atual para confirmar as alterações")
        nova_senha = st.text_input("Nova Senha (opcional)", type="password",
                                   help="Deixe em branco se não quiser alterar a senha")
        confirmar_senha = st.text_input("Confirmar Nova Senha", type="password",
                                        help="Repita a nova senha")

        col1, col2 = st.columns([1, 1])
        with col1:
            salvar = st.form_submit_button(
                "💾 Salvar Alterações", use_container_width=True)
        with col2:
            cancelar = st.form_submit_button(
                "❌ Cancelar", use_container_width=True)

        if salvar:
            # Validações
            if not nome or not email:
                st.error("❌ Nome e email são obrigatórios.")
                return

            if not senha_atual:
                st.error(
                    "❌ A senha atual é obrigatória para confirmar as alterações.")
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
                    # Atualiza os dados na session_state
                    st.session_state["usuario_dados"]["nome"] = nome
                    st.session_state["usuario_dados"]["email"] = email
                    st.session_state["usuario_dados"]["telefone"] = telefone
                    # Atualiza também o nome de exibição
                    st.session_state["usuario"] = nome
                    st.rerun()
                else:
                    st.error(
                        "❌ Falha ao atualizar perfil. Verifique os dados e tente novamente.")

            except Exception as e:
                st.error(f"❌ Erro: {str(e)}")

        if cancelar:
            st.info("ℹ️ Alterações canceladas.")
            st.rerun()

    st.markdown("---")
    if st.button("⬅️ Voltar ao Menu Principal"):
        st.session_state.subpagina_adm_predio = None
        st.rerun()

# Tela inicial do Administrador do Prédio:


def tela_adm_predio():
    col_titulo, col_notificacao = st.columns([8, 1])

    with col_titulo:
        # Se você tem um título para a página principal:
        st.title("👨‍💼 Área do Administrador do Prédio")

    with col_notificacao:
        st.write("") # Espaçamento para alinhar com o título
        st.write("") # Espaçamento para alinhar com o título
        # Botão que muda o st.session_state["pagina"] para rotear para a tela de notificações
        if st.button("🔔", key="btn_notificacao_adm_predio", use_container_width=True):
            st.session_state["pagina"] = "notificacao_adm_predio" # Usaremos esta chave no app.py
            st.rerun()



    # Carrega dados do usuário ao entrar na tela
    carregar_dados_usuario()

    st.sidebar.title("Menu")
    # Mostrar nome do usuário logado
    if "usuario" in st.session_state:
        st.sidebar.write(f"👤 Usuário: {st.session_state['usuario']}")

    # 🔥 NOVO: Buscar e mostrar nome da lavanderia
    id_lavanderia = st.session_state.get("id_lavanderia")
    nome_lavanderia = "Sua Lavanderia"
    if id_lavanderia:
        from controladores.controlador_plataforma import ControladorPlataforma
        controlador_plataforma = ControladorPlataforma()
        lavanderia_info = controlador_plataforma.obter_lavanderia_por_id(
            id_lavanderia)
        if lavanderia_info:
            nome_lavanderia = lavanderia_info.get("nome", "Sua Lavanderia")

    st.sidebar.write(f"🏢 Lavanderia: {nome_lavanderia}")

    # Botão de logout
    if st.sidebar.button("🚪 Sair"):
        st.session_state.clear()
        st.rerun()

    # 🔥 MODIFICADO: Mostrar nome da lavanderia no cabeçalho
    st.subheader(f"Lavanderia: **{nome_lavanderia}**")
    st.markdown("---")

    # ----------------------------------------------------
    # VERIFICAÇÃO PRINCIPAL DA SUBPÁGINA - DEVE VIR ANTES DOS BOTÕES
    if st.session_state.get("subpagina_adm_predio") == "aprovar_moradores":
        aprovar_moradores()
        return
    elif st.session_state.get("subpagina_adm_predio") == "gerenciar_maquinas":
        gerenciar_maquinas()
        return
    elif st.session_state.get("subpagina_adm_predio") == "gerenciar_manutencoes":
        gerenciar_manutencoes()
        return
    elif st.session_state.get("subpagina_adm_predio") == "abrir_relatorios":
        abrir_relatorios()
        return
    elif st.session_state.get("subpagina_adm_predio") == "visualizar_ocorrencias":
        visualizar_ocorrencias()
        return
    elif st.session_state.get("subpagina_adm_predio") == "editar_perfil":
        editar_perfil()
        return

    # --- NOVAS ABAS PRINCIPAIS ---
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "👥 Aprovar Moradores", "⚙️ Gerenciar Máquinas", "🔧 Manutenções",
        "📊 Relatórios", "⚠️ Ocorrências", "👤 Meu Perfil"
    ])

    with tab1:
        st.subheader("👥 Aprovar Moradores")
        st.write("Aprove ou rejeite cadastros de novos moradores na sua lavanderia.")

        # Estatística rápida
        try:
            id_lavanderia = st.session_state.get("id_lavanderia")
            if id_lavanderia:
                moradores_pendentes = controlador_usuario.listar_moradores_pendentes(
                    id_lavanderia)
                st.info(
                    f"**📊 Estatística:** {len(moradores_pendentes)} morador(es) aguardando aprovação")
        except:
            pass

        if st.button("Abrir Aprovações", use_container_width=True, key="btn_aprovar"):
            st.session_state["subpagina_adm_predio"] = "aprovar_moradores"
            st.rerun()

    with tab2:
        st.subheader("⚙️ Gerenciar Máquinas")
        st.write("Cadastre, edite ou remova máquinas da sua lavanderia.")
        if st.button("Abrir Gerenciamento", use_container_width=True, key="btn_maquinas"):
            st.session_state["subpagina_adm_predio"] = "gerenciar_maquinas"
            st.rerun()

    with tab3:
        st.subheader("🔧 Gerenciar Manutenções")
        st.write("Agende manutenções preventivas e registre manutenções realizadas.")

        # Estatística rápida de pendências
        try:
            from controladores.controlador_manutencao import ControladorManutencao
            controlador_manutencao = ControladorManutencao()
            id_lavanderia = st.session_state.get("id_lavanderia")
            if id_lavanderia:
                pendentes = controlador_manutencao.listar_manutencoes_pendentes(
                    id_lavanderia)
                st.info(
                    f"**📊 Estatística:** {len(pendentes)} manutenção(ões) pendente(s)")
        except:
            pass

        if st.button("Abrir Gerenciamento", use_container_width=True, key="btn_manutencoes"):
            st.session_state["subpagina_adm_predio"] = "gerenciar_manutencoes"
            st.rerun()

    with tab4:
        st.subheader("📊 Relatórios")
        st.write("Acompanhe o uso e desempenho da sua lavanderia.")
        if st.button("Abrir Relatórios", use_container_width=True, key="btn_relatorios"):
            st.session_state["subpagina_adm_predio"] = "abrir_relatorios"
            st.rerun()

    with tab5:
        st.subheader("⚠️ Ocorrências")
        st.write("Revise e gerencie os problemas reportados pelos moradores.")
        if st.button("Revisar Ocorrências", use_container_width=True, key="btn_ocorrencias"):
            st.session_state["subpagina_adm_predio"] = "visualizar_ocorrencias"
            st.rerun()

    with tab6:
        st.subheader("👤 Meu Perfil")
        st.write("Gerencie suas informações pessoais e senha.")

        # Mostra informações atuais do usuário
        usuario_dados = st.session_state.get("usuario_dados")
        if usuario_dados:
            st.info("**Suas informações atuais:**")
            col1, col2 = st.columns(2)
            with col1:
                st.write(
                    f"**Nome:** {usuario_dados.get('nome', 'Não informado')}")
                st.write(
                    f"**Email:** {usuario_dados.get('email', 'Não informado')}")
            with col2:
                st.write(
                    f"**Telefone:** {usuario_dados.get('telefone', 'Não informado')}")

        if st.button("✏️ Editar Perfil", use_container_width=True, key="btn_perfil"):
            st.session_state["subpagina_adm_predio"] = "editar_perfil"
            st.rerun()
