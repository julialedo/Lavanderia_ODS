# Controller - controlador_relatorios.py - O adm do prédio que tem acesso a estas funcionalidades. 
# Responsável pelas validações, transformar dados para o model, decisões.
# Não faz acesso direto ao banco, chama funções do Model. Retorna resultados para a View.
# Aqui entra as regras de negócio do tipo "regra de validação" que controla o fluxo da aplicação (ex: verificar se todos os campos obrigatórios foram preenchidos pelo usuario).

from modelos.reserva import obter_reservas_por_lavanderia_e_periodo
from modelos.maquina import listar_maquinas_por_lavanderia

class ControladorRelatorio:

    # Gerar relatório de uso para uma lavanderia no período especificado: CONFIRMAR
    def gerar_relatorio_uso(self, id_lavanderia: int, data_inicial: str, data_final: str):
        if not id_lavanderia:
            raise ValueError("ID da lavanderia é obrigatório")
        
        if not data_inicial or not data_final:
            raise ValueError("Período é obrigatório")
        
        if data_final < data_inicial:
            raise ValueError("Data final não pode ser anterior à data inicial")

        # Buscar reservas no período
        reservas = obter_reservas_por_lavanderia_e_periodo(id_lavanderia, data_inicial, data_final)
        
        # Buscar máquinas da lavanderia
        maquinas = listar_maquinas_por_lavanderia(id_lavanderia)
        
        return {
            "reservas": reservas,
            "maquinas": maquinas,
            "periodo": {
                "inicio": data_inicial,
                "fim": data_final
            }
        }
