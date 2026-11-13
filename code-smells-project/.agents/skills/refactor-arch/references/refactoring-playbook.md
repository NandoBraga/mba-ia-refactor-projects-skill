# Playbook de refatoração

Exemplos ilustrativos. Adapte nomes, versões, tratamento de erros e convenções ao projeto. Preserve contratos externos e prefira mudanças pequenas.

## 1. Segredo hardcoded → configuração externa

Antes (Python): `app.secret_key = "abc123"`

Depois: `app.secret_key = os.environ["APP_SECRET_KEY"]` (carregue e valide configuração na inicialização; segredo real fica em secret manager/env, nunca no repositório).

## 2. SQL concatenado → query parametrizada

Antes: `db.execute(f"SELECT * FROM users WHERE id={user_id}")`

Depois: `db.execute("SELECT * FROM users WHERE id = ?", (user_id,))` (placeholder conforme driver).

## 3. Rota com regra de negócio → serviço/caso de uso

Antes: `@app.post('/orders')` calcula total e grava vários registros no handler.

Depois: `@app.post('/orders')` valida entrada e chama `create_order.execute(data)`; serviço calcula total e coordena persistência.

## 4. Acesso a dados no handler → repositório/model

Antes: `router.get('/users/:id', async (req,res) => { const u = await db.query('...'); res.json(u); })`

Depois: `router.get('/users/:id', async (req,res) => res.json(await usersController.get(req.params.id)))`; controller usa `userRepository.findById(id)`. Query parametrizada fica no repositório.

## 5. Estado global mutável → dependência por composição

Antes: `global.db = connect()` e módulos leem/escrevem em `global.db`.

Depois: `createApp({ userRepository })`; composição cria conexão e injeta dependência. Feche recursos no lifecycle da aplicação.

## 6. Erros copiados por rota → mapeamento central

Antes: cada rota retorna `res.status(500).send(err.stack)`.

Depois: rotas passam erro ao middleware; handler central mapeia erros conhecidos a respostas públicas seguras e registra detalhes redigidos.

## 7. Validação espalhada → validação na fronteira

Antes: `const title = req.body.title; await save(title)` sem verificar tipo/tamanho.

Depois: `const input = parseCreateTask(req.body)`; inválido gera erro 400 padronizado, e o caso de uso também preserva invariantes do domínio.

## 8. API deprecated → API suportada

Antes: uso de símbolo explicitamente marcado deprecated na versão instalada.

Depois: migre para o substituto indicado pelo fabricante (exemplo conceitual: callbacks obsoletos de uma biblioteca → API promise/async suportada), atualize chamadas e dependências compatíveis e cubra o comportamento. Confirme docs e versão antes; não faça substituição especulativa.

## 9. Query em loop / N+1 → busca em lote

Antes: `for user in users: load_orders(user.id)`.

Depois: `orders_by_user = load_orders_for_users([u.id for u in users])`; associe em memória ou use eager loading suportado pelo ORM.

## 10. Duplicação e valores mágicos → função coesa e constantes

Antes: várias rotas repetem o mesmo cálculo e `if retries > 7`.

Depois: extraia função de domínio reutilizável e nomeie `MAX_RETRIES = 7`; mantenha a regra em um único lugar e teste seus limites.
