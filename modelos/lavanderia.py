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
    qtd_maquinas: Optional[int]


# Cadastrar Lavanderia:
def criar_lavanderia(lav: Lavanderia) -> int:
    
    sql = "INSERT INTO lavanderia (id_adm_predio, nome, endereco, data_cadastro_lav, qtd_maquinas) VALUES (%s, %s, %s, NOW(), 0)" #comando sql
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


# Listar Lavanderias:
def listar_lavanderias() -> List[Lavanderia]:
    
    sql = "SELECT id_lavanderia, id_adm_predio, nome, endereco, data_cadastro_lav, qtd_maquinas FROM lavanderia" #comando sql
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


# Contar quantas Lavanderias tem cadastradas:
def contar_lavanderias() -> int:
    
    sql = "SELECT COUNT(*) FROM lavanderia" #comando sql
    conn = conectar() #abre a conexão
    try:
        cur = conn.cursor()
        cur.execute(sql) #executa comando
        qtd_lavanderias = cur.fetchone()[0]   
        cur.close()
        return qtd_lavanderias #retorna a quantidade de lavanderias
    finally:
        conn.close() #fecha conexão
