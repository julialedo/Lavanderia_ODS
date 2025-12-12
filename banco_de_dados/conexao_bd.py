#Arquivo que inicia faz a conexão da aplicação com o bando de dados hospedado em streamlit:

import mysql.connector
from mysql.connector import Error

# Definindo a conexão com o Banco de Dados
def conectar():
    try:
        conexao = mysql.connector.connect(  #estabelecendo a conexão, passando os dados do banco de dados online
            host='REMOVIDO', 
            port=16027,
            user='root',
            password='REMOVIDO',
            database='railway',
            time_zone='-03:00'
        )
        if conexao.is_connected():
            print("Conexão bem-sucedida!")
        return conexao
    except Error as e:
        print("Erro ao conectar ao MySQL. Detalhes:", e)
        return None
