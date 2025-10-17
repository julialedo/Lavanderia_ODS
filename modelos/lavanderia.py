# Model - lavanderia.py
# Responsável pela persistência (consultas SQL), mapeamento simples entre linha do banco ↔ objeto Python. 
# Todas as operações CRUD com o MySQL. Onde cuidamos da integridade dos dados e do uso do conector (conexao_bd.conectar()). 

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
    
    sql = "INSERT INTO lavanderia (id_adm_predio, nome, endereco, data_cadastro_lav, qtd_maquinas) VALUES (%s, %s, %s, NOW(), 0)" #query
    conn = conectar()  #abre a conexão
    try:
        cur = conn.cursor()
        cur.execute(sql, (lav.id_adm_predio, lav.nome, lav.endereco)) #execura o comando sql
        conn.commit()
        return cur.lastrowid #retorna o id gerado
    finally:
        conn.close()  #fecha a conexão


# Listar Lavanderias:
def listar_lavanderias() -> List[Lavanderia]:
    
    sql = "SELECT id_lavanderia, id_adm_predio, nome, endereco, data_cadastro_lav, qtd_maquinas FROM lavanderia"
    conn = conectar() #abre a conexão
    lavanderias = []
    try:
        cur = conn.cursor()
        cur.execute(sql)  #executa o comando sql 
        for row in cur.fetchall():
            lavanderias.append(Lavanderia(*row)) #para cada lavanderia, salva os dados na lista
        return lavanderias
    finally:
        conn.close() #fecha


# Contar quantas Lavanderias tem cadastradas:
def contar_lavanderias() -> int:
    
    sql = "SELECT COUNT(*) FROM lavanderia"
    conn = conectar() #abre a conexão
    try:
        cur = conn.cursor()
        cur.execute(sql) #executa comando
        return cur.fetchone()[0] #retorna a quantidade de lavanderias
    finally:
        conn.close() #fecha conexão
