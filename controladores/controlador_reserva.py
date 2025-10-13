from modelos.reserva import Reserva

class ControladorReserva:
    def __init__(self):
        self.reservas = []  # Lista temporária - DEPOIS MUDAR NA CONEXÃO DO BD
    
    def obter_proximo_id(self) -> str:
        return f"R{len(self.reservas) + 1:04d}"
    
    def criar_reserva(self, maquina_id: str, usuario_id: str, data: str, hora_inicio: str):
        from modelos.reserva import Reserva
        
        # Verificar se horário está disponível
        if not self._horario_disponivel(maquina_id, data, hora_inicio):
            return None
        id_reserva = self.obter_proximo_id()
        nova_reserva = Reserva(id_reserva, maquina_id, usuario_id, data, hora_inicio)
        # Salvar (por enquanto na lista)
        self.reservas.append(nova_reserva)
        return nova_reserva
    
    def visualizar_horarios_disponiveis(self, maquina_id: str, data: str):
        # Todos os horários possíveis (8h às 20h)
        todos_horarios = [f"{hora:02d}:00" for hora in range(8, 20)]
        
        # Horários ocupados
        horarios_ocupados = []
        for reserva in self.reservas:
            if (reserva.maquina_id == maquina_id and 
                reserva.data == data and 
                reserva.status == "ativa"):
                horarios_ocupados.append(reserva.hora_inicio)
        
        # Retorna horários livres
        return [h for h in todos_horarios if h not in horarios_ocupados]
    
    def obter_reservas_por_usuario(self, usuario_id: str):
        """Retorna todas as reservas de um usuário"""
        return [r for r in self.reservas if r.usuario_id == usuario_id and r.status == "ativa"]
    
    def cancelar_reserva(self, id_reserva: str, usuario_id: str) -> bool:
        for reserva in self.reservas:
            if reserva.id_reserva == id_reserva and reserva.usuario_id == usuario_id:
                reserva.status = "cancelada"
                return True
        return False

    def editar_reserva(self, id_reserva: str, usuario_id: str, nova_data: str, nova_hora: str):
        for reserva in self.reservas:
            if (reserva.id_reserva == id_reserva and 
                reserva.usuario_id == usuario_id and
                reserva.status == "ativa"):
                # Verifica se novo horário está disponível
                if not self._horario_disponivel(reserva.maquina_id, nova_data, nova_hora):
                    return False  
                
                reserva.data = nova_data
                reserva.hora_inicio = nova_hora
                reserva.hora_fim = reserva._calcular_hora_fim(nova_hora)
                return True
        
        return False  # Reserva não encontrada

    def _horario_disponivel(self, maquina_id: str, data: str, hora_inicio: str):
        for reserva in self.reservas:
            if (reserva.maquina_id == maquina_id and 
                reserva.data == data and 
                reserva.hora_inicio == hora_inicio and
                reserva.status == "ativa"):
                return False  # Horário ocupado
        return True  # Horário livre