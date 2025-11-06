# Controller - controlador_ocorrencia.py

from modelos.ocorrencia import criar_ocorrencia

class ControladorOcorrencia:
    
    def __init__(self):
        pass

    def salvar_ocorrencia(self, id_maquina: str, descricao: str, nome_usuario: str):

        if not descricao or not nome_usuario:
            print("Erro: Dados incompletos para reportar ocorrência.")
            return None
        
        # Chama a função do modelo para criar e salvar
        try:
            nova_ocorrencia = criar_ocorrencia(id_maquina=id_maquina, descricao=descricao, nome_usuario=nome_usuario)
            return nova_ocorrencia
        except Exception as e:
            print(f"Erro no controlador ao salvar ocorrência: {e}")
            return None