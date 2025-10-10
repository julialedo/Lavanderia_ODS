from banco_de_dados.conexao_bd import conectar

con = conectar()
if con:
    cursor = con.cursor()
    cursor.execute("SHOW TABLES;")
    for tabela in cursor:
        print(tabela)
    con.close()