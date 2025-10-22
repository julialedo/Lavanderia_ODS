# Model - maquina.py
# Responsável pela persistência (consultas SQL), mapeamento simples entre linha do banco ↔ objeto Python e todas as operações CRUD com o MySQL.
# É onde cuidamos da integridade dos dados e do uso do conector (conexao_bd.conectar()). 
# Aqui entra regras de negócio do tipo "regra de domínio", que descrevem o comportamento do mundo real (ex: uma maquina nao pode ser reservadas por dois ao mesmo tempo)

from dataclasses import dataclass   #cria um "molde" para a classe (com init, repr)
from typing import Optional, List
from banco_de_dados.conexao_bd import conectar

@dataclass
class Maquina:
    id_maquina: Optional[int]
    id_lavanderia: int
    codigo_maquina: str
    tipo_maquina: str    # lavadora ou secadora
    status_maquina: str  # livre, em_uso, manutenção
    capacidade: str


# Cadastrar Máquina no Banco:
def criar_maquina(maquina: Maquina) -> int:

    #gera o comando sql de Insert (a query), não coloquei id.maquina porque esta com autoincrement no banco:    
    sql = " INSERT INTO maquina (id_lavanderia, codigo_maquina, tipo_maquina, status_maquina, capacidade) VALUES (%s, %s, %s, %s, %s)"
    conn = conectar()  #chama a função conectar para abrir a conexão com o banco
    try:
        cur = conn.cursor()  #abre o cursor
        cur.execute(sql, (maquina.id_lavanderia, maquina.codigo_maquina, maquina.tipo_maquina, maquina.status_maquina, maquina.capacidade))  #executa a query com os valores
        conn.commit() #"salva" a alteração
        new_id = cur.lastrowid  #pega o id gerado pelo autoincrement
        cur.close()  #fecha o cursor
        return new_id  #retorna id
    finally:
        conn.close()  #fecha a conexão


# Atualizar Máquina no Banco:
def atualizar_maquina(id_maquina: int, campos: dict) -> bool:   #campos: dicionario com colunas e dados a atualizar
    
    set_clause = ", ".join(f"{k} = %s" for k in campos.keys())  #organiza os campos em uma "string" set_clause
    params = list(campos.values()) + [id_maquina]  #orgazina os parametros
    
    sql = f"UPDATE maquina SET {set_clause} WHERE id_maquina = %s" #gera o comando sql de UPDATE
    conn = conectar() #abre a conexao com o banco
    try:
        cur = conn.cursor()
        cur.execute(sql, params) #executa o comando sql
        conn.commit()
        linhas_afetadas = cur.rowcount #indica quantas linhas alteradas, 
        cur.close()
        return linhas_afetadas > 0  #retorna true se alterou algo, false se não 
    finally:
        conn.close() #fecha a conexão


# Deletar Máquinas no Banco:
def deletar_maquina(id_maquina: int) -> bool:
    
    sql = "DELETE FROM maquina WHERE id_maquina = %s" #comando sql delete
    conn = conectar() #abre a conexão
    try:
        cur = conn.cursor()
        cur.execute(sql, (id_maquina,)) #executa o comando
        conn.commit()
        linhas_afetadas = cur.rowcount
        cur.close()
        return linhas_afetadas> 0  #retorna true se a maquina foi deletada
    finally:
        conn.close() #fecha a conexão


# Listar Máquinas por lavanderia:
def listar_maquinas_por_lavanderia(id_lavanderia: int) -> List[Maquina]:
   
    sql = "SELECT id_maquina, id_lavanderia, codigo_maquina, tipo_maquina, status_maquina, capacidade FROM maquina WHERE id_lavanderia = %s" #comando sql select
    conn = conectar() #abre a conexão
    maquinas = []
    try:
        cur = conn.cursor()
        cur.execute(sql, (id_lavanderia,)) #executa o comando
        for row in cur.fetchall():    #para cada linha lida cria um objeto maquina e adiciona ele na lista maquinas
            maquinas.append(Maquina(*row))  
        cur.close()
        return maquinas  #retorna a lista de maquinas
    finally:
        conn.close() #fecha a conexão


# Acessar uma Máquina especifica pelo id dela:
def obter_maquina_por_id(id_maquina: int) -> Optional[Maquina]:
    
    sql = "SELECT id_maquina, id_lavanderia, codigo_maquina, tipo_maquina, status_maquina, capacidade FROM maquina WHERE id_maquina = %s" #comando sql select
    conn = conectar()  #abre conexão
    try:
        cur = conn.cursor()
        cur.execute(sql, (id_maquina,)) #executa o comando
        row = cur.fetchone()
        cur.close()
        if row:
            return Maquina(*row)   #retorna o objeto maquina
        return None
    finally:
        conn.close()  #fecha a conexão
