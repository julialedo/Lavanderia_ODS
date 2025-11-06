# Modelo - ocorrencia.py
# Representa a tabela 'problemas_reportados' e as funções de banco de dados.

from pydantic import BaseModel
from datetime import date
from banco_de_dados.conexao_bd import conectar

class ProblemaReportado(BaseModel):
    id_problema: int
    id_maquina: str | None = None
    descricao: str
    data_problema: date
    nome_usuario: str

def listar_ocorrencias_db() -> list[ProblemaReportado]:
    """Busca todas as ocorrências do banco, ordenadas pela mais recente."""
    ocorrencias = []
    try:
        with conectar() as conexao:
            with conexao.cursor(dictionary=True) as cursor:
                # Ordena por ID decrescente para ver as mais novas primeiro
                sql = "SELECT * FROM problemas_reportados ORDER BY id_problema DESC"
                cursor.execute(sql)
                resultados = cursor.fetchall()
                
                if resultados:
                    for res in resultados:
                        # Converte o resultado do BD para o objeto Pydantic
                        ocorrencias.append(ProblemaReportado(**res))
        return ocorrencias
    except Exception as e:
        print(f"Erro ao listar ocorrências no banco: {e}")
        return [] # Retorna lista vazia em caso de erro    

def _obter_proximo_id() -> int:
    """Busca o maior ID existente e retorna o próximo."""
    try:
        with conectar() as conexao:
            with conexao.cursor() as cursor:
                # Usando o nome da tabela e coluna corretos
                cursor.execute("SELECT MAX(id_problema) FROM problemas_reportados")
                resultado = cursor.fetchone()
                if resultado and resultado[0] is not None:
                    return resultado[0] + 1
                return 1 # Se a tabela estiver vazia
    except Exception as e:
        print(f"Erro ao obter próximo ID do problema: {e}")
        return -1 # Indica um erro

def reportar_problema_db(problema: ProblemaReportado) -> bool:
    """Insere um novo reporte de problema no banco de dados."""
    try:
        with conectar() as conexao:
            with conexao.cursor() as cursor:
                # Usando o nome da tabela e colunas corretos
                sql = """
                INSERT INTO problemas_reportados 
                (id_problema, id_maquina, descricao, data_problema, nome_usuario)
                VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    problema.id_problema,
                    problema.id_maquina,
                    problema.descricao,
                    problema.data_problema,
                    problema.nome_usuario,
                ))
                conexao.commit()
                return True
    except Exception as e:
        print(f"Erro ao inserir problema no banco: {e}")
        return False

# Esta função é chamada pelo 'ControladorOcorrencia'
def criar_ocorrencia(id_maquina: str, descricao: str, nome_usuario: str) -> ProblemaReportado | None:
    """Cria e salva um novo objeto ProblemaReportado."""
    
    proximo_id = _obter_proximo_id()
    if proximo_id == -1:
        return None # Falha ao gerar ID

    # Criamos um objeto 'ProblemaReportado' com os dados corretos da tabela
    novo_problema = ProblemaReportado(
        id_problema=proximo_id,
        id_maquina=id_maquina,
        descricao=descricao,
        data_problema=date.today(),
        nome_usuario=nome_usuario,
    )
    
    if reportar_problema_db(novo_problema):
        return novo_problema
    else:
        return None