from datetime import datetime

class Usuario:
    def __init__(self, id_usuario: str, telefone: str, senha: str, 
                 tipo_perfil: str = "morador", status_conta: str = "ativa"):
        self.id_usuario = id_usuario
        self.telefone = telefone
        self.senha = senha
        self.tipo_perfil = tipo_perfil  # "morador", "admin_lavanderia", "admin_plataforma"
        self.status_conta = status_conta
        self.data_criacao = datetime.now()