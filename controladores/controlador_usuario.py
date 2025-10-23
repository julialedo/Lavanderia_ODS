# Controller - controlador_usuario.py
# Responsável pelas validações, transformar dados para o model, decisões.
# Não faz acesso direto ao banco, chama funções do Model. Retorna resultados para a View.
# Aqui entra as regras de negócio do tipo "regra de validação" que controla o fluxo da aplicação (ex: verificar se todos os campos obrigatórios foram preenchidos pelo usuario).

from typing import Optional
from modelos.usuario import autenticar_usuario, editar_usuario


class ControladorUsuario:
    
    # Autenticar Login:
    def login(self, email: str, senha: str):
        # ... código do login ...
        if not email or not senha:  
            raise ValueError("Email e senha são obrigatórios!")   

        usuario = autenticar_usuario(email, senha) #chama autenticação no model

        if not usuario:    
            raise ValueError("Usuário não encontrado! Verifique o e-mail e a senha.")
        if usuario["status_conta"] !=   "ativa":   
            raise ValueError("Conta inativa. Contate o administrador.")
        
        return usuario  #retorna o usuario 

    # Editar Perfil:
    def editar_perfil(self, id_usuario: int, nome: str, email: str, telefone: str, senha_atual: str, nova_senha: Optional[str] = None):
        
        # 1. Validação dos campos obrigatórios
        if not all([id_usuario, nome, email, telefone, senha_atual]):
            raise ValueError("Todos os campos obrigatórios (Nome, Email, Telefone, Senha Atual) devem ser preenchidos!")

        # 2. Re-autenticação/Validação da Senha Atual
        usuario_db = autenticar_usuario(email, senha_atual) # Tenta autenticar com o email e a senha atual
        
        if not usuario_db or usuario_db["id_usuario"] != id_usuario: 
            # Verifica se a autenticação falhou ou se o ID retornado não é o do usuário logado (segurança extra)
            raise ValueError("Senha atual incorreta ou usuário não encontrado.")
            
        # 3. Validação de Nova Senha (se fornecida)
        if nova_senha and len(nova_senha) < 6: # Exemplo simples de validação de senha
             raise ValueError("A nova senha deve ter pelo menos 6 caracteres.")
             
        # 4. Chama o Model para atualizar
        # Nota: O Model (editar_usuario) deve cuidar de não atualizar o email 
        # para um email já existente, se for uma regra de negócio, ou isso 
        # deve ser checado aqui. Para este exemplo, vamos assumir que o Model 
        # lida com a atualização simples e você pode adicionar a checagem de 
        # e-mail duplicado posteriormente no Model se necessário.
        
        ok = editar_usuario(id_usuario, nome, email, telefone, nova_senha)
        
        if not ok:
            # Pode indicar que não houve alteração ou um erro no banco (menos provável se não for um erro de Exception)
            raise Exception("Não foi possível atualizar as informações. Verifique os dados.")
            
        # Se a atualização for bem-sucedida e a senha foi alterada, é recomendado 
        # forçar o logout ou solicitar novo login por segurança. 
        # Para simplificar, neste exemplo, apenas retornaremos o sucesso.
        
        return True # Indica sucesso na edição
