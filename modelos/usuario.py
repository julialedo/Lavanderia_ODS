# Model - usuario.py
# Responsável pela persistência (consultas SQL), mapeamento simples entre linha do banco ↔ objeto Python. 
# Todas as operações CRUD com o MySQL. Onde cuidamos da integridade dos dados e do uso do conector (conexao_bd.conectar()). 

from dataclasses import dataclass
from typing import Optional, List
from banco_de_dados.conexao_bd import conectar
from datetime import datetime

@dataclass
class Usuario:
    id_usuario: Optional[int]
    nome: str
    email: str
    senha: str
    telefone: str
    tipo_usuario: str       # morador, adm_predio, adm_plataforma
    status_conta: str       # ativo, inativo
    data_cadastro_usuario: Optional[str]
    id_lavanderia: Optional[int]  # pode ser None se for admin da plataforma


# Criar conta de administrador do prédio:
def criar_administrador_predio(nome: str, email: str, senha: str, telefone: str, id_lavanderia: int):
    
    sql = "INSERT INTO usuario (nome, email, senha, telefone, tipo_usuario, status_conta, id_lavanderia) VALUES (%s, %s, %s, %s, 'adm_predio', 'ativa', %s)"
    conn = conectar() #abre conexão
    try:
        cur = conn.cursor()
        cur.execute(sql, (nome, email, senha, telefone, id_lavanderia)) #executa
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close() #fecha


# Contar quantidade de usuarios:
def contar_usuarios() -> int:
    sql = "SELECT COUNT(*) FROM usuario"
    conn = conectar()
    try:
        cur = conn.cursor()
        cur.execute(sql)
        return cur.fetchone()[0]
    finally:
        conn.close()
