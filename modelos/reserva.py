# Model - reserva.py

from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime, timedelta
from banco_de_dados.conexao_bd import conectar 

@dataclass
class Reserva:
    id_reserva: int
    id_maquina: str   
    id_usuario: str   
    data_reserva: str 
    hora_inicio: str
    hora_fim: str
    status_reserva: str 


# Criar uma reserva:
def criar_reserva(reserva: Reserva) -> Reserva:
    print(f"DEBUG: Data recebida no modelo: {reserva.data_reserva}")
    """Insere uma nova reserva no banco de dados."""
    sql = """
        INSERT INTO reservas 
        (id_reserva, id_maquina, id_usuario, data_reserva, hora_inicio, hora_fim, status_reserva) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    conn = conectar()
    try:
        cur = conn.cursor()
        cur.execute(sql, (
            reserva.id_reserva, reserva.id_maquina, reserva.id_usuario, 
            reserva.data_reserva, reserva.hora_inicio, reserva.hora_fim, 
            reserva.status_reserva
        ))
        conn.commit()
        cur.close()
        print(f"DEBUG: Data saindo no modelo: {reserva.data_reserva}")
        return reserva
    finally:
        conn.close()



def obter_reservas_por_maquina_e_data(maquina_id: str, data: str) -> List[Reserva]:
    """Busca todas as reservas ativas para uma máquina em uma data específica."""
    sql = "SELECT * FROM reservas WHERE id_maquina = %s AND data_reserva = %s AND status_reserva = 'ativa'"
    conn = conectar()
    reservas_ativas = []
    try:
        cur = conn.cursor()
        cur.execute(sql, (maquina_id, data))
        for row in cur.fetchall():
            # Converter a row para uma lista mutável
            row_list = list(row)
            # Se hora_inicio é timedelta, converter para string
            if isinstance(row_list[4], timedelta):  # hora_inicio está na posição 4
                total_seconds = int(row_list[4].total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                row_list[4] = f"{hours:02d}:{minutes:02d}:00"
            if isinstance(row_list[5], timedelta):  # hora_fim está na posição 5
                total_seconds = int(row_list[5].total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                row_list[5] = f"{hours:02d}:{minutes:02d}:00"
            
            reservas_ativas.append(Reserva(*row_list))
        cur.close()
        return reservas_ativas
    finally:
        conn.close()

def obter_reservas_por_usuario(usuario_id: str) -> List[Reserva]:
    """Busca todas as reservas ativas de um usuário."""
    sql = "SELECT * FROM reservas WHERE id_usuario = %s AND status_reserva = 'ativa'"
    conn = conectar()
    reservas_usuario = []
    try:
        cur = conn.cursor()
        cur.execute(sql, (usuario_id,))
        for row in cur.fetchall():
            reservas_usuario.append(Reserva(*row))
        cur.close()
        return reservas_usuario
    finally:
        conn.close()
        
def obter_reserva_por_id(id_reserva: str) -> Optional[Reserva]:
    """Busca uma reserva específica pelo seu ID."""
    sql = "SELECT * FROM reservas WHERE id_reserva = %s"
    conn = conectar()
    try:
        cur = conn.cursor()
        cur.execute(sql, (id_reserva,))
        row = cur.fetchone()
        cur.close()
        if row:
            row_list = list(row)
            reserva_corrigida = Reserva(
                id_reserva=row[0],     
                id_maquina=str(row[2]),     
                id_usuario=str(row[1]),     
                data_reserva=str(row[3]),
                hora_inicio=row[4],
                hora_fim=row[5],
                status_reserva=row[6]
            )
            
            return reserva_corrigida        
        return None
    finally:
        conn.close()

def atualizar_status_reserva(id_reserva: str, novo_status: str) -> bool:
    """Atualiza o status de uma reserva (ex: para 'cancelada')."""
    # MUDANÇA: Tabela 'reservas' e nome da coluna atualizados
    sql = "UPDATE reservas SET status_reserva = %s WHERE id_reserva = %s"
    conn = conectar()
    try:
        cur = conn.cursor()
        cur.execute(sql, (novo_status, id_reserva))
        conn.commit()
        affected = cur.rowcount
        cur.close()
        return affected > 0
    finally:
        conn.close()

def atualizar_data_hora_reserva(id_reserva: str, nova_data: str, nova_hora: str, nova_hora_fim: str) -> bool:
    """Atualiza a data e hora de uma reserva."""
    sql = "UPDATE reservas SET data_reserva = %s, hora_inicio = %s, hora_fim = %s WHERE id_reserva = %s"
    conn = conectar()
    try:
        cur = conn.cursor()
        cur.execute(sql, (nova_data, nova_hora, nova_hora_fim, id_reserva))
        conn.commit()
        affected = cur.rowcount
        cur.close()
        return affected > 0
    finally:
        conn.close()

def obter_maior_id_reserva() -> int:
    """Retorna o maior ID de reserva existente"""
    sql = "SELECT COALESCE(MAX(id_reserva), 0) FROM reservas"
    conn = conectar()
    try:
        cur = conn.cursor()
        cur.execute(sql)
        maior_id = cur.fetchone()[0]
        cur.close()
        return maior_id
    finally:
        conn.close()

def obter_reservas_por_lavanderia_e_periodo(id_lavanderia: int, data_inicial: str, data_final: str) -> List[Reserva]:
    """Busca todas as reservas de uma lavanderia em um período específico."""
    sql = """
        SELECT r.* 
        FROM reservas r
        JOIN maquina m ON r.id_maquina = m.id_maquina
        WHERE m.id_lavanderia = %s 
        AND r.data_reserva BETWEEN %s AND %s
        AND r.status_reserva = 'ativa'
        ORDER BY r.data_reserva, r.hora_inicio
    """
    conn = conectar()
    reservas = []
    try:
        cur = conn.cursor()
        cur.execute(sql, (id_lavanderia, data_inicial, data_final))
        for row in cur.fetchall():
            # Converter a row para uma lista mutável
            row_list = list(row)
            # Se hora_inicio é timedelta, converter para string
            if isinstance(row_list[4], timedelta):  # hora_inicio está na posição 4
                total_seconds = int(row_list[4].total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                row_list[4] = f"{hours:02d}:{minutes:02d}"
            if isinstance(row_list[5], timedelta):  # hora_fim está na posição 5
                total_seconds = int(row_list[5].total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                row_list[5] = f"{hours:02d}:{minutes:02d}"
            
            reservas.append(Reserva(*row_list))
        cur.close()
        return reservas
    finally:
        conn.close()

def listar_reservas_futuras_por_lavanderia(id_lavanderia: int) -> List[Reserva]:
    """
    Busca todas as reservas ativas ou agendadas (no futuro) de uma lavanderia,
    garantindo que o status seja 'ativa' ou 'agendada'.
    """
    
    # Busca reservas cuja data_reserva é hoje ou no futuro E status_reserva é 'ativa' ou 'agendada'
    sql = """
        SELECT 
            r.* FROM reservas r
        JOIN maquina m ON r.id_maquina = m.id_maquina
        WHERE m.id_lavanderia = %s 
          AND r.status_reserva IN ('ativa', 'agendada')
        ORDER BY r.data_reserva, r.hora_inicio
    """
    conn = conectar()
    reservas = []
    try:
        cur = conn.cursor()
        cur.execute(sql, (id_lavanderia,))
        for row in cur.fetchall():
            # Assumindo que a conversão de row para objeto Reserva acontece aqui.
            row_list = list(row)
            reservas.append(Reserva(*row_list)) # Certifique-se que a conversão de tipo (timedelta/string) está correta aqui
        cur.close()
        return reservas
    finally:
        conn.close()


# Contar total de reservas no dia de hoje: OK
def contar_reservas_hoje():
    sql = "SELECT COUNT(*) FROM reservas WHERE data_reserva = CURDATE()"
    conn = conectar()
    try:
        cur = conn.cursor()
        cur.execute(sql)
        total = cur.fetchone()[0]
        cur.close()
        return total
    finally:
        conn.close()


# Retornar as lavanderias mais ativas, de acordo com as reservas: OK
def lavanderias_mais_ativas():
    sql = """
        SELECT 
            l.id_lavanderia, 
            l.nome, 
            COUNT(r.id_reserva) AS reservas 
        FROM lavanderia l 
        # FAZ JOIN COM MAQUINA, que tem o id_lavanderia
        LEFT JOIN maquina m ON m.id_lavanderia = l.id_lavanderia 
        # DEPOIS, FAZ JOIN COM RESERVAS, que tem o id_maquina
        LEFT JOIN reservas r ON r.id_maquina = m.id_maquina 
        GROUP BY l.id_lavanderia, l.nome 
        ORDER BY reservas DESC 
        LIMIT 5
    """
    conn = conectar()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql)
        dados = cur.fetchall()
        cur.close()
        return dados
    finally:
        conn.close()