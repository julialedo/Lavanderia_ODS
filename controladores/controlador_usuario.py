# Controller - controlador_usuario.py
# Responsável pelas validações, transformar dados para o model, decisões.
# Não faz acesso direto ao banco, chama funções do Model. Retorna resultados para a View.
# Aqui entra as regras de negócio do tipo "regra de validação" que controla o fluxo da aplicação (ex: verificar se todos os campos obrigatórios foram preenchidos pelo usuario).

from modelos.usuario import autenticar_usuario

class ControladorUsuario:
    
    # Autenticar Login:
    def login(self, email: str, senha: str):

        #valida se os campos estão preenchidos
        if not email or not senha:  
            raise ValueError("Email e senha são obrigatórios!")   

        usuario = autenticar_usuario(email, senha) #chama autenticação no model

        #valida se usuario foi encontrado e se a conta esta inativa
        if not usuario:    
            raise ValueError("Usuário não encontrado! Verifique o e-mail e a senha.")
        if usuario["status_conta"] !=   "ativa":   
            raise ValueError("Conta inativa. Contate o administrador.")
        
        return usuario  #retorna o usuario 