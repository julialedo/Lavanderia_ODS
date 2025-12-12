# Controller - controlador_reserva.py


from datetime import datetime, timedelta
from modelos.maquina import atualizar_status_maquina
from modelos.reserva import (
    Reserva, 
    criar_reserva, 
    obter_reservas_por_maquina_e_data, 
    obter_reservas_por_usuario as obter_reservas_por_usuario_db, 
    obter_reserva_por_id,
    atualizar_status_reserva,
    atualizar_data_hora_reserva,
    obter_maior_id_reserva
)

class ControladorReserva:
    def __init__(self):
        pass
    
    def _calcular_hora_fim(self, hora_inicio: str) -> str:
        hora_fim = (datetime.strptime(hora_inicio, "%H:%M:%S") + timedelta(hours=1)).strftime("%H:%M:%S")
        return hora_fim
    

    def obter_proximo_id(self) -> int:
        from modelos.reserva import obter_maior_id_reserva 
        maior_id = obter_maior_id_reserva()
        return maior_id + 1 if maior_id else 1
    

    def criar_reserva(self, maquina_id: str, usuario_id: str, data_agendamento: str, hora_inicio: str):
        print(f"DEBUG: Tentando criar reserva - Máquina: {maquina_id}, Usuário: {usuario_id}, Data: {data_agendamento}, Hora: {hora_inicio}")
        if not self._horario_disponivel(maquina_id, data_agendamento, hora_inicio):
            return None
        
        id_reserva = self.obter_proximo_id()
        print(f"DEBUG: Próximo ID gerado: {id_reserva}")
        hora_fim = self._calcular_hora_fim(hora_inicio)
        
        nova_reserva = Reserva(
            id_reserva=id_reserva, 
            id_maquina=str(maquina_id), 
            id_usuario=str(usuario_id), 
            data_reserva=data_agendamento, 
            hora_inicio=hora_inicio,
            hora_fim=hora_fim,
            status_reserva="ativa"
        )
        print(f"DEBUG: Reserva criada - {nova_reserva}")
        print(f"DEBUG: Data saída no controlador: {data_agendamento}")
        resultado = criar_reserva(nova_reserva) #chama model

        # Se a reserva começa agora (ou já está em andamento), atualiza status da máquina
        try:
            agora = datetime.now()
            inicio_dt = datetime.strptime(f"{data_agendamento} {hora_inicio}", "%Y-%m-%d %H:%M")
            fim_dt = datetime.strptime(f"{data_agendamento} {hora_fim}", "%Y-%m-%d %H:%M")
        except Exception:
            # fallback: se as strings trouxerem segundos, tentar sem corte
            try:
                inicio_dt = datetime.strptime(f"{data_agendamento} {hora_inicio}", "%Y-%m-%d %H:%M:%S")
                fim_dt = datetime.strptime(f"{data_agendamento} {hora_fim}", "%Y-%m-%d %H:%M:%S")
            except Exception:
                inicio_dt = None
                fim_dt = None

        if inicio_dt and fim_dt:
            if inicio_dt <= agora < fim_dt:
                try:
                    atualizar_status_maquina(int(maquina_id), "em_uso")
                except Exception as e:
                    print(f"Erro ao atualizar status da máquina para 'em_uso': {e}")

        return resultado


    def visualizar_horarios_disponiveis(self, maquina_id: str, data: str):
        todos_horarios = [f"{hora:02d}:00" for hora in range(8, 20)]
    
        reservas_ocupadas = obter_reservas_por_maquina_e_data(maquina_id, data)
    
        horarios_ocupados = [reserva.hora_inicio[:5] for reserva in reservas_ocupadas]
        
        print(f"DEBUG - Horários ocupados: {horarios_ocupados}")
        return [h for h in todos_horarios if h not in horarios_ocupados]

    def obter_reservas_por_usuario(self, usuario_id: str):
        return obter_reservas_por_usuario_db(usuario_id)
    
    def cancelar_reserva(self, id_reserva: int, usuario_id: str) -> bool:
        reserva = obter_reserva_por_id(id_reserva)

        if reserva and reserva.id_usuario == str(usuario_id) and reserva.status_reserva == "ativa":
            return atualizar_status_reserva(id_reserva, "cancelada")
        return False

    def editar_reserva(self, id_reserva: int, usuario_id: str, nova_data: str, nova_hora: str) -> bool:
        reserva_atual = obter_reserva_por_id(id_reserva)

        if not (reserva_atual and str(reserva_atual.id_usuario) == str(usuario_id) and reserva_atual.status_reserva == "ativa"):
            return False

        if not self._horario_disponivel(reserva_atual.id_maquina, nova_data, nova_hora):
            return False 
        
        nova_hora_fim = self._calcular_hora_fim(nova_hora)
        return atualizar_data_hora_reserva(id_reserva, nova_data, nova_hora, nova_hora_fim)

    def _horario_disponivel(self, maquina_id: str, data: str, hora_inicio: str) -> bool:
        reservas_no_horario = obter_reservas_por_maquina_e_data(maquina_id, data)
        for reserva in reservas_no_horario:
            if reserva.hora_inicio == hora_inicio:
                return False
        return True

    def listar_reservas_periodo(self, id_lavanderia: int, data_inicial: str, data_final: str):
        """Lista reservas de uma lavanderia em um período específico"""
        from modelos.reserva import obter_reservas_por_lavanderia_e_periodo
        return obter_reservas_por_lavanderia_e_periodo(id_lavanderia, data_inicial, data_final)
