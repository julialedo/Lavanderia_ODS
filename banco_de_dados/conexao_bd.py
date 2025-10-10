import mysql.connector
from mysql.connector import Error

def conectar():
    try:
        conexao = mysql.connector.connect(
            host='maglev.proxy.rlwy.net',
            port='26076',
            user='root',
            password='tolRZxoWcJVgPkBDtOHkzrSqfkQkKSja',
            database='railway'
        )
        if conexao.is_connected():
            print("Conexão bem-sucedida!")
        return conexao
    except Error as e:
        print("Erro ao conectar ao MySQL:", e)
        return None
