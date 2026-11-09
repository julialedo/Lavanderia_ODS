#Arquivo que inicia faz a conexão da aplicação com o bando de dados hospedado em streamlit:

import os

import mysql.connector
from mysql.connector import Error

# Definindo a conexão com o Banco de Dados
def conectar():
    try:
        conexao = mysql.connector.connect(  #estabelecendo a conexão, passando os dados do banco de dados online
            host=os.getenv('DB_HOST'), 
            port=int(os.getenv('DB_PORT', '3306')),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME'),
            time_zone='-03:00'
        )
        if conexao.is_connected():
            print("Conexão bem-sucedida!")
        return conexao
    except Error as e:
        print("Erro ao conectar ao MySQL. Detalhes:", e)
        return None
