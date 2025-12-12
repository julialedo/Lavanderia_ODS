# controladores/controlador_notificacao.py

from modelos.notificacao import listar_notificacoes_por_usuario, marcar_notificacao_como_lida_db

class ControladorNotificacao:
    
    def __init__(self):
        pass
        
    def listar_notificacoes_do_usuario(self, id_usuario_logado: int) -> list[dict]:
        """
        Busca e retorna as notificações do usuário logado.
        """
        if not id_usuario_logado:
            return []
            
        try:
            return listar_notificacoes_por_usuario(id_usuario_logado)
        except Exception as e:
            print(f"Erro no controlador ao listar notificações: {e}")
            return []
        
    def marcar_como_lida(self, id_notificacao: int) -> bool:
        """Marca uma notificação como lida através do modelo."""
        try:
            return marcar_notificacao_como_lida_db(id_notificacao)
        except Exception as e:
            print(f"Erro no controlador ao marcar como lida: {e}")
            return False