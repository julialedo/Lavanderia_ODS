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


# Autenticar Login: OK
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


# Editar dados de perfil:
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


# Verificar se email já existe: OK
def verificar_email_existente(email: str) -> bool:
    sql = "SELECT COUNT(*) FROM usuario WHERE email = %s"
    conn = conectar()
    try:
        cur = conn.cursor()
        cur.execute(sql, (email))
        count = cur.fetchone()[0]
        cur.close()
        return count > 0
    finally:
        conn.close()


# Cadastrar novo morador no banco, com status de conta inativa, após ele fazer o cadastro: OK
def criar_morador(nome: str, email: str, senha: str, telefone: str, id_lavanderia: str):
    
    sql = "INSERT INTO usuario (nome, email, senha, telefone, tipo_usuario, status_conta, data_cadastro_usuario) VALUES (%s, %s, %s, %s, 'morador', 'inativa', NOW())"
    sql_associacao = "INSERT INTO usuario_lavanderia (id_usuario, id_lavanderia) VALUES (%s, %s)"

    conn = conectar()
    try:
        cur = conn.cursor()
        cur.execute(sql, (nome, email, senha, telefone))
        new_id = cur.lastrowid
        cur.execute(sql_associacao, (new_id, id_lavanderia))
        conn.commit()
        cur.close()
        return new_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


# Cadastrar novo administrador do prédio: OK +-
def criar_administrador_predio(nome: str, email: str, senha: str, telefone: str, id_lavanderia: int):
    
    sql = "INSERT INTO usuario (nome, email, senha, telefone, tipo_usuario, status_conta) VALUES (%s, %s, %s, %s, 'adm_predio', 'ativa')"
    sql_associacao = "INSERT INTO usuario_lavanderia (id_usurio, id_lavanderia) VALUES (%s, %s)"
    conn = conectar() #abre conexão
    try:
        cur = conn.cursor()     #inicia o cursor 
        cur.execute(sql, (nome, email, senha, telefone)) #executa
        new_id = cur.lastrowid      #lastrowid retorna o id, a chave primaria
        cur.execute(sql_associacao, (new_id, id_lavanderia))
        conn.commit()       #precisa de commit porque insert muda o banco
        cur.close()     #fecha o cursor
        return new_id, "Administrador e associação criados com sucesso." #retorna o id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close() #fecha conexão


# Listar moradores pendentes (para adm_predio): OK
def listar_moradores_pendentes_lavanderia(id_lavanderia: int):

    sql = "SELECT u.id_usuario, u.nome, u.email, u.telefone, u.data_cadastro_usuario FROM usuario u INER JOIN usuario_lavanderia ul ON u.id_usuario = ul.id_usuario WHERE u.tipo_usuario = 'morador' AND u.status_conta = 'inativa' AND ul.id_lavanderia = %s"
    conn = conectar()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, (id_lavanderia))
        moradores = cur.fetchall()
        cur.close()
        return moradores
    finally:
        conn.close()


# Aprovar conta de morador (para adm_predio): OK
def aprovar_conta_morador(id_usuario: int, id_lavanderia: int):

    sql = "UPDATE usuario SET status_conta = 'ativa' WHERE id_usuario = %s AND tipo_usuario = 'morador'"
    conn = conectar()
    try:
        cur = conn.cursor()
        cur.execute(sql, (id_usuario))
        rows_affected = cur.rowcount
        conn.commit()
        cur.close()
        return rows_affected > 0
    finally:
        conn.close()


# Rejeitar conta de morador (excluir ou manter como inativa): OK
def rejeitar_conta_morador(id_usuario: int):

    sql = "DELETE FROM usuario WHERE id_usuario = %s AND tipo_usuario = 'morador' AND status_conta = 'inativa'"
    conn = conectar()
    try:
        cur = conn.cursor()
        cur.execute(sql, (id_usuario))
        conn.commit()
        rows_affected = cur.rowcount
        cur.close()
        return rows_affected > 0
    finally:
        conn.close()


# Contar quantidade de usuarios: OK
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


# Obter usuário por ID: OK
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


#IMPLEMENTAR OBTER USUARIO POR EMAIL


# Obter lista de lavanderia por usuario
def obter_lavanderias_por_usuario(usuario_id: int) -> List[int]:
     
    sql = " SELECT id_lavanderia FROM usuario_lavanderia WHERE id_usuario = %s"
    conn = conectar()
    lista_ids = []
    try:
        cur = conn.cursor()
        cur.execute(sql, (usuario_id,))
        # fetchall() retorna uma lista de tuplas (ex: [(101,), (105,), ...])
        resultados = cur.fetchall()
        cur.close()
        # Transforma a lista de tuplas em uma lista simples de inteiros
        if resultados:
            lista_ids = [resultado[0] for resultado in resultados]
            
        return lista_ids
    
    except Exception as e:
        print(f"Erro ao obter lavanderias do usuário: {e}")
        return []
    finally:
        conn.close()
