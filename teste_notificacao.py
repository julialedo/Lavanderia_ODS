# teste_notificacao.py

import sys
import os

# Adiciona os diretórios pai para que as importações funcionem
# Ex: controladores.controlador_notificacao
sys.path.append(os.path.dirname(os.path.abspath(__file__))) 

# Importa o Controlador
from controladores.controlador_notificacao import ControladorNotificacao 

# --- Configuração de Teste ---
ID_USUARIO_TESTE = 1 # ID do ADM/Morador que você garante ter notificações
controlador = ControladorNotificacao()

print("--- 🔔 Teste de Listagem de Notificações ---")
print(f"Tentando listar notificações para o ID de Usuário: {ID_USUARIO_TESTE}")

try:
    # Chama a função do controlador
    notificacoes = controlador.listar_notificacoes_do_usuario(ID_USUARIO_TESTE)

    if notificacoes:
        print("\n✅ SUCESSO! Notificações encontradas:")
        print(f"Total de notificações: {len(notificacoes)}")
        print("Detalhes da primeira notificação:")
        # Imprime a primeira notificação para verificar o formato
        print(notificacoes[0]) 
    else:
        # Se retornar vazio, mas você tem dados, o problema está na QUERY ou Conexão
        print("\n❌ FALHA NA BUSCA! O controlador retornou uma lista vazia.")
        print("Possíveis causas: Tabela vazia, ID_USUARIO incorreto, ou erro de conexão/query.")

except Exception as e:
    # Se ocorrer uma exceção (erro de sintaxe, conexão, etc.)
    print(f"\n🚨 ERRO CRÍTICO DURANTE O TESTE: {e}")
    
print("\n--- Fim do Teste ---")