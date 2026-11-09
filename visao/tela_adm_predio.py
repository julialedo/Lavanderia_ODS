# View - tela_adm_predio.py
# Interface em Streamlit, recebe o input do usuário, chama o controller, mostra o feedback.

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Controladores inicializados e armazenador uma unica vez com cache:
@st.cache_resource
def get_controladores_adm_predio():
    try:
        from controladores.controlador_maquina import ControladorMaquina
        from controladores.controlador_reserva import ControladorReserva
        from controladores.controlador_usuario import ControladorUsuario
        from controladores.controlador_ocorrencia import ControladorOcorrencia
        from controladores.controlador_manutencao import ControladorManutencao
        from controladores.controlador_plataforma import ControladorPlataforma

        return {
            "maquina": ControladorMaquina(),
            "reserva": ControladorReserva(),
            "usuario": ControladorUsuario(),
            "ocorrencia": ControladorOcorrencia(),
            "manutencao": ControladorManutencao(),
            "plataforma": ControladorPlataforma()
        }
    except ImportError as e:
        st.error(f"Erro ao carregar controladores. Detalhes: {e}")
        return None

CONTROLADORES = get_controladores_adm_predio()
if CONTROLADORES:
    controlador_maquina = CONTROLADORES["maquina"]
    controlador_reserva = CONTROLADORES["reserva"]
    controlador_usuario = CONTROLADORES["usuario"]
    controlador_ocorrencia = CONTROLADORES["ocorrencia"]
    controlador_manutencao = CONTROLADORES["manutencao"]
    controlador_plataforma = CONTROLADORES["plataforma"]
else:
    controlador_maquina = None
    controlador_reserva = None
    controlador_usuario = None
    controlador_ocorrencia = None
    controlador_manutencao = None
    controlador_plataforma = None


if "id_lavanderia_ativa" not in st.session_state and st.session_state.get("lista_ids_lavanderia"):
    st.session_state["id_lavanderia_ativa"] = st.session_state["lista_ids_lavanderia"][0]  
    #para armazenar a lavanderia que ele esta, abre a tela com a primeira


# Pega os dados de todas as lavanderias associadas aquele adm, e utiliza cache
def get_all_lavanderias_info(lista_ids_lavanderia):
    if not lista_ids_lavanderia:
        return {}
    
    cache_key = "all_lavanderias_info"
    if cache_key not in st.session_state:
        lavanderias_info = {}
        try:
            for id_lav in lista_ids_lavanderia:
                info = controlador_plataforma.obter_lavanderia_por_id(id_lav)
                if info:
                    lavanderias_info[info['nome']] = id_lav # Mapeia Nome -> ID
            st.session_state[cache_key] = lavanderias_info
        except Exception as e:
            print(f"Erro ao carregar lista de lavanderias. Detalhes: {e}")   
            st.session_state[cache_key] = {}   # Em caso de erro, retorna dicionário vazio

    return st.session_state[cache_key]


# Função para carregar dados do usuário
def carregar_dados_usuario():
    if "usuario_dados" not in st.session_state and "id_usuario" in st.session_state:
        try:
            usuario_dados = controlador_usuario.obter_usuario_por_id(st.session_state["id_usuario"])
            if usuario_dados:
                st.session_state["usuario_dados"] = {
                    "id_usuario": usuario_dados.id_usuario,
                    "nome": usuario_dados.nome,
                    "email": usuario_dados.email,
                    "telefone": usuario_dados.telefone
                }
        except Exception as e:
            st.error(f"Erro ao carregar dados do usuário: {str(e)}")


# Carregar as maquinas com cache e limpar cache
def get_maquinas_lavanderia(id_lavanderia):
    if not id_lavanderia:
        return []
        
    cache_key = f"maquinas_{id_lavanderia}"
    if cache_key not in st.session_state:
        try:
            maquinas = controlador_maquina.listar_por_lavanderia(id_lavanderia) if controlador_maquina else []
            st.session_state[cache_key] = maquinas
        except Exception as e:
            print(f"Erro ao carregar máquinas. Detalhes: {e}")
            st.session_state[cache_key] = []
    return st.session_state[cache_key]

def clear_maquinas_cache(id_lavanderia):
    if id_lavanderia:
        cache_key = f"maquinas_{id_lavanderia}"
        if cache_key in st.session_state:
            del st.session_state[cache_key]


# Listar moradores pendentes de aprovação com cache e limpar cache
def get_moradores_pendentes_cache(id_lavanderia):
    if not id_lavanderia:
        return []
        
    cache_key = f"moradores_pendentes_{id_lavanderia}"
    if cache_key not in st.session_state:
        try:
            moradores = controlador_usuario.listar_moradores_pendentes(id_lavanderia) if controlador_usuario else []
            st.session_state[cache_key] = moradores
        except Exception as e:
            st.error(f"Erro ao buscar moradores pendentes. Detalhes:{e}")
            st.session_state[cache_key] = []
    return st.session_state[cache_key]

