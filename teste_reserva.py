# test_reservas.py
import sys
from datetime import date
from datetime import datetime, timedelta

# Adiciona o diretório raiz ao path para encontrar os módulos
# (Pode não ser necessário dependendo de como você executa, mas é uma boa prática)
# sys.path.append('.') 

# Importa o controlador que queremos testar
from controladores.controlador_reserva import ControladorReserva
# Importa uma função do modelo para verificação direta no banco
from modelos.reserva import obter_reserva_por_id

def executar_testes():
    controlador = ControladorReserva()
    
    # DEBUG: Verificar todas as reservas para a máquina 2 na data 2025-10-16
    from modelos.reserva import obter_reservas_por_maquina_e_data
    reservas_existentes = obter_reservas_por_maquina_e_data("2", "2025-10-16")
    print("=== DEBUG: RESERVAS EXISTENTES ===")
    for reserva in reservas_existentes:
        print(f"ID: {reserva.id_reserva}, Máquina: {reserva.id_maquina}, Data: {reserva.data_reserva}, Hora: {reserva.hora_inicio}, Status: {reserva.status_reserva}")
    
    # TESTE 2: Verificar horários disponíveis
    MAQUINA_ID = "2"
    DATA_TESTE = "2025-10-16"
    HORA_INICIAL = "11:00"
    
    horarios_disponiveis = controlador.visualizar_horarios_disponiveis(MAQUINA_ID, DATA_TESTE)
    print(f"Horários disponíveis para máquina {MAQUINA_ID} em {DATA_TESTE}: {horarios_disponiveis}")
    
    # CORREÇÃO: O horário 10:00 DEVE estar disponível pois não há reservas para máquina 2
    assert HORA_INICIAL in horarios_disponiveis, f"FALHA: O horário {HORA_INICIAL} não está listado como disponível quando deveria estar."
    
    print("✓ TESTE 2: Horários disponíveis verificados com sucesso!")
if __name__ == "__main__":
    executar_testes()