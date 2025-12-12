# modelos/notificacao.py

from pydantic import BaseModel
from datetime import date
from banco_de_dados.conexao_bd import conectar 

class Notificacao(BaseModel):
    id_notificacao: int
    id_usuario: int
    mensagem: str
    data_envio: date
    status: str # 'nao_lido', 'lido'

# --- Funções de Banco de Dados ---

def _obter_proximo_id_notificacao() -> int:
    """Busca o maior ID existente na tabela notificacoes e retorna o próximo (para id incremental)."""
    try:
        with conectar() as conexao:
            with conexao.cursor() as cursor:
                cursor.execute("SELECT MAX(id_notificacao) FROM notificacoes")
                resultado = cursor.fetchone()
                if resultado and resultado[0] is not None:
                    return resultado[0] + 1
                return 1 # Começa em 1 se a tabela estiver vazia
    except Exception as e:
        print(f"Erro ao obter próximo ID de notificação: {e}")
        return -1 # Indica erro

def criar_notificacao_db(notificacao: Notificacao) -> bool:
    """Insere uma nova notificação no banco de dados."""
    try:
        with conectar() as conexao:
            with conexao.cursor() as cursor:
                sql = """
                INSERT INTO notificacoes 
                (id_notificacao, id_usuario, mensagem, data_envio, status)
                VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    notificacao.id_notificacao,
                    notificacao.id_usuario,
                    notificacao.mensagem,
                    notificacao.data_envio,
                    notificacao.status,
                ))
                conexao.commit()
                return True
    except Exception as e:
        print(f"Erro ao inserir notificação no banco: {e}")
        return False

def notificar_nova_ocorrencia(id_usuario_adm: int) -> bool:
    """Função de alto nível para criar a notificação padrão de nova ocorrência."""
    
    proximo_id = _obter_proximo_id_notificacao()
    if proximo_id == -1:
        return False # Falha ao gerar ID

    nova_notificacao = Notificacao(
        id_notificacao=proximo_id,
        id_usuario=id_usuario_adm, # ID do Administrador
        mensagem="Tem uma nova ocorrência", # Mensagem solicitada
        data_envio=date.today(), # Data atual solicitada
        status="nao_lido", # Status solicitado
    )
    
    return criar_notificacao_db(nova_notificacao)


def listar_notificacoes_por_usuario(id_usuario: int) -> list[dict]:
    """Busca todas as notificações destinadas a um ID de usuário específico."""
    notificacoes = []
    try:
        with conectar() as conexao:
            # Retorna em formato de dicionário para facilitar o uso na tela/frontend
            with conexao.cursor(dictionary=True) as cursor: 
                sql = """
                SELECT id_notificacao, mensagem, data_envio, status 
                FROM notificacoes 
                WHERE id_usuario = %s 
                ORDER BY data_envio DESC, id_notificacao DESC
                """
                cursor.execute(sql, (id_usuario,))
                resultados = cursor.fetchall()
                
                if resultados:
                    # Converte o objeto date para string, se necessário, para evitar problemas no frontend
                    for res in resultados:
                         res['data_envio'] = res['data_envio'].strftime('%d/%m/%Y')
                         notificacoes.append(res)
                         
        return notificacoes
    except Exception as e:
        print(f"Erro ao listar notificações para o usuário {id_usuario}: {e}")
        return []
    
    # modelos/notificacao.py (Confirme que esta função existe)

# ... (outras funções e imports) ...

def marcar_notificacao_como_lida_db(id_notificacao: int) -> bool:
    """Atualiza o status de uma notificação para 'lido'."""
    try:
        with conectar() as conexao: # Supondo que 'conectar()' é sua função de conexão
            with conexao.cursor() as cursor:
                sql = """
                UPDATE notificacoes 
                SET status = 'lido' 
                WHERE id_notificacao = %s
                """
                cursor.execute(sql, (id_notificacao,))
                conexao.commit()
                return cursor.rowcount > 0 
    except Exception as e:
        print(f"Erro ao marcar notificação {id_notificacao} como lida no DB: {e}")
        return False