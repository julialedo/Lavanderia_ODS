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


def editar_usuario(id_usuario: int, nome: str, email: str, telefone: str, nova_senha: Optional[str] = None):
    # Base SQL para atualização
    sql = "UPDATE usuario SET nome = %s, email = %s, telefone = %s"
    params = [nome, email, telefone]
    
    # Se uma nova senha for fornecida, adicione-a ao SQL e aos parâmetros
    if nova_senha:
        sql += ", senha = %s"
        params.append(nova_senha)
        
    sql += " WHERE id_usuario = %s"
    params.append(id_usuario)

    conn = conectar() #abre conexão
    try:
        cur = conn.cursor()
        cur.execute(sql, tuple(params)) # Converte a lista de parâmetros para tupla
        conn.commit()
        rows_affected = cur.rowcount # Verifica se alguma linha foi alterada
        cur.close()
        return rows_affected > 0 # Retorna True se houve alteração
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


def criar_morador(nome: str, email: str, senha: str, telefone: str, id_lavanderia: int):
    
    sql = "INSERT INTO usuario (nome, email, senha, telefone, tipo_usuario, status_conta, data_cadastro_usuario, id_lavanderia) VALUES (%s, %s, %s, %s, 'morador', 'inativa', NOW(), %s)"
    conn = conectar()
    try:
        cur = conn.cursor()
        cur.execute(sql, (nome, email, senha, telefone, id_lavanderia))
        conn.commit()
        new_id = cur.lastrowid
        cur.close()
        return new_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


# Verificar se email já existe (mantém igual)
def verificar_email_existente(email: str) -> bool:
    sql = "SELECT COUNT(*) FROM usuario WHERE email = %s"
    conn = conectar()
    try:
        cur = conn.cursor()
        cur.execute(sql, (email,))
        count = cur.fetchone()[0]
        cur.close()
        return count > 0
    finally:
        conn.close()

# Aprovar conta de morador (para admin)
def aprovar_conta_morador(id_usuario: int):
    sql = "UPDATE usuario SET status_conta = 'ativa' WHERE id_usuario = %s AND tipo_usuario = 'morador'"
    conn = conectar()
    try:
        cur = conn.cursor()
        cur.execute(sql, (id_usuario,))
        conn.commit()
        rows_affected = cur.rowcount
        cur.close()
        return rows_affected > 0
    finally:
        conn.close()

# Listar moradores pendentes (para admin)
def listar_moradores_pendentes(id_lavanderia: int):
    sql = """SELECT id_usuario, nome, email, telefone, data_cadastro_usuario 
             FROM usuario 
             WHERE tipo_usuario = 'morador' AND status_conta = 'inativa' AND id_lavanderia = %s"""
    
    conn = conectar()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, (id_lavanderia,))
        moradores = cur.fetchall()
        cur.close()
        return moradores
    finally:
        conn.close()

# Listar moradores pendentes por lavanderia
def listar_moradores_pendentes_por_lavanderia(id_lavanderia: int):
    sql = """SELECT id_usuario, nome, email, telefone, data_cadastro_usuario 
             FROM usuario 
             WHERE tipo_usuario = 'morador' AND status_conta = 'inativa' AND id_lavanderia = %s"""
    
    conn = conectar()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, (id_lavanderia,))
        moradores = cur.fetchall()
        cur.close()
        return moradores
    finally:
        conn.close()

# Aprovar conta de morador
def aprovar_conta_morador(id_usuario: int):
    sql = "UPDATE usuario SET status_conta = 'ativa' WHERE id_usuario = %s AND tipo_usuario = 'morador'"
    conn = conectar()
    try:
        cur = conn.cursor()
        cur.execute(sql, (id_usuario,))
        conn.commit()
        rows_affected = cur.rowcount
        cur.close()
        return rows_affected > 0
    finally:
        conn.close()

# Rejeitar conta de morador (excluir ou manter como inativa)
def rejeitar_conta_morador(id_usuario: int):
    sql = "DELETE FROM usuario WHERE id_usuario = %s AND tipo_usuario = 'morador' AND status_conta = 'inativa'"
    conn = conectar()
    try:
        cur = conn.cursor()
        cur.execute(sql, (id_usuario,))
        conn.commit()
        rows_affected = cur.rowcount
        cur.close()
        return rows_affected > 0
    finally:
        conn.close()

# Obter usuário por ID
def obter_usuario_por_id(usuario_id: int):
    sql = "SELECT * FROM usuario WHERE id_usuario = %s"
    conn = conectar()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, (usuario_id,))
        usuario = cur.fetchone()
        cur.close()
        return usuario
    finally:
        conn.close()

# Obter lavanderia do usuário
def obter_lavanderia_usuario_db(usuario_id: int) -> Optional[int]:
    """Obtém o ID da lavanderia associada ao usuário"""
    sql = "SELECT id_lavanderia FROM usuario WHERE id_usuario = %s"
    conn = conectar()
    try:
        cur = conn.cursor()
        cur.execute(sql, (usuario_id,))
        resultado = cur.fetchone()
        cur.close()
        return resultado[0] if resultado and resultado[0] else None
    finally:
        conn.close()



def obter_id_adm_por_lavanderia(id_lavanderia: int) -> Optional[int]:
    """Busca e retorna o ID do usuário Administrador de Prédio associado a uma lavanderia."""
    
    # Busca um usuário que seja 'adm_predio' e pertença àquela lavanderia.
    # Usamos LIMIT 1 para garantir que buscaremos apenas um, mesmo que haja múltiplos admins.
    sql = """
    SELECT id_usuario 
    FROM usuario 
    WHERE id_lavanderia = %s AND tipo_usuario = 'adm_predio'
    LIMIT 1
    """
    conn = conectar()
    try:
        cur = conn.cursor()
        cur.execute(sql, (id_lavanderia,))
        resultado = cur.fetchone()
        cur.close()
        # Retorna o id_usuario (o primeiro elemento da tupla) ou None
        return resultado[0] if resultado and resultado[0] else None
    finally:
        conn.close()
