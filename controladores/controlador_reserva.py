# Controller - controlador_reserva.py  
# Responsável pelas validações, por transformar dados para o model, decisões.
# Não faz acesso direto ao banco, chama funções do Model. Retorna resultados para a View.

from datetime import datetime
from modelos.reserva import (
    Reserva, 
    criar_reserva, 
    obter_reservas_por_maquina_e_data, 
    obter_reservas_por_usuario as obter_reservas_por_usuario_db, 
    obter_reserva_por_id,
    atualizar_status_reserva,
    atualizar_data_hora_reserva,
    contar_total_reservas
)

class ControladorReserva:
    def __init__(self):
        pass
    
    def _calcular_hora_fim(self, hora_inicio: str) -> str:
        hora = int(hora_inicio.split(':')[0])
        hora_fim = (hora + 1) % 24
        return f"{hora_fim:02d}:00"

    def obter_proximo_id(self) -> int:
        total = contar_total_reservas()
        return total + 1
    
    def criar_reserva(self, maquina_id: str, usuario_id: str, data: str, hora_inicio: str):
        if not self._horario_disponivel(maquina_id, data, hora_inicio):
            return None
        
        id_reserva = self.obter_proximo_id()
        hora_fim = self._calcular_hora_fim(hora_inicio)
        
        nova_reserva = Reserva(
            id_reserva=id_reserva, 
            id_maquina=maquina_id, 
            id_usuario=usuario_id, 
            data_reserva=data, 
            hora_inicio=hora_inicio,
            hora_fim=hora_fim,
            status_reserva="ativa"
        )

        return criar_reserva(nova_reserva)
    
    def visualizar_horarios_disponiveis(self, maquina_id: str, data: str):
        todos_horarios = [f"{hora:02d}:00" for hora in range(8, 20)]
        
        reservas_ocupadas = obter_reservas_por_maquina_e_data(maquina_id, data)
        horarios_ocupados = [reserva.hora_inicio for reserva in reservas_ocupadas]
        
        return [h for h in todos_horarios if h not in horarios_ocupados]
    
    def obter_reservas_por_usuario(self, usuario_id: str):
        return obter_reservas_por_usuario_db(usuario_id)
    
    def cancelar_reserva(self, id_reserva: int, usuario_id: str) -> bool:
        reserva = obter_reserva_por_id(id_reserva)
        # MUDANÇA: Verificando com os nomes de atributos corretos
        if reserva and reserva.id_usuario == usuario_id and reserva.status_reserva == "ativa":
            return atualizar_status_reserva(id_reserva, "cancelada")
        return False

    def editar_reserva(self, id_reserva: int, usuario_id: str, nova_data: str, nova_hora: str) -> bool:
        reserva_atual = obter_reserva_por_id(id_reserva)
        # MUDANÇA: Verificando com os nomes de atributos corretos
        if not (reserva_atual and reserva_atual.id_usuario == usuario_id and reserva_atual.status_reserva == "ativa"):
            return False

        # MUDANÇA: Usando 'reserva_atual.id_maquina'
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