def clear_moradores_cache(id_lavanderia):
    if id_lavanderia:
        cache_key = f"moradores_pendentes_{id_lavanderia}"
        if cache_key in st.session_state:
            del st.session_state[cache_key]


# Listar ocorrências com cache e limpar cache
def get_ocorrencias_cache(id_lavanderia):
    if not id_lavanderia:
        return []
        
    cache_key = f"ocorrencias_{id_lavanderia}"
    if cache_key not in st.session_state:
        try:
            ocorrencias = controlador_ocorrencia.listar_ocorrencias_para_admin(id_lavanderia) if controlador_ocorrencia else []
            st.session_state[cache_key] = ocorrencias
        except:
            st.session_state[cache_key] = []
    return st.session_state[cache_key]

def clear_ocorrencias_cache(id_lavanderia):
    if id_lavanderia:
        cache_key = f"ocorrencias_{id_lavanderia}"
        if cache_key in st.session_state:
            del st.session_state[cache_key]


# Tela de Aprovação de Moradores
def aprovar_moradores():
    st.subheader("Aprovar Moradores Cadastrados")
    st.text("Aqui você pode aprovar ou rejeitar cadastros de novos moradores.")

    id_lavanderia_admin = st.session_state.get("id_lavanderia_ativa")
    if not id_lavanderia_admin:
        st.error("ID da lavanderia ativa não encontrado.")
        return

    # Buscar moradores pendentes com cache:
    try:
        moradores_pendentes = get_moradores_pendentes_cache(id_lavanderia_admin)
        if not moradores_pendentes:
            st.success("Não há moradores aguardando aprovação!")

            if st.button("Atualizar Lista", use_container_width=True, key="atualizar_lista_moradores"):
                clear_moradores_cache(id_lavanderia_admin)
                st.rerun()
        else:
            st.info(f"{len(moradores_pendentes)} morador(es) aguardando aprovação.")

            st.markdown("---")
            # Exibir em formato de cards
            for i, morador in enumerate(moradores_pendentes):
                with st.container():
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.subheader(f"{morador['nome']}")
                        st.write(f"**Email:** {morador['email']}")
                        st.write(f"**Telefone:** {morador['telefone']}")
                        st.write(f"**Data do Cadastro:** {morador['data_cadastro_usuario']}")

                    with col2:
                        st.subheader("Ações:")
                        if st.button("Aprovar", key=f"aprovar_{morador['id_usuario']}", use_container_width=True):
                            try:
                                if controlador_usuario.aprovar_morador(morador['id_usuario']):
                                    clear_moradores_cache(id_lavanderia_admin)
                                    st.rerun()
                            except Exception as e:
                                st.error(f"Erro: {str(e)}")

                        if st.button("Rejeitar", key=f"rejeitar_{morador['id_usuario']}", use_container_width=True):
                            try:
                                if controlador_usuario.rejeitar_morador(morador['id_usuario']):
                                    clear_moradores_cache(id_lavanderia_admin)
                                    st.rerun()
                            except Exception as e:
                                st.error(f"Erro: {str(e)}")

                    if i < len(moradores_pendentes) - 1:
                        st.markdown("---")
    except Exception as e:
        st.error(f"Erro ao carregar moradores pendentes: {str(e)}")

    st.markdown("---")
    if st.button("Voltar ao Menu Principal", use_container_width=True):
        st.session_state.subpagina_adm_predio = None
        st.rerun()


