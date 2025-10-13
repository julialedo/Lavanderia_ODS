from controladores.controlador_reserva import ControladorReserva

# Teste do controlador
controlador = ControladorReserva()

print("=== TESTE SISTEMA DE RESERVAS ===")

# 1. Visualizar horários disponíveis (deve mostrar todos)
print("\n1. Horários disponíveis (inicial):")
horarios = controlador.visualizar_horarios_disponiveis("M001", "2024-01-15")
print(f"M001 dia 15/01: {horarios}")

# 2. Fazer primeira reserva
print("\n2. Fazendo reserva às 10:00...")
reserva1 = controlador.criar_reserva("M001", "ana123", "2024-01-15", "10:00")
print(f"Reserva criada: {reserva1.id_reserva if reserva1 else 'FALHOU'}")

# 3. Tentar reservar mesmo horário (deve falhar)
print("\n3. Tentando reservar mesmo horário...")
reserva2 = controlador.criar_reserva("M001", "joao456", "2024-01-15", "10:00")
print(f"Segunda reserva: {reserva2.id_reserva if reserva2 else 'BLOQUEADA (correto!)'}")

# 4. Ver horários disponíveis novamente (10:00 sumiu)
print("\n4. Horários disponíveis após reserva:")
horarios = controlador.visualizar_horarios_disponiveis("M001", "2024-01-15")
print(f"M001 dia 15/01: {horarios}")

print("\n✅ TESTE CONCLUÍDO!")