import mysql.connector
from mysql.connector import Error


# Definindo a conexão com o Banco de Dados
def conectar():
    try:
        conexao = mysql.connector.connect(  #estabelecendo a conexão, passando os dados do banco de dados online
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
