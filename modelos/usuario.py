# Model - usuario.py
# Responsável pela persistência (consultas SQL), mapeamento simples entre linha do banco ↔ objeto Python e todas as operações CRUD com o MySQL.
# É onde cuidamos da integridade dos dados e do uso do conector (conexao_bd.conectar()). 
# Aqui entra regras de negócio do tipo "regra de domínio", que descrevem o comportamento do mundo real (ex: uma maquina nao pode ser reservadas por dois ao mesmo tempo)

from dataclasses import dataclass
from typing import Optional, List
from banco_de_dados.conexao_bd import conectar

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


# Autenticar Login:
def autenticar_usuario(email: str, senha: str):

    sql = "SELECT * FROM usuario WHERE email = %s AND senha = %s"    #comando sql
    conn = conectar() #abre conexão
    try:
        cur = conn.cursor(dictionary=True)  #para retornar em dicionario e não tupla
        cur.execute(sql, (email, senha)) #executa o comando sql
        usuario = cur.fetchone()    #fetchone quando se espera somente um resultado, retorna uma linha ou none
        cur.close()
        return usuario  #retorna o usuario
    finally:
        conn.close() #fecha conexão


# Criar conta de administrador do prédio:
def criar_administrador_predio(nome: str, email: str, senha: str, telefone: str, id_lavanderia: int):
    
    sql = "INSERT INTO usuario (nome, email, senha, telefone, tipo_usuario, status_conta, id_lavanderia) VALUES (%s, %s, %s, %s, 'adm_predio', 'ativa', %s)"
    conn = conectar() #abre conexão
    try:
        cur = conn.cursor()     #inicia o cursor 
        cur.execute(sql, (nome, email, senha, telefone, id_lavanderia)) #executa
        conn.commit()       #precisa de commit porque insert muda o banco
        new_id = cur.lastrowid      #lastrowid retorna o id, a chave primaria
        cur.close()     #fecha o cursor
        return new_id  #retorna o id
    finally:
        conn.close() #fecha conexão


# Contar quantidade de usuarios:
def contar_usuarios() -> int:

    sql = "SELECT COUNT(*) FROM usuario"   #comando sql
    conn = conectar()
    try:
        cur = conn.cursor()
        cur.execute(sql)  #executa sql
        qtd_usuarios = cur.fetchone()[0]
        cur.close()
        return qtd_usuarios    #retorna o total de usuarios
    finally:
        conn.close()
