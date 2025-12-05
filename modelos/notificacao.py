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