# Tela de Gerenciamento de Máquinas
def gerenciar_maquinas():
    st.subheader("Gerenciamento de Máquinas")
    st.text("Aqui você pode adicionar, editar ou remover maquinas em sua lavanderia.")

    # Verifica se está editando uma máquina específica
    if "editar_maquina" in st.session_state:
        editar_maquina_screen()
        return

    id_lavanderia = st.session_state.get("id_lavanderia_ativa")
    if not id_lavanderia:
        st.error("ID da lavanderia não encontrado.")
        return

    try:
        maquinas = get_maquinas_lavanderia(id_lavanderia)
        if not maquinas:
            st.info("Nenhuma máquina cadastrada para esta Lavanderia!")
        else:
            # Estatísticas rápidas:
            total_maquinas = len(maquinas)
            maquinas_operantes = len([m for m in maquinas if m.status_maquina != "manutencao"])
            maquinas_manutencao = len([m for m in maquinas if m.status_maquina == "manutencao"])
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("**Total de Maquinas**", total_maquinas)
            with col2:
                st.metric("**Operantes**", maquinas_operantes)
            with col3:
                st.metric("**Em Manutenção**", maquinas_manutencao)

            # Cadastrar Máquinas - Formulário
            with st.expander("Cadastrar Nova Máquina", expanded=False):
                with st.form("nova_maquina", clear_on_submit=True):
                    codigo = st.text_input("Código da Máquina (ex: LAV-01, SEC-07)")
                    tipo = st.selectbox("Tipo da Máquina", ["lavadora", "secadora"])
                    capacidade = st.text_input("Capacidade (ex: 8kg)")
                    status = st.selectbox("Status Inicial", ["livre", "em_uso", "manutencao"])
                    
                    if st.form_submit_button("Cadastrar Máquina"):
                        if not codigo:
                            st.error("O código da máquina é obrigatório!")
                        elif not capacidade:
                            st.error("A capacidade da máquina é obrigatória!")
                        else:
                            try:
                                new_id = controlador_maquina.cadastrar_maquina(
                                    id_lavanderia, codigo, tipo, capacidade, status
                                )
                                st.success(f"Máquina cadastrada com sucesso! ID: {new_id}")
                                clear_maquinas_cache(id_lavanderia)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao cadastrar máquina: {str(e)}")

            # Listar as Máquinas Cadastradas:
            st.markdown("---")
            st.subheader("Máquinas cadastradas:")
            for maq in maquinas:
                status_color = "" if maq.status_maquina == "livre" else "" if maq.status_maquina == "em_uso" else ""
                
                with st.expander(f"{status_color} {maq.codigo_maquina} - {maq.tipo_maquina.capitalize()} ({maq.capacidade})"):
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.write(f"**Status:** {maq.status_maquina}")
                        st.write(f"**Tipo:** {maq.tipo_maquina}")
                        st.write(f"**Capacidade:** {maq.capacidade}")

                    with col2:
                        if st.button("Editar", key=f"edit_{maq.id_maquina}", use_container_width=True):
                            st.session_state["editar_maquina"] = maq.id_maquina
                            st.rerun()

                        if st.button("Excluir", key=f"del_{maq.id_maquina}", use_container_width=True):
                            try:
                                ok = controlador_maquina.remover_maquina(maq.id_maquina)
                                if ok:
                                    st.success("Máquina removida com sucesso!")
                                    clear_maquinas_cache(id_lavanderia)
                                    st.rerun()
                                else:
                                    st.error("Erro ao remover máquina.")
                            except Exception as e:
                                st.error(f"Erro: {str(e)}")
    except Exception as e:
        st.error(f"Erro ao carregar máquinas: {str(e)}")

    st.markdown("---")
    if st.button("Voltar ao Menu Principal", use_container_width=True):
        st.session_state.subpagina_adm_predio = None
        st.rerun()


# Tela de Edição de Máquina
def editar_maquina_screen():
    st.subheader("Editar Máquina:")

    maq_id = st.session_state["editar_maquina"]
    try:
        maquina = controlador_maquina.obter(maq_id) if controlador_maquina else None

        if not maquina:
            st.error("Máquina não encontrada!")
            if st.button("Voltar"):
                del st.session_state["editar_maquina"]
                st.rerun()
            return

        with st.form("form_editar_maquina"):
            st.write("**Informações da Máquina:**")
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
                    index=["livre", "em_uso", "manutencao"].index(maquina.status_maquina)
                )
            st.caption("*Campos obrigatórios")

            col_btn1, col_btn2 = st.columns([1, 1])
            with col_btn1:
                salvar = st.form_submit_button("Salvar Alterações", use_container_width=True)
            with col_btn2:
                cancelar = st.form_submit_button("Cancelar", use_container_width=True)

            if salvar:
                if not codigo_novo:
                    st.error("O código da máquina é obrigatório!")
                    return

                if not capacidade_nova:
                    st.error("A capacidade da máquina é obrigatória!")
                    return

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
                        clear_maquinas_cache(st.session_state.get("id_lavanderia_ativa"))
                        del st.session_state["editar_maquina"]
                        st.rerun()
                    else:
                        st.warning("Nenhuma alteração detectada ou máquina não encontrada.")
                except Exception as e:
                    st.error(f"Erro ao atualizar máquina: {str(e)}")

            if cancelar:
                del st.session_state["editar_maquina"]
                st.rerun()

    except Exception as e:
        st.error(f"Erro ao carregar dados da máquina: {str(e)}")
   

