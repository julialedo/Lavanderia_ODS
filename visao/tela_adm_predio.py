# View - tela_adm_predio.py
# Interface em Streamlit, recebe o input do usuário, chama o controller, mostra o feedback.

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from controladores.controlador_maquina import ControladorMaquina
from controladores.controlador_reserva import ControladorReserva
from controladores.controlador_usuario import ControladorUsuario

# Inicialização dos controladores:
controlador_maquina = ControladorMaquina()
controlador_reserva = ControladorReserva()
controlador_usuario = ControladorUsuario()


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
                    new_id = controlador_maquina.cadastrar_maquina(
                        st.session_state["id_lavanderia"], codigo, tipo, capacidade, status
                    )
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
            tipo_novo = st.selectbox(
                "Tipo", ["lavadora", "secadora"], index=["lavadora", "secadora"].index(maquina.tipo_maquina)
            )
            capacidade_nova = st.text_input("Capacidade", maquina.capacidade)
            status_novo = st.selectbox(
                "Status", ["livre", "em_uso", "manutencao"],
                index=["livre", "em_uso", "manutencao"].index(maquina.status_maquina)
            )
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

    id_lavanderia = st.session_state.get("id_lavanderia")
    if not id_lavanderia:
        st.error("❌ ID da lavanderia não encontrado. Faça login novamente.")
        return

    with st.container():
        st.subheader("📅 Filtro de Período")
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            data_inicial = st.date_input("**Data inicial**")
        with col2:
            data_final = st.date_input("**Data final**")
        with col3:
            gerar_btn = st.button("🚀 **Gerar Relatório**", use_container_width=True, type="primary")

    if gerar_btn:
        try:
            if data_final < data_inicial:
                st.error("❌ A data final não pode ser anterior à data inicial.")
                return

            maquinas = controlador_maquina.listar_por_lavanderia(id_lavanderia)
            if not maquinas:
                st.info("ℹ️ Nenhuma máquina cadastrada nesta lavanderia.")
                return

            with st.spinner("🔍 Buscando dados..."):
                todas_reservas = controlador_reserva.listar_reservas_periodo(
                    id_lavanderia, data_inicial.strftime("%Y-%m-%d"), data_final.strftime("%Y-%m-%d")
                )

            if not todas_reservas:
                st.info("📭 Nenhuma reserva encontrada nesse período.")
            else:
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
                st.markdown("---")
                st.subheader("📈 Visão Geral")

                col1, col2, col3 = st.columns(3)
                col1.metric("Total de Reservas", len(df))
                col2.metric("Máquinas Utilizadas", df["Máquina"].nunique())
                col3.metric("Usuários Únicos", df["Usuário"].nunique())

                st.markdown("---")
                st.subheader("📊 Reservas por Máquina")
                reservas_por_maquina = df["Máquina"].value_counts()
                fig, ax = plt.subplots()
                reservas_por_maquina.plot(kind="bar", ax=ax)
                st.pyplot(fig)

        except Exception as e:
            st.error(f"❌ Erro ao gerar relatório: {str(e)}")

    st.markdown("---")
    if st.button("⬅️ Voltar para o Menu Principal"):
        st.session_state.subpagina_adm_predio = None
        st.rerun()


# Tela inicial do Administrador do Prédio:
def tela_adm_predio():

    st.title("👨‍💼 Área do Administrador do Prédio")
    st.markdown("---")

    st.sidebar.title("Menu")
    if "usuario" in st.session_state:
        st.sidebar.write(f"👤 Usuário: {st.session_state['usuario']}")
    if st.sidebar.button("🚪 Sair"):
        st.session_state.clear()
        st.rerun()

    codigo_lavanderia = st.session_state.get("codigo_lavanderia", "Não Definido")
    st.subheader(f"Lavanderia: **{codigo_lavanderia}**")
    st.markdown("---")

    if st.session_state.get("subpagina_adm_predio") == "gerenciar_maquinas":
        gerenciar_maquinas()
        return
    elif st.session_state.get("subpagina_adm_predio") == "abrir_relatorios":
        abrir_relatorios()
        return

    # --- NOVAS ABAS PRINCIPAIS ---
    tab1, tab2, tab3 = st.tabs(["⚙️ Gerenciar Máquinas", "📊 Relatórios", "👤 Meu Perfil"])

    with tab1:
        st.subheader("⚙️ Gerenciar Máquinas")
        if st.button("Abrir Gerenciamento", use_container_width=True, key="btn_maquinas"):
            st.session_state["subpagina_adm_predio"] = "gerenciar_maquinas"
            st.rerun()

    with tab2:
        st.subheader("📊 Relatórios")
        if st.button("Abrir Relatórios", use_container_width=True, key="btn_relatorios"):
            st.session_state["subpagina_adm_predio"] = "abrir_relatorios"
            st.rerun()

    with tab3:
        st.subheader("👤 Editar Informações do Perfil")

        usuario_logado = st.session_state.get("usuario_dados")
        if not usuario_logado:
            st.warning("⚠️ Não foi possível carregar suas informações. Faça login novamente.")
        else:
            with st.form("form_editar_perfil_adm_predio"):
                nome = st.text_input("Nome", value=usuario_logado["nome"])
                email = st.text_input("Email", value=usuario_logado["email"])
                telefone = st.text_input("Telefone", value=usuario_logado["telefone"])
                senha_atual = st.text_input("Senha Atual*", type="password")
                nova_senha = st.text_input("Nova Senha (opcional)", type="password")

                salvar = st.form_submit_button("💾 Salvar Alterações")

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


# Execução Principal
tela_adm_predio()
