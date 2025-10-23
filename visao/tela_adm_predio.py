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


    if "subpagina_adm_predio" not in st.session_state:
        st.session_state["subpagina_adm_predio"] = None

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("⚙️ Gerenciar Maquinas") # Subheader ajustado para ícone
        if st.button("Gerenciar Máquinas", use_container_width=True):
            #st.session_state["subpagina_adm_predio"] = "gerenciar_maquinas"
            gerenciar_maquinas()
            #st.rerun()

    with col2:
        st.subheader("📊 Relatórios")
        if st.button("Abrir Relatórios", use_container_width=True):
            st.session_state["subpagina_adm_predio"] = "abrir_relatorios"
            st.rerun()

    st.markdown("---")

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
        st.session_state.pagina = "tela_adm_predio"
        st.session_state["subpagina_adm_predio"] = None
        st.rerun()


# Tela de Relatórios:
def abrir_relatorios():

    st.title("📊 Relatórios de Uso da Lavanderia")
    st.markdown("---")

    # Obtém o ID da lavanderia do usuário logado
    id_lavanderia = st.session_state.get("id_lavanderia")

    st.subheader("📅 Filtro de Período")
    col1, col2 = st.columns(2)

    with col1:
        data_inicial = st.date_input("Data inicial")
    with col2:
        data_final = st.date_input("Data final")

    if st.button("🔍 Gerar Relatório", use_container_width=True):
        try:
            # Busca dados de reservas no período
            reservas = controlador_reserva.listar_reservas_periodo(
                id_lavanderia,
                data_inicial.strftime("%Y-%m-%d"),
                data_final.strftime("%Y-%m-%d")
            )

            if not reservas:
                st.info("Nenhuma reserva encontrada nesse período.")
            else:
                # Cria DataFrame com os dados para análise
                df = pd.DataFrame([{
                "Máquina": r.maquina_id,
                "Data": r.data,
                "Hora Início": r.hora_inicio,
                "Hora Fim": r.hora_fim,
                "Usuário": r.usuario_id,
                "Status": r.status
                } for r in reservas])

                st.dataframe(df, use_container_width=True)

                st.markdown("### 📈 Estatísticas gerais")
                total_reservas = len(df)
                maquinas_ativas = df["Máquina"].nunique()
                usuarios = df["Usuário"].nunique()

                st.metric("Total de reservas", total_reservas)
                st.metric("Máquinas utilizadas", maquinas_ativas)
                st.metric("Usuários diferentes", usuarios)

                st.markdown("### ⚙️ Reservas por máquina")
                reservas_por_maquina = df["Máquina"].value_counts()
                fig, ax = plt.subplots()
                reservas_por_maquina.plot(kind="bar", ax=ax)
                ax.set_xlabel("Máquina")
                ax.set_ylabel("Número de Reservas")
                ax.set_title("Reservas por Máquina")
                st.pyplot(fig)

                st.markdown("### ⏰ Taxa de utilização (%)")
                total_horas = (len(pd.date_range(data_inicial, data_final)) * 12 * maquinas_ativas)
                horas_reservadas = len(df)
                taxa_utilizacao = (horas_reservadas / total_horas) * 100
                st.progress(int(taxa_utilizacao))
                st.write(f"Taxa de utilização aproximada: **{taxa_utilizacao:.1f}%**")

        except Exception as e:
            st.error(f"Erro ao gerar relatório: {str(e)}")

    st.markdown("---")
    if st.button("⬅️ Voltar"):
        st.session_state.pagina = "inicial"
        st.rerun()


# Execução Principal
if "subpagina_adm_predio" not in st.session_state:
    st.session_state["subpagina_adm_predio"] = None

if st.session_state["subpagina_adm_predio"] == "gerenciar_maquinas":
    gerenciar_maquinas()
elif st.session_state["subpagina_adm_predio"] == "abrir_relatorios":
    abrir_relatorios()
