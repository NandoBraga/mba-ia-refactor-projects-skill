# Relatório de Auditoria Arquitetural — Projeto 3

- Projeto: `task-manager-api`
- Data: 2026-10-28
- Stack: Python; Flask 3.0.0; Flask-SQLAlchemy 3.1.1; Flask-CORS 4.0.0 (`requirements.txt`)
- Escopo: 13 arquivos de aplicação/configuração inspecionados (`app.py`, `database.py`, `seed.py`, três models, três route modules, serviço de notificações, helpers e requirements)
- Domínio: API Task Manager com usuários, tarefas, categorias e relatórios
- Arquitetura atual: separação parcial por `models/`, `routes/`, `services/` e `utils/`; a lógica de tarefas foi extraída para `TaskService`, mas relatórios e usuários ainda concentram consultas e regras em rotas.
- Banco: SQLite (`sqlite:///tasks.db` em `app.py:11`)
- Execução: `python app.py`; Flask inicia em `0.0.0.0:5000` com debug ligado.

## Resumo

| Severidade | Quantidade |
|---|---:|
| CRITICAL | 1 |
| HIGH | 3 |
| MEDIUM | 1 |
| LOW | 0 |
| **Total** | **5** |

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

### [HIGH] Corrigido — Rotas concentravam regras de domínio e acesso a dados
- Local corrigido: `routes/task_routes.py`; caso de uso extraído em `services/task_service.py`
- Evidência anterior: handlers faziam validação detalhada, consultas/commits ORM, cálculo de estatísticas e montagem de respostas diretamente.
- Evidência atual: o blueprint só lê parâmetros/payload, delega ao `TaskService` e traduz retornos/erros HTTP; não contém `db.session`, consultas `Task.query`, criação de entidades ou serialização de tarefas.
- Impacto resolvido: criação, consulta, atualização, busca e estatísticas ficam testáveis fora do contexto Flask e a validação/serialização está centralizada.
- Validação: compilação passou; `GET /health`, `GET /tasks`, `POST /tasks`, `GET /tasks/<id>`, `PUT /tasks/<id>`, `GET /tasks/search`, `GET /tasks/stats` e `DELETE /tasks/<id>` retornaram sucesso em banco temporário.
- Recomendação restante: aplicar o mesmo limite a rotas de usuários e relatórios para remover os outros concentradores.

### [MEDIUM] Padrões N+1 em listagens e relatórios
- Local: `routes/task_routes.py:14-57`; `routes/report_routes.py:53-68`, `157-165`; `routes/user_routes.py:10-25`
- Evidência: a listagem de tarefas consulta usuários/categorias por tarefa; relatórios consultam tarefas por usuário e contagem por categoria em loops; listagem de usuários acessa tarefas de cada usuário.
- Impacto: número de consultas cresce com os registros retornados.
- Recomendação: usar eager loading, agregações e consultas agrupadas com joins; paginar listagens extensas.

## APIs deprecated

A API legada `Query.get()` foi identificada; a versão exata de SQLAlchemy em uso não está travada no `requirements.txt`, então a severidade é MEDIUM e a compatibilidade deve ser conferida no ambiente resolvido antes da migração.

## Fase 3 — Reexecutada

- Playbook reforçado com padrão Flask: rota fina → `service/caso de uso`.
- Criado `services/task_service.py` para validação, persistência, busca, estatísticas e serialização de tarefas.
- `routes/task_routes.py` foi reduzido a leitura HTTP e tradução de respostas/erros.
- Compilação passou para `routes/task_routes.py` e `services/task_service.py`.
- Validados em banco temporário: `GET /health`, `GET /tasks`, `POST /tasks`, `GET /tasks/<id>`, `PUT /tasks/<id>`, `GET /tasks/search`, `GET /tasks/stats` e `DELETE /tasks/<id>`.