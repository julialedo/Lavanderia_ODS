# Controller - controlador_manutencao.py
# Responsável pelas validações, transformar dados para o model, decisões.

from modelos.manutencao import (
    Manutencao, criar_manutencao, listar_manutencoes_por_lavanderia,
    atualizar_manutencao_realizada, verificar_manutencao_agendada, listar_manutencoes_pendentes
)
from datetime import datetime


class ControladorManutencao:

    # Agendar uma manutenção preventiva para uma máquina: OK
    def agendar_manutencao_preventiva(self, id_maquina: int, data_agendada: str, hora_agendada: str, descricao: str, nome_adm: str) -> int:
        # Validar o preenchimento:
        if not id_maquina or not data_agendada or not hora_agendada or not descricao or not nome_adm:
            raise ValueError("Todos os campos são obrigatórios!")

        # Combinar data e hora em um DATETIME
        datetime_agendada = f"{data_agendada} {hora_agendada}"

        # Verificar se já existe manutenção agendada para esta maquina neste dia e hora:
        if verificar_manutencao_agendada(id_maquina, datetime_agendada):
            raise ValueError("Já existe uma manutenção agendada para esta máquina neste horário")

        # Criar objeto manutenção
        manutencao = Manutencao(
            id_manutencao=None,
            id_maquina=id_maquina,
            data_agendada=datetime_agendada,
            data_realizada=None,
            descricao=descricao,
            nome_adm=nome_adm
        )
        # Salvar no banco
        new_id = criar_manutencao(manutencao)
        return new_id


    # Registrar manutenção realizada: OK
    def registrar_manutencao_realizada(self, id_maquina: int, data_realizada: str, hora_realizada: str, descricao: str, nome_adm: str) -> int:
        #valida o preenchimento:
        if not id_maquina or not descricao or not nome_adm:
            raise ValueError(
                "ID da máquina, descrição e nome do admin são obrigatórios")

        # Combinar data e hora em um DATETIME
        datetime_realizada = f"{data_realizada} {hora_realizada}"
        manutencao = Manutencao(
            id_manutencao=None,
            id_maquina=id_maquina,
            data_agendada=None,
            data_realizada=datetime_realizada,
            descricao=descricao,
            nome_adm=nome_adm
        )
        new_id = criar_manutencao(manutencao)
        return new_id


    # Marcar manutenção como realizada: OK
    def atualizar_manutencao(self, id_manutencao: int, id_maquina: int, data_realizada: str, hora_realizada: str, descricao: str, nome_adm: str) -> int:
        #valida o preenchimento:
        if not id_maquina or not descricao or not nome_adm:
            raise ValueError(
                "ID da máquina, descrição e nome do admin são obrigatórios")

        # Combinar data e hora em um DATETIME
        datetime_realizada = f"{data_realizada} {hora_realizada}"
        manutencao = Manutencao(
            id_manutencao=id_manutencao,
            id_maquina=id_maquina,
            data_agendada=None,
            data_realizada=datetime_realizada,
            descricao=descricao,
            nome_adm=nome_adm
        )
        new_id = atualizar_manutencao_realizada(manutencao)
        return new_id
    

    # Listar todas as manutenções: OK
    def listar_manutencoes(self, id_lavanderia: int) -> list:
        return listar_manutencoes_por_lavanderia(id_lavanderia)


    # Listar manutenções pendentes: OK
    def listar_manutencoes_pendentes(self, id_lavanderia: int) -> list:
        return listar_manutencoes_pendentes(id_lavanderia)