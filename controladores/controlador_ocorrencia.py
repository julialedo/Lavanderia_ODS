# Controller - controlador_ocorrencia.py

from modelos.ocorrencia import (
    criar_ocorrencia, 
    listar_ocorrencias_db,
    listar_ocorrencias_por_lavanderia_db    
)
from modelos.notificacao import notificar_nova_ocorrencia 
from modelos.usuario import obter_id_adm_por_lavanderia

class ControladorOcorrencia:
    
    def __init__(self):
        pass

    def salvar_ocorrencia(self, id_maquina: str, descricao: str, nome_usuario: str, id_lavanderia: int):

        if not descricao or not nome_usuario:
            print("Erro: Dados incompletos para reportar ocorrência.")
            return None
        
        # Chama a função do modelo para criar e salvar
        try:
            nova_ocorrencia = criar_ocorrencia(id_maquina=id_maquina, descricao=descricao, nome_usuario=nome_usuario, id_lavanderia=id_lavanderia)
            
            if nova_ocorrencia:
                # 1. Busca o ID do Administrador (ADM do Prédio)
                id_adm_destino = obter_id_adm_por_lavanderia(id_lavanderia) 
                
                if id_adm_destino is not None:
                    # 2. Cria a notificação para o ADM
                    if notificar_nova_ocorrencia(id_adm_destino):
                        print(f"Notificação de nova ocorrência criada para o ADM ID: {id_adm_destino}")
                    else:
                        print("Aviso: Falha ao registrar notificação no banco de dados 'notificacoes'.")
                else:
                    print(f"Aviso: Administrador de Prédio não encontrado para a Lavanderia ID: {id_lavanderia}. Notificação não foi criada.")
            return nova_ocorrencia
            
        except Exception as e:
            print(f"Erro no controlador ao salvar ocorrência: {e}")
            return None
            
    def listar_ocorrencias(self):
        """
        Busca todas as ocorrências do banco de dados.
        """
        try:
            return listar_ocorrencias_db()
        except Exception as e:
            print(f"Erro no controlador ao listar ocorrências: {e}")
            return []




    def listar_ocorrencias_para_admin(self, id_lavanderia_admin: int):
        """
        Busca ocorrências específicas da lavanderia do Admin.
        """
        if not id_lavanderia_admin:
            print("Erro: Admin não tem ID de lavanderia associado.")
            return []
        
        try:
            # Chama a nova função filtrada do modelo
            return listar_ocorrencias_por_lavanderia_db(id_lavanderia_admin)
        except Exception as e:
            print(f"Erro no controlador ao listar ocorrências do admin: {e}")
            return []