# Tela de Gerenciamento de Manutenções
def gerenciar_manutencoes():
    st.subheader("Gerenciamento de Manutenções")
    st.text("Aqui você pode realatar ou agendar manutenções preventivas e corretivas em suas máquinas.")

    id_lavanderia = st.session_state.get("id_lavanderia_ativa")
    if not id_lavanderia:
        st.error("ID da lavanderia não encontrado.")
        return
    if not controlador_manutencao:
        st.error("Sistema de manutenção indisponível.")
        return

    # Obter nome do admin logado
    nome_adm = st.session_state.get("usuario", "Administrador")

    # Abas para diferentes funcionalidades
    tab1, tab2, tab3 = st.tabs(["Agendar Manutenção Preventiva", "Registrar Manutenção Realizada", "Histórico de Manutenções"])
    with tab1:
        st.subheader("Agendar Manutenção Preventiva:")
        maquinas = get_maquinas_lavanderia(id_lavanderia)

        if not maquinas:
            st.info("Nenhuma máquina cadastrada para agendar manutenção.")
        else:
            with st.form("form_agendar_manutencao", clear_on_submit=True):
                opcoes_maquinas = {
                    f"{maq.codigo_maquina} - {maq.tipo_maquina}": maq.id_maquina for maq in maquinas
                }
                maquina_selecionada = st.selectbox("Máquina*", list(opcoes_maquinas.keys()), index=None, placeholder="Selecione uma maquina...")

                col1, col2 = st.columns(2)
                with col1:
                    data_agendada = st.date_input("Data de Agendamento*", value=None, min_value=datetime.now().date())
                with col2:
                    hora_agendada = st.time_input("Hora de Agendamento*", value=None)

                descricao = st.text_area("Descrição*",
                                       placeholder="Descreva os serviços de manutenção preventiva a serem realizados...",
                                       height=100)

                if st.form_submit_button("Agendar Manutenção", use_container_width=True):
                    try:
                        id_maquina = opcoes_maquinas[maquina_selecionada]
                        manutencao_id = controlador_manutencao.agendar_manutencao_preventiva(
                            id_maquina=id_maquina,
                            data_agendada=data_agendada.strftime("%Y-%m-%d"),
                            hora_agendada=hora_agendada.strftime("%H:%M:%S"),
                            descricao=descricao,
                            nome_adm=nome_adm
                        )
                        st.success(f"Manutenção preventiva agendada com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao agendar manutenção: {str(e)}")

    with tab2:
        st.subheader("Registrar Manutenção Realizada")
        maquinas = get_maquinas_lavanderia(id_lavanderia)

        if not maquinas:
            st.info("Nenhuma máquina cadastrada.")
        else:
            with st.form("form_registrar_manutencao", clear_on_submit=True):
                opcoes_maquinas = {
                    f"{maq.codigo_maquina} - {maq.tipo_maquina}": maq.id_maquina for maq in maquinas
                }
                maquina_selecionada = st.selectbox("Máquina*", list(opcoes_maquinas.keys()), key="corretiva", index=None, placeholder="Selecione uma maquina...")

                col1, col2 = st.columns(2)
                with col1:
                    data_realizada = st.date_input("Data de Realização*", value=None, key="data_realizada")
                with col2:
                    hora_realizada = st.time_input("Hora Realizada*", value=None)

                descricao = st.text_area("Descrição do Reparo/Manutenção*",
                                       placeholder="Descreva o problema encontrado e o reparo realizado...",
                                       height=100)

                if st.form_submit_button("Registrar Manutenção", use_container_width=True):
                    try:
                        id_maquina = opcoes_maquinas[maquina_selecionada]
                        manutencao_id = controlador_manutencao.registrar_manutencao_realizada(
                            id_maquina=id_maquina,
                            data_realizada=data_realizada.strftime("%Y-%m-%d"),
                            hora_realizada=hora_realizada.strftime("%H:%M:%S"),
                            descricao=descricao,
                            nome_adm=nome_adm
                        )
                        st.success(f"Manutenção registrada com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao registrar manutenção: {str(e)}")

    with tab3:
        # Mostrar manutenções pendentes primeiro
        st.markdown("#### Manutenções:")
        try:
            todas_manutencoes = controlador_manutencao.listar_manutencoes(id_lavanderia)
            if not todas_manutencoes:
                st.info("Nenhuma manutenção registrada.")
            else:
                # Filtros
                filtro_tipo = st.selectbox("Filtrar por Status:", ["Pendentes", "Realizadas", "Todas"])
                # Aplicar filtros
                if filtro_tipo == "Todas":
                    manutencoes_filtradas = todas_manutencoes
                    st.info(f"Mostrando {len(manutencoes_filtradas)} manutenção(ões)")
                elif filtro_tipo == "Realizadas":
                    manutencoes_filtradas = [m for m in todas_manutencoes if m.data_realizada is not None]
                    st.info(f"Mostrando {len(manutencoes_filtradas)} manutenção(ões)")
                else:
                    manutencoes_filtradas = [m for m in todas_manutencoes if m.data_realizada is None]
                    if not manutencoes_filtradas:
                        st.success("Nenhuma manutenção pendente!")
                    else:
                        st.warning(f"Você tem {len(manutencoes_filtradas)} manutenção(ões) pendente(s)")
                
                for manutencao in manutencoes_filtradas:
                    if manutencao.data_realizada:
                        icone = ""
                        status = "Realizada"
                    else:
                        icone = ""
                        status = "Pendente "

                    with st.expander(f"{icone} Manutenção {manutencao.id_manutencao} - {status}"):
                        col1, col2 = st.columns(2)

                        maquinas = get_maquinas_lavanderia(st.session_state.get("id_lavanderia_ativa"))
                        maquina = next((m for m in maquinas if m.id_maquina == manutencao.id_maquina), None)
                        with col1:
                            st.write(f"**Máquina:** {maquina.codigo_maquina}")
                            st.write(f"**Data Agendada:** {manutencao.data_agendada}")
                            st.write(f"**Agendado por:** {manutencao.nome_adm}")

                        if f"editando_{manutencao.id_manutencao}" not in st.session_state:
                            st.session_state[f"editando_{manutencao.id_manutencao}"] = False

                        with col2:
                            if manutencao.data_realizada:
                                st.write(f"**Data Realizada:** {manutencao.data_realizada}")
                                st.success("Concluída")
                            else:
                                st.warning("Pendente")
                                if st.button("Marcar como Realizada", key=f"realizar_hist_{manutencao.id_manutencao}"):
                                    st.session_state[f"editando_{manutencao.id_manutencao}"] = True

                        st.write(f"**Descrição:** {manutencao.descricao}")
                        
                        if st.session_state[f"editando_{manutencao.id_manutencao}"]:
                            try:
                                st.markdown("---")
                                st.markdown("##### Confirmar Dados para Marcar Manutenção como Realizada:")
                                with st.form(f"form_editar_{manutencao.id_manutencao}", clear_on_submit=False):

                                    # Data realizada padrão = hoje
                                    data_realizada = st.date_input(
                                        "Data de Realização",
                                        value=datetime.now().date()
                                    )
                                    # Hora realizada padrão = agora
                                    hora_realizada = st.time_input(
                                        "Hora de Realização",
                                        value=datetime.now().time()
                                    )
                                    descricao_editada = st.text_area(
                                        "Descrição da manutenção realizada",
                                        value=manutencao.descricao,
                                        height=120
                                    )
                                    confirmar = st.form_submit_button("Confirmar Manutenção Realizada.", use_container_width=True)

                                    if confirmar:
                                        controlador_manutencao.atualizar_manutencao(
                                            id_manutencao=manutencao.id_manutencao,
                                            id_maquina=manutencao.id_maquina,
                                            data_realizada=data_realizada.strftime("%Y-%m-%d"),
                                            hora_realizada=hora_realizada.strftime("%H:%M:%S"),
                                            descricao=descricao_editada,
                                            nome_adm=nome_adm,
                                            )
                                        st.success("Manutenção registrada como realizada!")
                                        del st.session_state[f"editando_{manutencao.id_manutencao}"]
                                        st.rerun()
                            except Exception as e:
                                st.error("Erro ao marcar como realizada.")
        except Exception as e:
            st.error(f"Erro ao carregar histórico: {str(e)}")

    st.markdown("---")
    if st.button("Voltar ao Menu Principal", use_container_width=True):
        st.session_state.subpagina_adm_predio = None
        st.rerun()


