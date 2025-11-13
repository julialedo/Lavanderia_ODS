# Controller - controlador_plataforma.py - O adm_plataforma que tem acesso a estas funcionalidades.
# Responsável pelas validações, transformar dados para o model, decisões.
# Não faz acesso direto ao banco, chama funções do Model. Retorna resultados para a View.
# Aqui entra as regras de negócio do tipo "regra de validação" que controla o fluxo da aplicação (ex: verificar se todos os campos obrigatórios foram preenchidos pelo usuario).

from modelos.lavanderia import Lavanderia, criar_lavanderia, listar_lavanderias, contar_lavanderias, obter_lavanderia_por_id
from modelos.usuario import criar_administrador_predio, contar_usuarios

class ControladorPlataforma:

    # Cadastrar lavanderia:
    def cadastrar_lavanderia(self, nome: str, endereco: str, id_adm_predio: int = None):
        if not nome:
            raise ValueError("O nome da lavanderia é obrigatório.")
        lav = Lavanderia(None, id_adm_predio, nome, endereco, None, 0)
        return criar_lavanderia(lav)


    # Cadastrar Administrador do Predio:
    def cadastrar_admin_predio(self, nome: str, email: str, senha: str, telefone: str, id_lavanderia: int):
        if not all([nome, email, senha, telefone, id_lavanderia]):
            raise ValueError("Todos os campos são obrigatórios.")
        return criar_administrador_predio(nome, email, senha, telefone, id_lavanderia)


    # Listar lavanderias cadastradas:
    def listar_lavanderias(self):
        return listar_lavanderias()


    # Gerar estatisticas e relatorios da plataforma:
    def obter_estatisticas(self):
        return {
            "usuarios": contar_usuarios(),
            "lavanderias": contar_lavanderias()
        }

    # Obter lavanderia por ID
    def obter_lavanderia_por_id(self, lavanderia_id: int):
        """Obtém dados de uma lavanderia específica"""
        return obter_lavanderia_por_id(lavanderia_id)
