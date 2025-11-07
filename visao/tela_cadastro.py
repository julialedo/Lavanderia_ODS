# visao/tela_cadastro.py
import streamlit as st
from banco_de_dados.conexao_bd import conectar
from controladores.controlador_usuario import ControladorUsuario

controlador_usuario = ControladorUsuario()

def listar_lavanderias_ativas():
    """Lista lavanderias do banco de dados"""
    sql = "SELECT id_lavanderia, nome_lavanderia FROM lavanderia WHERE status_lavanderia = 'ativa'"
    conn = conectar()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql)
        lavanderias = cur.fetchall()
        cur.close()
        return lavanderias
    except Exception as e:
        print(f"Erro ao buscar lavanderias: {e}")
        return []
    finally:
        conn.close()

def tela_cadastro():
    st.title("📝 Cadastro de Morador")
    st.markdown("---")
    st.info("Preencha os dados abaixo para se cadastrar no sistema de lavanderia")
    
    with st.form("form_cadastro"):
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input("Nome Completo*")
            email = st.text_input("Email*")
        
        with col2:
            telefone = st.text_input("Telefone*")
            lavanderia_id = st.selectbox(
                "Lavanderia*",
                options=[1, 2, 3],
                format_func=lambda x: f"Lavanderia {x}"
            )
        
        senha = st.text_input("Senha*", type="password")
        confirmar_senha = st.text_input("Confirmar Senha*", type="password")
        
        st.caption("* Campos obrigatórios")
        
        if st.form_submit_button("📝 Cadastrar", use_container_width=True):
            # Validações no frontend
            if not all([nome, email, telefone, senha]):
                st.error("Por favor, preencha todos os campos obrigatórios!")
                return
            
            if senha != confirmar_senha:
                st.error("As senhas não coincidem!")
                return
            
            if len(senha) < 6:
                st.error("A senha deve ter pelo menos 6 caracteres!")
                return
            
            # Tentar cadastrar
            sucesso, mensagem = controlador_usuario.cadastrar_morador(
                nome=nome,
                email=email,
                senha=senha,
                telefone=telefone,
                id_lavanderia=lavanderia_id
            )
            
            if sucesso:
                st.success(mensagem)
                st.balloons()
                if st.button("🔐 Fazer Login"):
                    st.session_state["mostrar_cadastro"] = False
                    st.rerun()
            else:
                st.error(f"Erro no cadastro: {mensagem}")