# Tela de Relatórios: CONFERIR
def abrir_relatorios():
    st.subheader("Relatórios de Uso da Lavanderia:")
    st.text("Aqui você pode visualizar relatórios e insight sobre o uso da sua lavanderia.")

    id_lavanderia = st.session_state.get("id_lavanderia_ativa")
    if not id_lavanderia:
        st.error("ID da lavanderia não encontrado. Faça login novamente.")
        return

    with st.container():
        st.markdown("#### Filtro de Período:")
        col1, col2, col3 = st.columns([2, 2, 1])

        with col1:
            data_inicial = st.date_input("**Data inicial:**", help="Selecione a data de início do período")
        with col2:
            data_final = st.date_input("**Data final:**", help="Selecione a data final do período")
        with col3:
            st.write("")
            gerar_btn = st.button("**Gerar Relatório**", use_container_width=True)

    if gerar_btn:
        try:
            if data_final < data_inicial:
                st.error("A data final não pode ser anterior à data inicial.")
                return

            maquinas = get_maquinas_lavanderia(id_lavanderia)
            if not maquinas:
                st.info("Nenhuma máquina cadastrada nesta lavanderia.")
                return

            with st.spinner("Buscando dados..."):
                todas_reservas = controlador_reserva.listar_reservas_periodo(
                    id_lavanderia,
                    data_inicial.strftime("%Y-%m-%d"),
                    data_final.strftime("%Y-%m-%d")
                ) if controlador_reserva else []

            if not todas_reservas:
                st.info("Nenhuma reserva encontrada nesse período.")
            else:
                # Criar DataFrame
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

                # Estatísticas:
                st.markdown("---")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    total_reservas = len(df)
                    st.metric("Total de Reservas", total_reservas, delta=f"{total_reservas} agendamentos")
                with col2:
                    maquinas_ativas = df["Máquina"].nunique()
                    st.metric("Máquinas Utilizadas", maquinas_ativas, delta=f"de {len(maquinas)} disponíveis")
                with col3:
                    usuarios_unicos = df["Usuário"].nunique()
                    st.metric("Usuários Únicos", usuarios_unicos)
                with col4:
                    dias_periodo = (data_final - data_inicial).days + 1
                    horas_por_dia = 12
                    horas_totais_disponiveis = dias_periodo * horas_por_dia * len(maquinas)
                    horas_reservadas = len(df)
                    taxa_utilizacao = (horas_reservadas / horas_totais_disponiveis) * 100 if horas_totais_disponiveis > 0 else 0
                    st.metric("Taxa de Utilização", f"{taxa_utilizacao:.1f}%")

                # Gráficos
                st.markdown("---")
                st.subheader("Análise Visual")

                tab1, tab2 = st.tabs(["Dados Detalhados", "Gráficos"])

                with tab1:
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Exportar para CSV",
                        data=csv,
                        file_name=f"relatorio_lavanderia_{data_inicial}_{data_final}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )

                with tab2:
                    col1, col2 = st.columns(2)
                    with col1:
                        if not df.empty:
                            reservas_por_maquina = df["Máquina"].value_counts()
                            fig1, ax1 = plt.subplots(figsize=(8, 6))
                            cores = plt.cm.Set3(range(len(reservas_por_maquina)))
                            bars = reservas_por_maquina.plot(kind="bar", ax=ax1, color=cores)
                            ax1.set_xlabel("Máquina")
                            ax1.set_ylabel("Número de Reservas")
                            ax1.set_title("Reservas por Máquina", fontsize=14, fontweight='bold')
                            plt.xticks(rotation=45)
                            for i, v in enumerate(reservas_por_maquina):
                                ax1.text(i, v + 0.1, str(v), ha='center', va='bottom')
                            st.pyplot(fig1)
        except Exception as e:
            st.error(f"Erro ao gerar relatório: {str(e)}")

    # Botão de voltar
    st.markdown("---")
    if st.button("Voltar para o Menu Principal", use_container_width=True):
        st.session_state.subpagina_adm_predio = None
        st.rerun()


