# Controller - controlador_manutencao.py
from modelos.manutencao import (
    Manutencao, criar_manutencao, listar_manutencoes_por_lavanderia,
    atualizar_data_realizada, obter_manutencao_por_id,
    verificar_manutencao_agendada, listar_manutencoes_pendentes
)
from datetime import datetime


class ControladorManutencao:

    # Agendar manutenção preventiva
    def agendar_manutencao_preventiva(self, id_maquina: int, data_agendada: str,
                                      hora_agendada: str, descricao: str, nome_adm: str) -> int:
        """
        Agenda uma manutenção preventiva para uma máquina
        """
        # Validar dados
        if not id_maquina or not data_agendada or not hora_agendada or not descricao or not nome_adm:
            raise ValueError("Todos os campos são obrigatórios")

        # DEBUG DETALHADO: Verificar os valores recebidos
        print(f"🔍 DEBUG - Controlador - Valores recebidos:")
        print(f"ID Máquina: {id_maquina}")
        print(f"Data: {data_agendada} (tipo: {type(data_agendada)})")
        print(f"Hora: {hora_agendada} (tipo: {type(hora_agendada)})")
        print(f"Descrição: {descricao}")
        print(f"Nome ADM: {nome_adm}")

        # CORREÇÃO: Se hora_agendada for um objeto time, converter para string
        if hasattr(hora_agendada, 'strftime'):
            # É um objeto time, converter para string no formato HH:MM:SS
            hora_agendada = hora_agendada.strftime("%H:%M:%S")
            print(f"🔄 Hora convertida de time para string: {hora_agendada}")

        # Garantir que a hora esteja no formato HH:MM:SS
        if ':' in hora_agendada:
            partes_hora = hora_agendada.split(':')
            if len(partes_hora) == 2:  # Formato "HH:MM"
                hora_agendada = f"{partes_hora[0]}:{partes_hora[1]}:00"
                print(f"🔄 Hora formatada para HH:MM:SS: {hora_agendada}")

        # Combinar data e hora em um DATETIME
        datetime_agendada = f"{data_agendada} {hora_agendada}"
        print(f"✅ DATETIME FINAL para salvar: {datetime_agendada}")

        # Verificar se a data é futura
        try:
            data_agendada_obj = datetime.strptime(
                data_agendada, "%Y-%m-%d").date()
            if data_agendada_obj < datetime.now().date():
                raise ValueError("A data de agendamento deve ser futura")
        except ValueError as e:
            raise ValueError(f"Data de agendamento inválida: {e}")

        # Verificar se já existe manutenção agendada
        if verificar_manutencao_agendada(id_maquina, datetime_agendada):
            raise ValueError(
                "Já existe uma manutenção agendada para esta máquina neste horário")

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
        print(f"✅ Manutenção salva com ID: {new_id}")
        return new_id

    # Registrar manutenção realizada
    def registrar_manutencao_realizada(self, id_maquina: int, descricao: str,
                                       nome_adm: str, data_realizada: str = None) -> int:
        """
        Registra uma manutenção já realizada
        """
        if not id_maquina or not descricao or not nome_adm:
            raise ValueError(
                "ID da máquina, descrição e nome do admin são obrigatórios")

        data_realizada = data_realizada or datetime.now().strftime("%Y-%m-%d")

        # Para manutenções corretivas, usar data atual e hora padrão (00:00:00)
        data_hora_realizada = f"{data_realizada} 00:00:00"

        print(f"🔍 DEBUG - Manutenção Realizada:")
        print(f"ID Máquina: {id_maquina}")
        print(f"Data/Hora: {data_hora_realizada}")

        manutencao = Manutencao(
            id_manutencao=None,
            id_maquina=id_maquina,
            data_agendada=data_hora_realizada,
            data_realizada=data_realizada,
            descricao=descricao,
            nome_adm=nome_adm
        )

        new_id = criar_manutencao(manutencao)
        return new_id

    # Listar todas as manutenções
    def listar_manutencoes(self, id_lavanderia: int) -> list:
        """
        Lista todas as manutenções de uma lavanderia
        """
        return listar_manutencoes_por_lavanderia(id_lavanderia)

    # Listar manutenções pendentes
    def listar_manutencoes_pendentes(self, id_lavanderia: int) -> list:
        """
        Lista manutenções agendadas mas não realizadas
        """
        return listar_manutencoes_pendentes(id_lavanderia)

    # Marcar manutenção como realizada
    def marcar_como_realizada(self, id_manutencao: int, data_realizada: str = None) -> bool:
        """
        Marca uma manutenção agendada como realizada
        """
        data_realizada = data_realizada or datetime.now().strftime("%Y-%m-%d")
        return atualizar_data_realizada(id_manutencao, data_realizada)

    # Obter manutenção por ID
    def obter_manutencao(self, id_manutencao: int):
        """
        Obtém detalhes de uma manutenção específica
        """
        return obter_manutencao_por_id(id_manutencao)
