""" Controller controlador_maquina.py
Responsável pela lógica de negócio: validações, transformar dados para o model, decisões.
Não faz acesso direto ao banco, chama funções do Model. Retorna resultados para a View """

from modelos.maquina import Maquina, criar_maquina, atualizar_maquina, deletar_maquina, listar_maquinas_por_lavanderia, obter_maquina_por_id

class ControladorMaquina:

    # -- Cadastrar Maquinas:
    def cadastrar_maquina(self, id_lavanderia: int, codigo: str, tipo: str, capacidade: str, status: str = "livre"):
        if tipo not in ("lavadora", "secadora"):  #validação de tipo
            raise ValueError("Tipo inválido")
        #REGISTRAR LOG/AUDITORIA DE CADASTRO DE MAQUINA
        maquina = Maquina(id_maquina=None, id_lavanderia=id_lavanderia, codigo_maquina=codigo, tipo_maquina=tipo, status_maquina=status, capacidade=capacidade) #constroi objeto maquina
        new_id = criar_maquina(maquina) #chama criar maquina do modelo e recebe como retorno o id da maquina criada
        return new_id


    # -- Editar Máquinas:
    def editar_maquina(self, id_maquina: int, campos: dict):
        #VALIDAÇÃO DE SE FOR DEIXAR EM MANUTENÇÃO, AVISAR OS QUE TEM RESRVAS ATIVAS
        #REGISTRAR LOG/AUDITORIA
        maquina = obter_maquina_por_id(id_maquina)
        if not maquina:
            raise ValueError("Máquina não encontrada.")
        if "tipo_maquina" in campos and campos["tipo_maquina"] not in ("lavadora", "secadora"):
            raise ValueError("Tipo de máquina inválido.")
        if "status_maquina" in campos and campos["status_maquina"] not in ("livre", "em_uso", "manutencao"):
            raise ValueError("Status de máquina inválido.")
        ok = atualizar_maquina(id_maquina, campos) #chama atualizar maquina do modelo
        return ok


    # -- Remover Máquina
    def remover_maquina(self, id_maquina: int):
        #VALIDAÇÕES VERIFICAR SE TEM RESERVAS PARA A MAQUINA E AVISAR OS MORADORES
        #REGISTRAR LOG/AUDITORIA DA EXCLUSÃO
        return deletar_maquina(id_maquina) #Chama deletar maquina do modelo


    # -- Listar Máquinas por lavanderia
    def listar_por_lavanderia(self, id_lavanderia: int):
        return listar_maquinas_por_lavanderia(id_lavanderia)


    # -- Obter Máquina por Id
    def obter(self, id_maquina: int):
        return obter_maquina_por_id(id_maquina)
