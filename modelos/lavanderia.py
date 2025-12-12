# Model - lavanderia.py
# Responsável pela persistência (consultas SQL), mapeamento simples entre linha do banco ↔ objeto Python e todas as operações CRUD com o MySQL.
# É onde cuidamos da integridade dos dados e do uso do conector (conexao_bd.conectar()). 
# Aqui entra regras de negócio do tipo "regra de domínio", que descrevem o comportamento do mundo real (ex: uma maquina nao pode ser reservadas por dois ao mesmo tempo)

from dataclasses import dataclass
from typing import Optional, List
from banco_de_dados.conexao_bd import conectar

@dataclass
class Lavanderia:
    id_lavanderia: Optional[int]
    id_adm_predio: Optional[int]
    nome: str
    endereco: str
    data_cadastro_lav: Optional[str]


# Cadastrar Lavanderia: OK
def criar_lavanderia(lav: Lavanderia) -> int:
    sql = "INSERT INTO lavanderia (id_adm_predio, nome, endereco, data_cadastro_lav) VALUES (%s, %s, %s, NOW())" #comando sql
    conn = conectar()  #abre a conexão
    try:
        cur = conn.cursor()
        cur.execute(sql, (lav.id_adm_predio, lav.nome, lav.endereco)) #execura o comando sql
        conn.commit()
        new_id = cur.lastrowid  #pega o id
        cur.close()
        return new_id #retorna o id 
    finally:
        conn.close()  #fecha a conexão


# Listar Lavanderias: OK
def listar_lavanderias() -> List[Lavanderia]:
    sql = "SELECT id_lavanderia, id_adm_predio, nome, endereco, data_cadastro_lav FROM lavanderia" #comando sql
    conn = conectar() #abre a conexão
    lavanderias = []
    try:
        cur = conn.cursor()
        cur.execute(sql)  #executa o comando sql 
        for row in cur.fetchall():
            lavanderias.append(Lavanderia(*row)) #para cada lavanderia, salva os dados na lista lavanderias
        cur.close()
        return lavanderias  #retorna a lista de lavanderias
    finally:
        conn.close() #fecha


# Obter lavanderia por ID: OK
def retornar_lavanderia_por_id(lavanderia_id: int):
    sql = "SELECT * FROM lavanderia WHERE id_lavanderia = %s"
    conn = conectar()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, (lavanderia_id,))
        lavanderia = cur.fetchone()
        cur.close()
        return lavanderia
    finally:
        conn.close()


# Atualizar lavanderia criada se adm, o seu novo adm definido: OK
def atualizar_adm_lavanderia(id_lavanderia: int, id_adm: int):
    sql = "UPDATE lavanderia SET id_adm_predio = %s WHERE id_lavanderia = %s"
    conn = conectar()
    try:
        cur = conn.cursor()
        cur.execute(sql, (id_adm, id_lavanderia))
        conn.commit()
        cur.close()
        return True
    finally:
        conn.close()


# Contar total de lavanderias: OK
def contar_lavanderias():
    sql = "SELECT COUNT(*) FROM lavanderia"
    conn = conectar()
    try:
        cur = conn.cursor()
        cur.execute(sql)
        total = cur.fetchone()[0]
        cur.close()
        return total
    finally:
        conn.close()


# Excluir Lavanderia: OK
def excluir_lavanderia_por_id(id_lavanderia: int) -> bool:
    sql = "DELETE FROM lavanderia WHERE id_lavanderia = %s"
    conn = conectar()
    try:
        cur = conn.cursor()
        cur.execute(sql, (id_lavanderia,))
        conn.commit()
        cur.close()
        # Retorna True se a exclusão foi bem-sucedida (pelo menos uma linha afetada)
        return cur.rowcount > 0
    finally:
        conn.close()


# Remover o Administrador do Predio da Lavanderia: OK
def remover_adm_lavanderia(id_lavanderia: int, id_adm_predio: int) -> bool:
    sql_uptade_lav = "UPDATE lavanderia SET id_adm_predio = NULL WHERE id_lavanderia = %s"
    sql_delete_associacao = "DELETE FROM usuario_lavanderia WHERE id_usuario = %s AND id_lavanderia = %s"
    conn = conectar()
    try:
        cur = conn.cursor()
        cur.execute(sql_delete_associacao, (id_adm_predio, id_lavanderia))
        cur.execute(sql_uptade_lav, (id_lavanderia,))
        conn.commit()
        cur.close()
        return cur.rowcount > 0
    finally:
        conn.close()