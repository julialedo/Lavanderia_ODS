
from modelos.lavanderia import Lavanderia, criar_lavanderia, listar_lavanderias, contar_lavanderias
from modelos.usuario import criar_administrador_predio, contar_usuarios

class ControladorPlataforma:

    def cadastrar_lavanderia(self, nome: str, endereco: str, id_adm_predio: int = None):
        if not nome:
            raise ValueError("O nome da lavanderia é obrigatório.")
        lav = Lavanderia(None, id_adm_predio, nome, endereco, None, 0)
        return criar_lavanderia(lav)

    def cadastrar_admin_predio(self, nome: str, email: str, senha: str, telefone: str, id_lavanderia: int):
        if not all([nome, email, senha, telefone, id_lavanderia]):
            raise ValueError("Todos os campos são obrigatórios.")
        return criar_administrador_predio(nome, email, senha, telefone, id_lavanderia)

    def listar_lavanderias(self):
        return listar_lavanderias()

    def obter_estatisticas(self):
        return {
            "usuarios": contar_usuarios(),
            "lavanderias": contar_lavanderias()
        }
