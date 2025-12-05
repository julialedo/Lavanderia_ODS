# Controller - controlador_usuario.py
# Responsável pelas validações, transformar dados para o model, decisões.

from typing import Optional, Tuple
from modelos.lavanderia import listar_lavanderias
from modelos.usuario import (
    autenticar_usuario, editar_usuario, criar_morador, 
    verificar_email_existente, listar_moradores_pendentes_lavanderia,
    aprovar_conta_morador, rejeitar_conta_morador, criar_administrador_predio,
    contar_usuarios, obter_usuario_por_id, obter_lavanderias_por_usuario
)
import re

class ControladorUsuario:
    
    # Auntenticar Login: OK
    def login(self, email: str, senha: str) -> dict:
        if not email or not senha:  
            raise ValueError("Email e senha são obrigatórios!")   

        usuario = autenticar_usuario(email, senha)

        if not usuario:    
            raise ValueError("Usuário não encontrado! Verifique o e-mail e a senha.")
        if usuario["status_conta"] != "ativa":   
            raise ValueError("Conta inativa. Contate o administrador do seu prédio.")
        
        return usuario


    # Editar Perfi:
    def editar_perfil(self, id_usuario: int, nome: str, email: str, telefone: str, 
                     senha_atual: str, nova_senha: Optional[str] = None) -> bool:
        """Edita perfil do usuário"""
        # 1. Validação dos campos obrigatórios
        if not all([id_usuario, nome, email, telefone, senha_atual]):
            raise ValueError("Todos os campos obrigatórios (Nome, Email, Telefone, Senha Atual) devem ser preenchidos!")

        # 2. Re-autenticação/Validação da Senha Atual
        usuario_db = autenticar_usuario(email, senha_atual)
        
        if not usuario_db or usuario_db["id_usuario"] != id_usuario: 
            raise ValueError("Senha atual incorreta ou usuário não encontrado.")
             
        # 3. Validação de Nova Senha (se fornecida)
        if nova_senha and len(nova_senha) < 6:
             raise ValueError("A nova senha deve ter pelo menos 6 caracteres.")
             
        # 4. Chama o Model para atualizar
        ok = editar_usuario(id_usuario, nome, email, telefone, nova_senha)
        
        if not ok:
            raise Exception("Não foi possível atualizar as informações. Verifique os dados.")
            
        return True


    # Validação de Email: OK
    def validar_email(self, email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None


    # Validação de Telefone: OK
    def validar_telefone(self, telefone: str) -> bool:
        padrao = r'^(\+55\s?)?(\(?\d{2}\)?\s?)?\d{4,5}-?\d{4}$'
        return re.match(padrao, telefone) is not None
     

    # Cadastrar Morador que se inscreveu: OK
    def cadastrar_morador(self, nome: str, email: str, senha: str, telefone: str, id_lavanderia: int) -> Tuple[bool, str]:
        try:
            # Validações de campos obrigatórios:
            if not all([nome, email, senha, telefone]):
                raise ValueError("Todos os campos são obrigatórios!")
            
            # Verificar se foi adicionado uma lavanderia
            if id_lavanderia is None:
                raise ValueError("Por favor, selecione uma lavanderia.")
        
            # Validação de telefone:
            if not self.validar_telefone(telefone):
                raise ValueError("Telefone inválido! Use oformato como (XX) XXXXXXXXX")
            
            # Validação de email:
            if not self.validar_email(email):
                raise ValueError("Email inválido!")
                        
            # Validação de tamanho da senha:
            if len(senha) < 6:
                raise ValueError("A senha deve ter pelo menos 6 caracteres")
            
            # Verificar se email já existe:
            if verificar_email_existente((email,)):
                raise ValueError("Email já cadastrado no sistema")
            
            # Criar morador (status 'inativa')
            novo_id = criar_morador(nome, email, senha, telefone, id_lavanderia)
            
            return True, f"Cadastro realizado com sucesso! Aguarde aprovação do administrador."
            
        except Exception as e:
            return False, str(e)


    # Cadastrar novo adm_predio: OK+-
    def criar_administrador_predio(self, nome: str, email: str, senha: str, 
                                  telefone: str, id_lavanderia: int) -> Tuple[bool, str]:
        try:
            if not all([nome, email, senha, telefone]):
                raise ValueError("Todos os campos são obrigatórios!")
            
            if not self.validar_email(email):
                raise ValueError("Email inválido!")
            
            if len(senha) < 6:
                raise ValueError("A senha deve ter pelo menos 6 caracteres")
            
            if verificar_email_existente(email):
                raise ValueError("Email já cadastrado no sistema")
            
            novo_id = criar_administrador_predio(nome, email, senha, telefone, id_lavanderia)
            
            return True, f"Administrador criado com sucesso! ID: {novo_id}"
            
        except Exception as e:
            return False, str(e)


    # Listar moradores pendentes (para serem aceitos na lavanderia pelo adm): OK
    def listar_moradores_pendentes(self, id_lavanderia: int) -> list:
        try:
            return listar_moradores_pendentes_lavanderia(id_lavanderia)
        except Exception as e:
            raise ValueError(f"Erro ao listar moradores pendentes: {str(e)}")


    # Aprovar moradores: OK
    def aprovar_morador(self, id_usuario: int) -> bool:
        try:
            sucesso = aprovar_conta_morador(id_usuario)
            if not sucesso:
                raise ValueError("Morador não encontrado ou já aprovado")
            return True
        except Exception as e:
            raise ValueError(f"Erro ao aprovar morador: {str(e)}")


    # Rejeitar moradores: OK
    def rejeitar_morador(self, id_usuario: int) -> bool:
        try:
            sucesso = rejeitar_conta_morador(id_usuario)
            if not sucesso:
                raise ValueError("Morador não encontrado")
            return True
        except Exception as e:
            raise ValueError(f"Erro ao rejeitar morador: {str(e)}")


    # Contar total de usuarios no sistema: OK
    def contar_usuarios(self) -> int:
        try:
            return contar_usuarios()
        except Exception as e:
            raise ValueError(f"Erro ao contar usuários: {str(e)}")

    
    # Buscar usuario por ID: OK
    def obter_usuario_por_id(self, usuario_id: int) -> Optional[dict]:
        try:
            return obter_usuario_por_id(usuario_id)
        except Exception as e:
            raise ValueError(f"Erro ao buscar usuário: {str(e)}")


    # ATENÇÃOBuscar usuario por email:
    def buscar_usuario_por_email(self, email: str) -> Optional[dict]:
        try:
            # ATENÇÃO!!!! Esta função precisaria ser implementada no modelo
            # Por enquanto retornamos None
            return None
        except Exception as e:
            raise ValueError(f"Erro ao buscar usuário: {str(e)}")


    # Listar lavanderias cadastradas: OK
    def listar_lavanderias(self):
        return listar_lavanderias()
    

    # Obter lavanderias por usuario:
    def obter_lavanderias_usuario(self, id_usuario: int) -> list:

        if not id_usuario or not isinstance(id_usuario, int):
            # Validação básica de entrada
            print("⚠️ ID de usuário não fornecido.")
            return []
            
        try:
            lista_ids = obter_lavanderias_por_usuario(id_usuario)            
            if not lista_ids:
                print(f"Usuário ID {id_usuario} não está associado a nenhuma lavanderia.")
            return lista_ids
            
        except Exception as e:
            print(f"❌ Erro no controlador ao buscar lavanderias: {e}")
            return []