# Tela de Ocorrências: CONFERIR
def visualizar_ocorrencias():
    st.subheader("Gerenciamento de Ocorrências")
    st.text("Aqui você pode visualizar as ocorrências relatadas por usuarios da sua lavanderia.")
    
    id_lavanderia_admin = st.session_state.get("id_lavanderia_ativa")
    if not id_lavanderia_admin:
        st.error("ID da lavanderia do admin não encontrado na sessão.")
        st.markdown("---")
        if st.button("Voltar ao Menu Principal", use_container_width=True):
            st.session_state.subpagina_adm_predio = None
            st.rerun()
        return

    try:
        ocorrencias = get_ocorrencias_cache(id_lavanderia_admin)

        if not ocorrencias:
            st.success("Nenhuma ocorrência reportada. Tudo em ordem!")
        else:
            st.error(f"Você tem {len(ocorrencias)} ocorrência(s) para revisar")
            
            for oc in ocorrencias:
                col1, col2 = st.columns([4, 1])
                with col1:
                    with st.expander(f"Ocorrência {oc.id_problema} - Data: {oc.data_problema}"):
                        st.write(f"**Reportado por:** {oc.nome_usuario}")
                        st.write(f"**Máquina:** {oc.id_maquina if oc.id_maquina else 'N/A'}")
                        st.write(f"**Descrição:**")
                        st.warning(f"_{oc.descricao}_")

    except Exception as e:
        st.error(f"Erro ao carregar ocorrências: {e}")

    if st.button("Atualizar Ocorrências", use_container_width=True):
        clear_ocorrencias_cache(id_lavanderia_admin)
        st.rerun()
    
    st.markdown("---")
    if st.button("Voltar ao Menu Principal", use_container_width=True):
        st.session_state.subpagina_adm_predio = None
        st.rerun()


