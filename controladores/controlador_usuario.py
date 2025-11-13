# Controller - controlador_usuario.py
# Responsável pelas validações, transformar dados para o model, decisões.

from typing import Optional, Tuple
from modelos.usuario import (
    autenticar_usuario, editar_usuario, criar_morador, 
    verificar_email_existente, listar_moradores_pendentes_por_lavanderia,
    aprovar_conta_morador, rejeitar_conta_morador, criar_administrador_predio,
    contar_usuarios, obter_usuario_por_id, obter_lavanderia_usuario_db
)
import re

class ControladorUsuario:
    
    # AUTENTICAR LOGIN
    def login(self, email: str, senha: str) -> dict:
        """Autentica usuário no sistema"""
        if not email or not senha:  
            raise ValueError("Email e senha são obrigatórios!")   

        usuario = autenticar_usuario(email, senha)

        if not usuario:    
            raise ValueError("Usuário não encontrado! Verifique o e-mail e a senha.")
        if usuario["status_conta"] != "ativa":   
            raise ValueError("Conta inativa. Contate o administrador.")
        
        return usuario

    # EDITAR PERFIL
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

    # CADASTRAR MORADOR
    def cadastrar_morador(self, nome: str, email: str, senha: str, telefone: str, 
                         id_lavanderia: int) -> Tuple[bool, str]:
        """Cadastra novo morador (status inativa)"""
        try:
            # 1. Validações básicas
            if not all([nome, email, senha, telefone]):
                raise ValueError("Todos os campos são obrigatórios!")
            
            # 2. Validação de email
            if not self.validar_email(email):
                raise ValueError("Email inválido!")
            
            # 3. Validação de senha
            if len(senha) < 6:
                raise ValueError("A senha deve ter pelo menos 6 caracteres")
            
            # 4. Verificar se email já existe
            if verificar_email_existente(email):
                raise ValueError("Email já cadastrado no sistema")
            
            # 5. Criar morador (status 'inativa')
            novo_id = criar_morador(nome, email, senha, telefone, id_lavanderia)
            
            return True, f"Cadastro realizado com sucesso! ID: {novo_id}. Aguarde aprovação do administrador."
            
        except Exception as e:
            return False, str(e)

    # CRIAR ADMINISTRADOR DO PRÉDIO
    def criar_administrador_predio(self, nome: str, email: str, senha: str, 
                                  telefone: str, id_lavanderia: int) -> Tuple[bool, str]:
        """Cria novo administrador do prédio"""
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

    # LISTAR MORADORES PENDENTES
    def listar_moradores_pendentes(self, id_lavanderia: int) -> list:
        """Lista moradores aguardando aprovação"""
        try:
            return listar_moradores_pendentes_por_lavanderia(id_lavanderia)
        except Exception as e:
            raise ValueError(f"Erro ao listar moradores pendentes: {str(e)}")

    # APROVAR MORADOR
    def aprovar_morador(self, id_usuario: int) -> bool:
        """Aprova conta de morador"""
        try:
            sucesso = aprovar_conta_morador(id_usuario)
            if not sucesso:
                raise ValueError("Morador não encontrado ou já aprovado")
            return True
        except Exception as e:
            raise ValueError(f"Erro ao aprovar morador: {str(e)}")

    # REJEITAR MORADOR
    def rejeitar_morador(self, id_usuario: int) -> bool:
        """Rejeita conta de morador"""
        try:
            sucesso = rejeitar_conta_morador(id_usuario)
            if not sucesso:
                raise ValueError("Morador não encontrado")
            return True
        except Exception as e:
            raise ValueError(f"Erro ao rejeitar morador: {str(e)}")

    # CONTAR USUÁRIOS
    def contar_usuarios(self) -> int:
        """Retorna o total de usuários no sistema"""
        try:
            return contar_usuarios()
        except Exception as e:
            raise ValueError(f"Erro ao contar usuários: {str(e)}")

    # VALIDAÇÃO DE EMAIL
    def validar_email(self, email: str) -> bool:
        """Valida formato de email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    # BUSCAR USUÁRIO POR EMAIL
    def buscar_usuario_por_email(self, email: str) -> Optional[dict]:
        """Busca usuário por email"""
        try:
            # Esta função precisaria ser implementada no modelo
            # Por enquanto retornamos None
            return None
        except Exception as e:
            raise ValueError(f"Erro ao buscar usuário: {str(e)}")

    # OBTER USUÁRIO POR ID
    def obter_usuario_por_id(self, usuario_id: int) -> Optional[dict]:
        """Obtém dados completos do usuário por ID"""
        try:
            return obter_usuario_por_id(usuario_id)
        except Exception as e:
            raise ValueError(f"Erro ao buscar usuário: {str(e)}")

    # OBTER LAVANDERIA DO USUÁRIO
    def obter_lavanderia_usuario(self, usuario_id: int) -> Optional[int]:
        """Obtém o ID da lavanderia associada ao usuário"""
        try:
            return obter_lavanderia_usuario_db(usuario_id)
        except Exception as e:
            print(f"Erro ao obter lavanderia do usuário: {e}")
            return None
