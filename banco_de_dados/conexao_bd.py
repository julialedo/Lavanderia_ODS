import mysql.connector
from mysql.connector import Error

def conectar():
    try:
        conexao = mysql.connector.connect(
            host='REMOVIDO',
            port='26076',
            user='root',
            password='REMOVIDO',
            database='railway'
        )
        if conexao.is_connected():
            print("Conexão bem-sucedida!")
        return conexao
    except Error as e:
        print("Erro ao conectar ao MySQL:", e)
        return None
