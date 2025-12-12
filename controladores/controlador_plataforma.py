# Controller - controlador_plataforma.py - O adm_plataforma que tem acesso a estas funcionalidades.
# Responsável pelas validações, transformar dados para o model, decisões.
# Não faz acesso direto ao banco, chama funções do Model. Retorna resultados para a View.
# Aqui entra as regras de negócio do tipo "regra de validação" que controla o fluxo da aplicação (ex: verificar se todos os campos obrigatórios foram preenchidos pelo usuario).

from modelos.lavanderia import Lavanderia, criar_lavanderia, listar_lavanderias, retornar_lavanderia_por_id, atualizar_adm_lavanderia, contar_lavanderias, excluir_lavanderia_por_id, remover_adm_lavanderia
from modelos.usuario import criar_administrador_predio, contar_usuarios, contar_usuarios_por_tipo, desassociar_usuarios_da_lavanderia
from modelos.maquina import contar_maquinas_por_lavanderia, contar_maquinas
from modelos.reserva import contar_reservas_hoje, lavanderias_mais_ativas

class ControladorPlataforma:

    # Cadastrar Lavanderia: OK
    def cadastrar_lavanderia(self, nome: str, endereco: str):
        lav = Lavanderia(None, None, nome, endereco, None)
        return criar_lavanderia(lav)


    # Cadastrar Administrador do Predio: OK
    def cadastrar_admin_predio(self, nome: str, email: str, senha: str, telefone: str, id_lavanderia: int):
        novo_adm = criar_administrador_predio(nome, email, senha, telefone, id_lavanderia)
        if not novo_adm:
            return None
        atualizar_adm_lavanderia(id_lavanderia, novo_adm)
        return novo_adm


    # Listar lavanderias cadastradas: OK
    def listar_lavanderias(self):
        return listar_lavanderias()


    # Contar maquinas por lavanderia: OK
    def contar_maquinas(self, id_lavanderia: int):
        return contar_maquinas_por_lavanderia(id_lavanderia)


   # Obter lavanderia por ID: OK
    def obter_lavanderia_por_id(self, lavanderia_id: int):
        return retornar_lavanderia_por_id(lavanderia_id)
    

    # Gerar estatisticas e relatorios da plataforma: OK
    def obter_estatisticas(self):
        return {
            "usuarios": contar_usuarios(),
            "lavanderias": contar_lavanderias(),
            "maquinas": contar_maquinas(),
            "reservas_hoje": contar_reservas_hoje(),
            "tipos_usuarios": contar_usuarios_por_tipo(),
            "lavanderias_ativas": lavanderias_mais_ativas()
        }
    

    # Excluir Lavanderia e usuarios associados a ela: OK
    def excluir_lavanderia_e_dependentes(self, id_lavanderia: int) -> bool:
        lavanderia_excluida = excluir_lavanderia_por_id(id_lavanderia)
        if lavanderia_excluida:
            desassociar_usuarios_da_lavanderia(id_lavanderia)
        return lavanderia_excluida
    

    # Remover adm de uma lavanderia: OK
    def remover_administrador_lavanderia(self, id_lavanderia: int, id_adm_predio: int) -> bool:
        return remover_adm_lavanderia(id_lavanderia, id_adm_predio)
