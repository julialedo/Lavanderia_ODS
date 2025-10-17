# Model - reserva.py
# Responsável pela persistência (consultas SQL), mapeamento simples entre linha do banco ↔ objeto Python. 
# Todas as operações CRUD com o MySQL. Onde cuidamos da integridade dos dados e do uso do conector (conexao_bd.conectar()). 

from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime, timedelta
from banco_de_dados.conexao_bd import conectar 


@dataclass
class Reserva:
    id_reserva: int
    id_maquina: str   # MUDANÇA: de 'maquina_id' para 'id_maquina'
    id_usuario: str   # MUDANÇA: de 'usuario_id' para 'id_usuario'
    data_reserva: str # MUDANÇA: de 'data' para 'data_reserva'
    hora_inicio: str
    hora_fim: str
    status_reserva: str # MUDANÇA: de 'status' para 'status_reserva'
    # MUDANÇA: A coluna 'data_criacao' foi removida para corresponder ao banco de dados

# --- Funções de Interação com o Banco de Dados ---

def criar_reserva(reserva: Reserva) -> Reserva:
    print(f"DEBUG: Data recebida no modelo: {reserva.data_reserva}")
    """Insere uma nova reserva no banco de dados."""
    # MUDANÇA: Tabela 'reservas' e nomes das colunas atualizados
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
    # MUDANÇA: Tabela 'reservas' e nomes das colunas atualizados
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
    # MUDANÇA: Tabela 'reservas' e nome da coluna atualizados
    sql = "SELECT * FROM reservas WHERE id_reserva = %s"
    conn = conectar()
    try:
        cur = conn.cursor()
        cur.execute(sql, (id_reserva,))
        row = cur.fetchone()
        cur.close()
        if row:
            return Reserva(*row)
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
    # MUDANÇA: Tabela 'reservas' e nome da coluna atualizados
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

def contar_total_reservas() -> int:
    """Conta o número total de reservas já criadas para gerar o próximo ID."""
    # MUDANÇA: Tabela 'reservas'
    sql = "SELECT COUNT(*) FROM reservas"
    conn = conectar()
    try:
        cur = conn.cursor()
        cur.execute(sql)
        total = cur.fetchone()[0]
        cur.close()
        return total
    finally:
        conn.close()