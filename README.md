# Lavanderias Coletivas

Sistema web para reserva e controle de uso de lavanderias compartilhadas em prédios e repúblicas. Projeto em grupo da disciplina de [nome da disciplina] ([universidade], 2025), pensado a partir dos Objetivos de Desenvolvimento Sustentável da ONU: uso racional de água e energia e organização de espaços coletivos.

## O que o sistema faz

Três perfis de acesso, cada um com sua área:

- **Morador**: reserva máquinas por horário, acompanha o ciclo em andamento, registra ocorrências (máquina com defeito, por exemplo) e recebe notificações.
- **Administrador do prédio**: aprova o cadastro de moradores, cadastra e edita máquinas, agenda manutenções preventivas, registra manutenções feitas e responde ocorrências.
- **Administrador da plataforma**: cadastra lavanderias, vincula administradores e acompanha estatísticas de uso.

## Arquitetura

O código segue o padrão MVC:

```
modelos/        acesso ao banco (SQL) e entidades
controladores/  regras de negócio e validações
visao/          telas em Streamlit
banco_de_dados/ conexão com o MySQL
app.py          ponto de entrada e controle de sessão
```

Tecnologias: Python, Streamlit, MySQL (hospedado no Railway).

## Como rodar

```bash
pip install -r requirements.txt
cp .env.example .env   # preencha com os dados do seu banco MySQL
streamlit run app.py
```

## Minha participação

Montei o protótipo inicial da interface e a estrutura de pastas MVC. Implementei o módulo de reservas (criação, conflito de horários e controle do ciclo das máquinas), o de notificações para moradores e administradores, e a parte de ocorrências.

## Equipe

Ana Julia Ledo, Gustavo Pedrosa, Marcus Lobo Felipe e Thalia Melo.

## Próximos passos

- Guardar as senhas com hash (bcrypt) em vez de texto puro
- Testes automatizados para as regras de reserva
