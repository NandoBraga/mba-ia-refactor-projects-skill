# Relatório de Auditoria Arquitetural — Projeto 1

- Projeto: `code-smells-project`
- Data: 2026-10-28
- Stack: Python; Flask 3.1.1; SQLite via `sqlite3` (requirements.txt e imports)
- Escopo: 5 arquivos de aplicação/configuração inspecionados (`app.py`, `controllers.py`, `models.py`, `database.py`, `requirements.txt`)
- Domínio: API de e-commerce (produtos, usuários, pedidos e vendas)
- Arquitetura: monolítica; rotas e inicialização em `app.py`, handlers em `controllers.py`, consultas e regras de quatro domínios concentradas em `models.py`, conexão global em `database.py`.
- Banco: SQLite, arquivo relativo `loja.db` (database.py:5)
- Execução documentada: `python app.py`; Flask escuta em `0.0.0.0:5000`.

## Resumo

| Severidade | Quantidade |
|---|---:|
| CRITICAL | 2 |
| HIGH | 2 |
| MEDIUM | 1 |
| LOW | 1 |
| **Total** | **6** |

## Findings

### [CRITICAL] Endpoint administrativo executa SQL arbitrário sem autenticação
- Local: `app.py:47-78`
- Evidência: `POST /admin/query` lê `sql` do JSON e passa o texto diretamente a `cursor.execute`; não há autenticação/autorização no handler. A rota também permite comandos de escrita e devolve mensagens de erro do banco.
- Impacto: um cliente que alcance a rota pode consultar, alterar ou apagar dados e explorar o banco.
- Recomendação: remover a rota de produção ou restringi-la a operação administrativa autenticada e autorizada; nunca aceitar SQL livre de uma requisição.

### [CRITICAL] SQL Injection nas consultas construídas por concatenação
- Local: `models.py:28`, `47-50`, `58-60`, `109-111`, `126-129`, `139-165`, `174`, `188-192`, `220`, `224`, `279-281`, `289-299`
- Evidência: valores de usuário são concatenados em SQL, incluindo busca, criação/atualização, login e status de pedido.
- Impacto: entradas com caracteres SQL podem alterar a consulta e comprometer dados ou autenticação.
- Recomendação: substituir por placeholders parametrizados do `sqlite3` em todas as instruções; validar tipos e limites na fronteira HTTP.

### [HIGH] Senhas em texto puro e incluídas nas respostas de usuários
- Local: `database.py:27-35`, `75-82`; `models.py:72-86`, `89-103`
- Evidência: coluna `senha` recebe valores diretamente; `get_todos_usuarios` e `get_usuario_por_id` incluem o campo `senha` nos objetos retornados.
- Impacto: listagem/consulta de usuários expõe credenciais e um vazamento do banco revela senhas utilizáveis.
- Recomendação: armazenar hash com algoritmo apropriado para senhas, migrar credenciais, e excluir sempre o campo secreto dos serializadores e respostas.

### [HIGH] Configuração sensível exposta e modo debug habilitado
- Local: `app.py:7-8`, `47-57`, `59-78`, `80-88`; `controllers.py:264-292`
- Evidência: há uma chave de sessão hardcoded; debug é ligado tanto na configuração quanto na chamada de `app.run`; `/health` devolve caminho local do banco, estado debug e valor da chave.
- Impacto: vazamento de chave e detalhes de infraestrutura; debug pode expor informações internas e aumentar a superfície de ataque.
- Recomendação: rotacionar a chave se for real, carregá-la de secret manager/configuração externa, remover campos sensíveis de health e desabilitar debug fora do desenvolvimento.

### [MEDIUM] Padrão N+1 ao montar pedidos
- Local: `models.py:171-201` e `203-233`
- Evidência: para cada pedido consulta itens, e para cada item faz outra consulta para obter o nome do produto.
- Impacto: quantidade de queries cresce com pedidos e itens, elevando latência e carga.
- Recomendação: buscar itens/produtos em lote com JOIN e agrupar os resultados em memória.

### [LOW] Responsabilidades de quatro domínios concentradas no módulo `models.py`
- Local: `models.py:4-314`
- Evidência: o mesmo módulo reúne consultas e transformação de produtos, usuários/autenticação, pedidos/estoque e relatório de vendas.
- Impacto: mudanças e testes ficam acoplados entre domínios.
- Recomendação: separar módulos/repositórios por domínio e mover fluxo de negócio para serviços/casos de uso, preservando os contratos atuais.

## APIs deprecated

Nenhuma API deprecated foi confirmada no escopo e nas versões declaradas. `sqlite3` é usado por meio da API padrão com versão fornecida pelo Python runtime, que não está especificado.

## Confirmação para refatorar

Fase 3 não iniciada. Aguardando confirmação explícita para modificar o código.