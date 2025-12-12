# Controller - controlador_maquina.py 
# Responsável pelas validações, transformar dados para o model, decisões.
# Não faz acesso direto ao banco, chama funções do Model. Retorna resultados para a View.
# Aqui entra as regras de negócio do tipo "regra de validação" que controla o fluxo da aplicação (ex: verificar se todos os campos obrigatórios foram preenchidos pelo usuario).
from datetime import datetime, time, timedelta
from modelos.maquina import Maquina, criar_maquina, atualizar_maquina, deletar_maquina, listar_maquinas_por_lavanderia, obter_maquina_por_id, atualizar_status_maquina, obter_status_e_reserva_ativa
from modelos.reserva import listar_reservas_futuras_por_lavanderia, atualizar_status_reserva
class ControladorMaquina:

    #Cadastrar Máquinas: OK
    def cadastrar_maquina(self, id_lavanderia: int, codigo: str, tipo: str, capacidade: str, status: str = "livre"):
        if tipo not in ("lavadora", "secadora"):  #validação de tipo
            raise ValueError("Tipo inválido")
        maquina = Maquina(id_maquina=None, id_lavanderia=id_lavanderia, codigo_maquina=codigo, tipo_maquina=tipo, status_maquina=status, capacidade=capacidade) #constroi objeto maquina
        new_id = criar_maquina(maquina) #chama criar maquina do modelo e recebe como retorno o id da maquina criada
        return new_id
        #REGISTRAR LOG/AUDITORIA DE CADASTRO DE MAQUINA


    #Editar Máquinas: OK
    def editar_maquina(self, id_maquina: int, campos: dict):
        #VALIDAÇÃO DE SE FOR DEIXAR EM MANUTENÇÃO, AVISAR OS QUE TEM RESERVAS ATIVAS
        #REGISTRAR LOG/AUDITORIA
        maquina = obter_maquina_por_id(id_maquina)
        if not maquina:
            raise ValueError("Máquina não encontrada.")
        if "tipo_maquina" in campos and campos["tipo_maquina"] not in ("lavadora", "secadora"):
            raise ValueError("Tipo de máquina inválido.")
        if "status_maquina" in campos and campos["status_maquina"] not in ("livre", "em_uso", "manutencao"):
            raise ValueError("Status de máquina inválido.")
        ok = atualizar_maquina(id_maquina, campos) #chama atualizar maquina do modelo
        return ok


    #Remover Máquina: OK
    def remover_maquina(self, id_maquina: int):
        from modelos.notificacao import notificar_exclusao_de_maquina_para_usuarios 
        from modelos.usuario import listar_ids_usuarios_por_lavanderia 
        # 1. Obter a máquina para pegar os dados e id_lavanderia
        maquina_a_deletar = obter_maquina_por_id(id_maquina)
        if not maquina_a_deletar:
            raise ValueError("Máquina não encontrada para remoção.")

        id_lavanderia = maquina_a_deletar.id_lavanderia
        codigo_maquina = maquina_a_deletar.codigo_maquina
        tipo_maquina = maquina_a_deletar.tipo_maquina

        # **VALIDAÇÕES (já existente, mas agora com contexto de notificação)**
        # VALIDAR SE TEM RESERVAS FUTURAS, CANCELAR E AVISAR MORADORES
        # ... (sua lógica de validação/aviso sobre reservas) ...
        
        # 2. Deletar a máquina do banco
        deletado_ok = deletar_maquina(id_maquina) # Chama deletar maquina do modelo
        
        if deletado_ok:
            # 3. Listar todos os usuários da lavanderia
            ids_usuarios = listar_ids_usuarios_por_lavanderia(id_lavanderia)

            # 4. Criar notificações para todos os usuários
            # Chamamos a função de alto nível que acabamos de criar no modelo de notificação
            notificar_exclusao_de_maquina_para_usuarios(
                id_lavanderia, 
                codigo_maquina, 
                tipo_maquina.capitalize(), 
                ids_usuarios
            )
            # REGISTRAR LOG/AUDITORIA DA EXCLUSÃO
            
        return deletado_ok

    # Listar Máquinas por lavanderia: OK
    def listar_por_lavanderia(self, id_lavanderia: int):
        return listar_maquinas_por_lavanderia(id_lavanderia)


    # Obter Máquina por Id: OK
    def obter(self, id_maquina: int):
        return obter_maquina_por_id(id_maquina)
    

    #Calcula Ciclo da maquina sendo utilizada, se houver. 
    def calcular_progresso(self, inicio: datetime, fim: datetime, agora: datetime) -> tuple:
    
        duracao_total = (fim - inicio).total_seconds()
        tempo_passado = (agora - inicio).total_seconds()
        progresso_percentual = (tempo_passado / duracao_total) * 100

        #simulação etapas do ciclo
        if progresso_percentual < 33:
            etapa = "Lavando"
        elif progresso_percentual < 66:
            etapa = "Enxaguando"
        elif progresso_percentual < 99:
            etapa = "Centrifugando"
        else:
            etapa = "Concluindo"
            
        tempo_restante_segundos = int((fim - agora).total_seconds()) #calcula tempo restante
        
        if tempo_restante_segundos <= 0:
            tempo_restante_str = "Concluído!"
            progresso_percentual = 100
        else:
            horas = tempo_restante_segundos // 3600
            minutos = (tempo_restante_segundos % 3600) // 60
            segundos = tempo_restante_segundos % 60
            
            if horas > 0:
                 tempo_restante_str = f"{horas}h {minutos:02d}m"
            else:
                 tempo_restante_str = f"{minutos:02d}m {segundos:02d}s"
        
        return round(progresso_percentual), tempo_restante_str, etapa
    

    #Obter status das maquinas
    def obter_status_em_tempo_real(self, id_lavanderia: int, id_usuario_logado: int) -> list:

        maquinas = listar_maquinas_por_lavanderia(id_lavanderia)
        reservas_futuras = listar_reservas_futuras_por_lavanderia(id_lavanderia)
        
        status_map = {
            m.id_maquina: {
                "id_maquina": m.id_maquina,
                "codigo_maquina": m.codigo_maquina,
                "tipo_maquina": m.tipo_maquina.capitalize(),
                "capacidade": m.capacidade,
                "status": m.status_maquina.replace('_', ' ').title(), 
                "progresso": 0,
                "tempo_restante": "N/A",
                "etapa_ciclo": "N/A",
                "is_my_reservation": False, 
            } for m in maquinas
        }
        
        agora = datetime.now()
        
        for reserva in reservas_futuras:
            maquina_id = int(reserva.id_maquina)
            print(f"maquina id {maquina_id}")
            maquina_data = status_map.get(maquina_id)

            if not maquina_data:
                continue 

            if maquina_data["status"].lower() == "manutencao":  #se o statur for manutenção, ignora reservas
                 continue
            
            try:
                data_hora_inicio = datetime.strptime(f"{reserva.data_reserva} {reserva.hora_inicio}", "%Y-%m-%d %H:%M:%S")
                data_hora_fim = datetime.strptime(f"{reserva.data_reserva} {reserva.hora_fim}", "%Y-%m-%d %H:%M:%S")
            except Exception:
                try:
                    data_hora_inicio = datetime.strptime(f"{reserva.data_reserva} {reserva.hora_inicio}", "%Y-%m-%d %H:%M:%S")
                    data_hora_fim = datetime.strptime(f"{reserva.data_reserva} {reserva.hora_fim}", "%Y-%m-%d %H:%M:%S")
                except Exception:
                    # não conseguir parsear, pula
                    continue

            #Verificar se a reserva está ATIVA AGORA (Ciclo em andamento)
            if data_hora_inicio <= agora < data_hora_fim:
                
                progresso, tempo_restante, etapa_ciclo = self.calcular_progresso(
                    data_hora_inicio, data_hora_fim, agora
                )
                
                # Atualiza o status da máquina com os dados da reserva ativa
                maquina_data.update({
                    "status": "Em Uso", # Sobrescreve o status inicial do BD, se necessário
                    "progresso": progresso,
                    "tempo_restante": tempo_restante,
                    "etapa_ciclo": etapa_ciclo,
                    "is_my_reservation": str(reserva.id_usuario) == str(id_usuario_logado)
                })
                print(f"RESERVA id usuario {reserva.id_usuario}, id usuario_logado: {id_usuario_logado}")
            
                # Certifica-se que no banco a máquina está com status 'em_uso'
                try:
                    atualizar_status_maquina(maquina_id, "em_uso")
                except Exception as e:
                    print(f"Erro ao marcar máquina como em_uso no DB: {e}")


            # b) Verificar se é uma reserva FUTURA
            elif agora < data_hora_inicio:
                
                # Se a máquina não está em uso fica Agendada
                if maquina_data["status"].lower() == "livre":
                    maquina_data["status"] = "Agendada"
                    maquina_data["tempo_restante"] = f"Inicia às {reserva.hora_inicio}"


            # Caso: reserva já passou (reserva expirou) -> liberar máquina e fechar reserva
            elif agora >= data_hora_fim:
                # Se a reserva passou, devemos garantir que ela esteja finalizada e a maquina liberada.
                try:
                    # atualizar status reserva no banco para 'finalizada' (se ainda estiver ativa)
                    atualizar_status_reserva(reserva.id_reserva, "concluida")
                except Exception as e:
                    print(f"Erro ao finalizar reserva {reserva.id_reserva}: {e}")
                try:
                    atualizar_status_maquina(maquina_id, "livre")
                except Exception as e:
                    print(f"Erro ao liberar máquina {maquina_id}: {e}")

                # Também refletir no mapa local:
                maquina_data.update({
                    "status": "Livre",
                    "progresso": 0,
                    "tempo_restante": "N/A",
                    "etapa_ciclo": "N/A",
                    "is_my_reservation": False
                })

        # 5. Converter o dicionário de volta para uma lista (o formato que a View espera)
        return list(status_map.values())