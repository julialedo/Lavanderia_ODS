# View - tela_cadastro.py
# Interface em Streamlit, recebe o input do usuário, chama o controller, mostra o feedback.

import streamlit as st
from banco_de_dados.conexao_bd import conectar
from controladores.controlador_usuario import ControladorUsuario

controlador_usuario = ControladorUsuario()


# Tela de cadastro
def tela_cadastro():
    st.title("📝 Cadastro de Morador")
    st.info("Preencha os dados abaixo para se cadastrar no sistema de lavanderia")
    
    lavanderias = controlador_usuario.listar_lavanderias()   #acessndo lista de lavanderias antes de iniciar o formulario
    opcoes = {lav.nome: lav.id_lavanderia for lav in lavanderias}
    
    with st.form("form_cadastro"):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome Completo*")
        with col2:
            telefone = st.text_input("Telefone*") 

        email = st.text_input("Email*")
       
        col1, col2 = st.columns(2)
        with col1:
            senha = st.text_input("Senha*", type="password")
        with col2:
            confirmar_senha = st.text_input("Confirmar Senha*", type="password")
        
        lavanderia_nome = st.selectbox(
                "Lavanderia*",
                options=list(opcoes.keys()),
                index=None, #para deixar seleção vaia
                placeholder="Selecione uma opção"
        )
        id_lavanderia = opcoes.get(lavanderia_nome)
        
        st.caption(" *Campos obrigatórios")
        
        if st.form_submit_button("📝 Cadastrar", use_container_width=True):
            
            # Validações no frontend
            if senha != confirmar_senha:
                st.error("As senhas não coincidem!")
                return
        
            # Fazer cadastro
            sucesso, mensagem = controlador_usuario.cadastrar_morador(
                nome=nome,
                email=email,
                senha=senha,
                telefone=telefone,
                id_lavanderia=id_lavanderia
            )
            if sucesso:
                st.success(mensagem)
                st.balloons()
            else:
                st.error(f"Erro no cadastro: {mensagem}")
