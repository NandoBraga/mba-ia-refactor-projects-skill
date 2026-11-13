# Relatório de Auditoria Arquitetural — Projeto 3

- Projeto: `task-manager-api`
- Data: 2026-10-28
- Stack: Python; Flask 3.0.0; Flask-SQLAlchemy 3.1.1; Flask-CORS 4.0.0 (`requirements.txt`)
- Escopo: 13 arquivos de aplicação/configuração inspecionados (`app.py`, `database.py`, `seed.py`, três models, três route modules, serviço de notificações, helpers e requirements)
- Domínio: API Task Manager com usuários, tarefas, categorias e relatórios
- Arquitetura: separação parcial por `models/`, `routes/`, `services/` e `utils/`; porém rotas mantêm lógica de negócio, consultas e serialização.
- Banco: SQLite (`sqlite:///tasks.db` em `app.py:11`)
- Execução: `python app.py`; Flask inicia em `0.0.0.0:5000` com debug ligado.

## Resumo

| Severidade | Quantidade |
|---|---:|
| CRITICAL | 1 |
| HIGH | 3 |
| MEDIUM | 2 |
| LOW | 0 |
| **Total** | **6** |

## Findings

### [CRITICAL] Hash MD5 inadequado para senhas e campo secreto serializado
- Local: `models/user.py:16-32`
- Evidência: `to_dict()` inclui `password`; `set_password` e `check_password` usam MD5 direto, sem salt nem função de derivação para senha.
- Impacto: APIs que usam `to_dict()` podem revelar os hashes, que são rápidos de quebrar; senhas ficam expostas em respostas e em dumps.
- Recomendação: remover `password` de qualquer representação pública, migrar para hash moderno específico para senhas (com salt/fator de custo) e invalidar/atualizar credenciais existentes.

### [HIGH] Segredo de aplicação hardcoded e servidor de desenvolvimento exposto
- Local: `app.py:11-15`, `30-34`
- Evidência: `SECRET_KEY` é literal; CORS é ativado sem opções restritivas; execução usa `debug=True` e `host='0.0.0.0'`.
- Impacto: chave pode ser compartilhada no repositório; debug em interface exposta pode divulgar detalhes internos. CORS sem política explícita amplia origens permitidas conforme defaults da extensão.
- Recomendação: carregar chave secreta de configuração segura, restringir CORS às origens necessárias e executar com debug desligado em ambiente exposto.

### [HIGH] Token de autenticação é literal previsível e não representa sessão segura
- Local: `routes/user_routes.py:185-211`
- Evidência: login retorna `fake-jwt-token-` concatenado ao ID; não há assinatura, expiração nem validação associada a esse token no código inspecionado.
- Impacto: clientes podem tratar identificador previsível como credencial, sem garantia criptográfica de integridade ou prazo.
- Recomendação: usar mecanismo de sessão/token mantido por biblioteca compatível, assinado com segredo seguro, com expiração e validação em rotas protegidas; não denominar token simulado como JWT.

### [HIGH] Controllers/rotas concentram regras de domínio e acesso a dados
- Local: `routes/task_routes.py:85-223`, `240-299`; `routes/report_routes.py:12-101`; `routes/user_routes.py:42-90`
- Evidência: handlers fazem validação detalhada, consultas/commits ORM, cálculo de estatísticas e montagem de respostas diretamente.
- Impacto: regras ficam duplicadas entre endpoints e difíceis de testar sem contexto Flask/banco.
- Recomendação: manter rotas como fronteira HTTP fina, extrair casos de uso/serviços e centralizar validação/serialização de domínio com limites coesos.

### [MEDIUM] Padrões N+1 em listagens e relatórios
- Local: `routes/task_routes.py:14-57`; `routes/report_routes.py:53-68`, `157-165`; `routes/user_routes.py:10-25`
- Evidência: a listagem de tarefas consulta usuários/categorias por tarefa; relatórios consultam tarefas por usuário e contagem por categoria em loops; listagem de usuários acessa tarefas de cada usuário.
- Impacto: número de consultas cresce com os registros retornados.
- Recomendação: usar eager loading, agregações e consultas agrupadas com joins; paginar listagens extensas.

### [MEDIUM] Uso de `Query.get()` da API legada do SQLAlchemy
- Local: por exemplo, `routes/task_routes.py:67`, `routes/user_routes.py:29` e `routes/report_routes.py:105`
- Evidência: handlers chamam `Model.query.get(id)`. `Query.get()` é API legada em SQLAlchemy 2.x; o `requirements.txt` fixa Flask-SQLAlchemy 3.1.1, mas não fixa a versão transitiva de SQLAlchemy.
- Impacto: manutenção sobre interface legada e possível incompatibilidade futura; não foi confirmada a versão efetivamente instalada.
- Recomendação: confirmar a versão resolvida no ambiente e migrar para `db.session.get(Model, id)` conforme a versão suportada.

## APIs deprecated

A API legada `Query.get()` foi identificada; a versão exata de SQLAlchemy em uso não está travada no `requirements.txt`, então a severidade é MEDIUM e a compatibilidade deve ser conferida no ambiente resolvido antes da migração.

## Confirmação para refatorar

Fase 3 não iniciada. Aguardando confirmação explícita para modificar o código.