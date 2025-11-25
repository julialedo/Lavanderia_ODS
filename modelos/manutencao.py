# Model - manutencao.py
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime
from banco_de_dados.conexao_bd import conectar


@dataclass
class Manutencao:
    id_manutencao: Optional[int]
    id_maquina: int
    data_agendada: str
    data_realizada: Optional[str]
    descricao: str
    nome_adm: str

# Criar manutenção


def criar_manutencao(manutencao: Manutencao) -> int:
    sql = """
    INSERT INTO manutencoes 
    (id_maquina, data_agendada, data_realizada, descricao, nome_adm) 
    VALUES (%s, %s, %s, %s, %s)
    """
    conn = conectar()
    try:
        cur = conn.cursor()
        cur.execute(sql, (
            manutencao.id_maquina,
            manutencao.data_agendada,
            manutencao.data_realizada,
            manutencao.descricao,
            manutencao.nome_adm
        ))
        conn.commit()
        new_id = cur.lastrowid
        cur.close()
        return new_id
    except Exception as e:
        print(f"❌ Erro no modelo ao criar manutenção: {e}")
        conn.rollback()
        raise e
    finally:
        conn.close()

# Listar manutenções por lavanderia - CORRIGIDO


def listar_manutencoes_por_lavanderia(id_lavanderia: int) -> List[Manutencao]:
    sql = """
    SELECT m.id_manutencao, m.id_maquina, m.data_agendada, m.data_realizada, m.descricao, m.nome_adm
    FROM manutencoes m
    JOIN maquina maq ON m.id_maquina = maq.id_maquina
    WHERE maq.id_lavanderia = %s
    ORDER BY m.data_agendada DESC
    """
    conn = conectar()
    manutencoes = []
    try:
        cur = conn.cursor()
        cur.execute(sql, (id_lavanderia,))
        for row in cur.fetchall():
            manutencoes.append(Manutencao(
                id_manutencao=row[0],
                id_maquina=row[1],
                data_agendada=row[2],
                data_realizada=row[3],
                descricao=row[4],
                nome_adm=row[5]
            ))
        cur.close()
        return manutencoes
    except Exception as e:
        print(f"❌ Erro no modelo ao listar manutenções: {e}")
        return []
    finally:
        conn.close()

# Listar manutenções pendentes - CORRIGIDO


def listar_manutencoes_pendentes(id_lavanderia: int) -> List[Manutencao]:
    sql = """
    SELECT m.id_manutencao, m.id_maquina, m.data_agendada, m.data_realizada, m.descricao, m.nome_adm
    FROM manutencoes m
    JOIN maquina maq ON m.id_maquina = maq.id_maquina
    WHERE maq.id_lavanderia = %s AND m.data_realizada IS NULL
    ORDER BY m.data_agendada ASC
    """
    conn = conectar()
    manutencoes = []
    try:
        cur = conn.cursor()
        cur.execute(sql, (id_lavanderia,))
        for row in cur.fetchall():
            manutencoes.append(Manutencao(
                id_manutencao=row[0],
                id_maquina=row[1],
                data_agendada=row[2],
                data_realizada=row[3],
                descricao=row[4],
                nome_adm=row[5]
            ))
        cur.close()
        return manutencoes
    except Exception as e:
        print(f"❌ Erro no modelo ao listar manutenções pendentes: {e}")
        return []
    finally:
        conn.close()

# Atualizar data realizada da manutenção


def atualizar_data_realizada(id_manutencao: int, data_realizada: str) -> bool:
    sql = "UPDATE manutencoes SET data_realizada = %s WHERE id_manutencao = %s"
    conn = conectar()
    try:
        cur = conn.cursor()
        cur.execute(sql, (data_realizada, id_manutencao))
        conn.commit()
        linhas_afetadas = cur.rowcount
        cur.close()
        return linhas_afetadas > 0
    finally:
        conn.close()

# Obter manutenção por ID - CORRIGIDO


def obter_manutencao_por_id(id_manutencao: int) -> Optional[Manutencao]:
    sql = "SELECT id_manutencao, id_maquina, data_agendada, data_realizada, descricao, nome_adm FROM manutencoes WHERE id_manutencao = %s"
    conn = conectar()
    try:
        cur = conn.cursor()
        cur.execute(sql, (id_manutencao,))
        row = cur.fetchone()
        cur.close()
        if row:
            return Manutencao(
                id_manutencao=row[0],
                id_maquina=row[1],
                data_agendada=row[2],
                data_realizada=row[3],
                descricao=row[4],
                nome_adm=row[5]
            )
        return None
    finally:
        conn.close()

# Verificar se máquina tem manutenção agendada


def verificar_manutencao_agendada(id_maquina: str, datetime_agendada: str) -> bool:
    """
    Verifica se já existe manutenção agendada para esta máquina no mesmo horário
    """
    sql = """
    SELECT COUNT(*) FROM manutencoes 
    WHERE id_maquina = %s AND data_agendada = %s AND data_realizada IS NULL
    """
    conn = conectar()
    try:
        cur = conn.cursor()
        cur.execute(sql, (id_maquina, datetime_agendada))
        count = cur.fetchone()[0]
        cur.close()
        return count > 0
    finally:
        conn.close()