# Tela de Edição de Perfil:
def editar_perfil():
    st.subheader("Editar Informações do Perfil:")

    carregar_dados_usuario()
    usuario_logado = st.session_state.get("usuario_dados")

    if not usuario_logado:
        st.warning("Não foi possível carregar suas informações. Faça login novamente.")
        if st.button("Tentar Novamente"):
            carregar_dados_usuario()
            st.rerun()
        return

    with st.form("form_editar_perfil_adm_predio"):
        st.write("**Informações Pessoais**")
        nome = st.text_input("Nome Completo*", value=usuario_logado.get("nome", ""))
        email = st.text_input("Email*", value=usuario_logado.get("email", ""))
        telefone = st.text_input("Telefone", value=usuario_logado.get("telefone", ""))

        st.markdown("---")
        st.write("**Alterar Senha**")
        senha_atual = st.text_input("Senha Atual*", type="password",
                                  help="Digite sua senha atual para confirmar as alterações")
        nova_senha = st.text_input("Nova Senha (opcional)", type="password",
                                 help="Deixe em branco se não quiser alterar a senha")
        confirmar_senha = st.text_input("Confirmar Nova Senha", type="password",
                                      help="Repita a nova senha")

        st.text("*Campos obrigatórios.")
        col1, col2 = st.columns([1, 1])
        with col1:
            salvar = st.form_submit_button("Salvar Alterações", use_container_width=True)
        with col2:
            cancelar = st.form_submit_button("Cancelar", use_container_width=True)

        if salvar:
            if not nome or not email:
                st.error("Nome e email são obrigatórios.")
                return

            if not senha_atual:
                st.error("A senha atual é obrigatória para confirmar as alterações.")
                return

            if nova_senha and nova_senha != confirmar_senha:
                st.error("As senhas não coincidem.")
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
                    st.success("Perfil atualizado com sucesso!")
                    st.session_state["usuario_dados"]["nome"] = nome
                    st.session_state["usuario_dados"]["email"] = email
                    st.session_state["usuario_dados"]["telefone"] = telefone
                    st.session_state["usuario"] = nome
                    st.session_state.subpagina_adm_predio = None
                    st.rerun()
                else:
                    st.error("Falha ao atualizar perfil. Verifique os dados e tente novamente.")

            except Exception as e:
                st.error(f"Erro: {str(e)}")

        if cancelar:
            st.session_state.subpagina_adm_predio = None
            st.rerun()

    st.markdown("---")
    if st.button("Voltar ao Menu Principal", use_container_width=True):
        st.session_state.subpagina_adm_predio = None
        st.rerun()


