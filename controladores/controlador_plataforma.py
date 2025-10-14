from modelos.plataforma import Plataforma
from modelos.usuario import Usuario

class ControladorPlataforma:
    def __init__(self):
        self.plataformas = []
        self._criar_dados_iniciais()
    
    def _criar_dados_iniciais(self):
        #Dados para teste
        plataforma_principal = Plataforma("PLAT001", "Lavanderia Central", "Rua Principal, 123")
        self.plataformas.append(plataforma_principal)
    

    def cadastrar_lavanderia(self, nome: str, endereco: str = "") -> Plataforma:
        novo_id = f"PLAT{len(self.plataformas) + 1:03d}"
        nova_plataforma = Plataforma(novo_id, nome, endereco)
        self.plataformas.append(nova_plataforma)
        return nova_plataforma
    
    def obter_estatisticas(self, usuarios: list) -> dict:
        total_usuarios = len(usuarios)
        total_admins = len([u for u in usuarios if u.tipo_perfil in ["admin_plataforma", "admin_lavanderia"]])
        
        return {
            "total_lavanderias": len(self.plataformas),
            "total_usuarios": total_usuarios,
            "total_administradores": total_admins,
            "lavanderia_principal": self.plataformas[0].nome_plataforma if self.plataformas else "Nenhuma"
        }
    
    def listar_lavanderias(self) -> list:
        return self.plataformas
    
    def obter_plataforma_por_id(self, id_plataforma: str) -> Plataforma:
        for plataforma in self.plataformas:
            if plataforma.id_plataforma == id_plataforma:
                return plataforma
        return None