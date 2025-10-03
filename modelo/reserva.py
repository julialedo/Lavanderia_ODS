from datetime import datetime

class Reserva:
    def __init__(self, id_reserva: str, maquina_id: str, usuario_id: str, 
                 data: str, hora_inicio: str, status: str = "ativa"):
        self.id_reserva = id_reserva
        self.maquina_id = maquina_id
        self.usuario_id = usuario_id
        self.data = data  
        self.hora_inicio = hora_inicio  
        self.hora_fim = hora_fim
        self.status = status  # pode estar ativa, cancelada ou concluída
        self.data_criacao = datetime.now().isoformat()
    

    def _calcular_hora_fim(self, hora_inicio: str) -> str:
        """Calcula a hora de fim (1 hora depois)"""
        hora = int(hora_inicio.split(':')[0])
        hora_fim = (hora + 1) % 24           #aqui vai mudar a hora de acordo com o tempo da máquina
        return f"{hora_fim:02d}:00" 