# Tela inicial do Administrador do Prédio
def tela_adm_predio():

    # Verificação inicial dos controladores:
    if not all([controlador_maquina, controlador_reserva, controlador_usuario, controlador_ocorrencia, controlador_manutencao, controlador_plataforma]):
        st.error("Sistema temporariamente indisponível. Tente novamente.")
        if st.button("Recarregar"):
            st.rerun()
        return

    lista_ids = st.session_state.get("lista_ids_lavanderia", [])
    id_lavanderia_ativa = st.session_state.get("id_lavanderia_ativa")    
    # Obter nomes das lavanderias para o seletor:
    lavanderias_info = get_all_lavanderias_info(lista_ids)
    nomes_lavanderias = list(lavanderias_info.keys()) # Lista dos nomes

    # Carrega dados do usuário ao entrar na tela:
    carregar_dados_usuario()

    # SIDEBAR:
    with st.sidebar:
        if "usuario" in st.session_state:
            st.subheader(f"Bem-vindo(a) {st.session_state['usuario']}!")

        st.markdown("---")
        if len(nomes_lavanderias) > 0 and id_lavanderia_ativa:
            nome_lavanderia_ativa = next(
                (nome for nome, id_val in lavanderias_info.items() if id_val == id_lavanderia_ativa),
                None
            )
            try:
                index_selecionado = nomes_lavanderias.index(nome_lavanderia_ativa)
            except ValueError:
                index_selecionado = 0

            lavanderia_selecionada = st.selectbox( 
                "  Selecione uma Lavanderia:",
                options=nomes_lavanderias, 
                index=index_selecionado,
                key="seletor_lavanderia_adm_predio"
            )
            
            # Verifica e atualiza o ID ativo:
            novo_id_ativo = lavanderias_info.get(lavanderia_selecionada)
            
            # Se o ID do seletor mudou, atualiza a sessão e recarrega
            if novo_id_ativo != id_lavanderia_ativa and novo_id_ativo is not None:
                st.session_state["id_lavanderia_ativa"] = novo_id_ativo
                st.rerun() 
            
            id_lavanderia_ativa = novo_id_ativo # Atualiza o contexto local
            
        if not id_lavanderia_ativa:
            st.error("Administrador não associado a nenhuma lavanderia.")
        
        st.markdown("---")
        if st.button("Limpar Cache", use_container_width=True, help="Recarregar todos os dados em cache"):
            clear_moradores_cache(id_lavanderia_ativa)
            clear_maquinas_cache(id_lavanderia_ativa)
            clear_ocorrencias_cache(id_lavanderia_ativa)
            st.success("Cache limpo!")
            st.rerun()

        if st.button("Sair", use_container_width=True):
            st.session_state.clear()
            st.rerun()


    # VERIFICAÇÃO PRINCIPAL DA SUBPÁGINA:
    subpagina = st.session_state.get("subpagina_adm_predio")
    if subpagina == "aprovar_moradores":
        aprovar_moradores()
        return
    elif subpagina == "gerenciar_maquinas":
        gerenciar_maquinas()
        return
    elif subpagina == "gerenciar_manutencoes":
        gerenciar_manutencoes()
        return
    elif subpagina == "abrir_relatorios":
        abrir_relatorios()
        return
    elif subpagina == "visualizar_ocorrencias":
        visualizar_ocorrencias()
        return
    elif subpagina == "editar_perfil":
        editar_perfil()
        return

    
    # TELA PRINCIPAL:
    col_titulo, col_notificacao = st.columns([8, 1])
    with col_titulo:
        st.header(" Área do Administrador da Lavanderia")

    with col_notificacao:
        st.write("") # Espaçamento para alinhar com o título
        # Botão que muda o st.session_state["pagina"] para rotear para a tela de notificações
        if st.button("", key="btn_notificacao_adm_predio", use_container_width=True):
            st.session_state["pagina"] = "notificacao_adm_predio" # Usaremos esta chave no app.py
            st.rerun()
    
    
    # Abas Principais:
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Aprovar Moradores", "Gerenciar Máquinas", "Manutenções",
        "Relatórios", "Ocorrências", "Meu Perfil"
    ])

    with tab1:
        st.subheader("Aprovar Moradores")
        st.write("Aprove ou rejeite cadastros de novos moradores na sua lavanderia.")
        # Estatística rápida com cache:
        try:
            id_lavanderia = st.session_state.get("id_lavanderia_ativa")
            if id_lavanderia:
                moradores_pendentes = get_moradores_pendentes_cache(id_lavanderia)
                st.info(f"**Estatística:** {len(moradores_pendentes)} morador(es) aguardando aprovação.")
        except:
            pass
        if st.button("Abrir Aprovações", use_container_width=True, key="btn_aprovar"):
            st.session_state["subpagina_adm_predio"] = "aprovar_moradores"
            st.rerun()

    with tab2:
        st.subheader("Gerenciar Máquinas")
        st.write("Cadastre, edite ou remova máquinas da sua lavanderia.")
        # Estatísticas rápidas:
        try:
            id_lavanderia = st.session_state.get("id_lavanderia_ativa")
            if id_lavanderia:
                maquinas = get_maquinas_lavanderia(id_lavanderia)
                total = len(maquinas)
                operantes = len([m for m in maquinas if m.status_maquina != "manutencao"])
                st.info(f"**Estatística:** {total} máquina(s) total, {operantes} operante(s)")
        except:
            pass
        if st.button("Abrir Gerenciamento", use_container_width=True, key="btn_maquinas"):
            st.session_state["subpagina_adm_predio"] = "gerenciar_maquinas"
            st.rerun()

    with tab3:
        st.subheader("Gerenciar Manutenções")
        st.write("Agende manutenções preventivas e registre manutenções realizadas.")
        # Estatística rápida de pendências:
        try:
            id_lavanderia = st.session_state.get("id_lavanderia_ativa")
            if id_lavanderia and controlador_manutencao:
                pendentes = controlador_manutencao.listar_manutencoes_pendentes(id_lavanderia)
                st.info(f"**Estatística:** {len(pendentes)} manutenção(ões) pendente(s)")
        except:
            pass
        if st.button("Abrir Gerenciamento", use_container_width=True, key="btn_manutencoes"):
            st.session_state["subpagina_adm_predio"] = "gerenciar_manutencoes"
            st.rerun()

    with tab4:
        st.subheader("Relatórios")
        st.write("Acompanhe o uso e desempenho da sua lavanderia.")
        if st.button("Abrir Relatórios", use_container_width=True, key="btn_relatorios"):
            st.session_state["subpagina_adm_predio"] = "abrir_relatorios"
            st.rerun()

    with tab5:
        st.subheader("Ocorrências")
        st.write("Revise e gerencie os problemas reportados pelos moradores.")
        # Estatística rápida:
        try:
            id_lavanderia = st.session_state.get("id_lavanderia_ativa")
            if id_lavanderia:
                ocorrencias = get_ocorrencias_cache(id_lavanderia)
                st.info(f"**Estatística:** {len(ocorrencias)} ocorrência(s) em aberto")
        except:
            pass
        if st.button("Revisar Ocorrências", use_container_width=True, key="btn_ocorrencias"):
            st.session_state["subpagina_adm_predio"] = "visualizar_ocorrencias"
            st.rerun()

    with tab6:
        st.subheader("Meu Perfil")
        st.write("Gerencie suas informações pessoais e senha.")
        # Mostra informações atuais do usuário:
        usuario_dados = st.session_state.get("usuario_dados")
        if usuario_dados:
            st.markdown("#### **Suas informações atuais:**")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Nome:** {usuario_dados.get('nome', 'Não informado')}")
                st.write(f"**Email:** {usuario_dados.get('email', 'Não informado')}")
            with col2:
                st.write(f"**Telefone:** {usuario_dados.get('telefone', 'Não informado')}")
        if st.button("Editar Perfil", use_container_width=True, key="btn_perfil"):
            st.session_state["subpagina_adm_predio"] = "editar_perfil"
            st.rerun()
