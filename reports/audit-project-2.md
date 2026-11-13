# Relatório de Auditoria Arquitetural — Projeto 2

- Projeto: `ecommerce-api-legacy`
- Data: 2026-10-28
- Stack: Node.js (runtime não especificado), Express `^4.18.2`, `sqlite3` `^5.1.6` (`package.json`)
- Escopo: 4 arquivos de aplicação/configuração inspecionados (`package.json`, `src/app.js`, `src/AppManager.js`, `src/utils.js`)
- Domínio: API LMS com checkout, matrículas e relatório financeiro
- Arquitetura: inicialização em `app.js`; classe `AppManager` reúne schema/seeds, rotas, checkout, relatórios e exclusão; utilitários contêm configuração e estado global.
- Banco: SQLite em memória (`src/AppManager.js:7`); dados reiniciam a cada processo.
- Execução: `npm start` (`node src/app.js`); porta 3000 definida em `src/utils.js:6`.

## Resumo

| Severidade | Quantidade |
|---|---:|
| CRITICAL | 2 |
| HIGH | 2 |
| MEDIUM | 2 |
| LOW | 0 |
| **Total** | **6** |

## Findings

### [CRITICAL] Segredos de produção e chave de pagamento hardcoded
- Local: `src/utils.js:1-7`
- Evidência: configuração inclui credencial de banco, senha, chave de gateway com prefixo `pk_live_` e usuário SMTP como literais.
- Impacto: caso sejam credenciais reais, o histórico do repositório permite acesso indevido a serviços; a chave também é usada e registrada no fluxo de checkout.
- Recomendação: tratar como comprometidas se reais, rotacionar fora deste código e carregar segredos de secret manager/configuração segura. O relatório omite os valores.

### [CRITICAL] Dados de cartão e chave de gateway registrados em log
- Local: `src/AppManager.js:43-46`
- Evidência: `console.log` interpola o valor recebido em `card` e `config.paymentGatewayKey`.
- Impacto: cartão e segredo de integração podem permanecer em logs acessíveis por mais tempo e a mais pessoas que o fluxo autorizado.
- Recomendação: remover dados de cartão e segredos dos logs; usar identificadores/tokenização do provedor e logging redigido.

### [HIGH] Checkout aceita qualquer senha e usa pseudo-hash inseguro
- Local: `src/AppManager.js:29-35`, `66-70`; `src/utils.js:17-23`
- Evidência: senha `p` não é exigida na validação; quando ausente, recebe senha padrão; `badCrypto` repete Base64 e trunca o resultado, que não é algoritmo de hash de senha.
- Impacto: criação de conta com credencial previsível e armazenamento resistente a ataque muito fraco; usuário existente também é selecionado somente por e-mail sem verificar senha.
- Recomendação: exigir autenticação/credencial válida para contas existentes; usar hash próprio para senha com salt e fator de custo (biblioteca adequada), e eliminar senha padrão.

### [HIGH] Relatório administrativo sem proteção de acesso
- Local: `src/AppManager.js:80-129`
- Evidência: `GET /api/admin/financial-report` retorna receitas e estudantes e não verifica autenticação nem papel administrativo.
- Impacto: informação financeira e dados de alunos ficam expostos a qualquer cliente com acesso à API.
- Recomendação: exigir autenticação e autorização administrativa antes de consultar e serializar o relatório.

### [MEDIUM] Consultas N+1 no relatório financeiro
- Local: `src/AppManager.js:89-124`
- Evidência: consulta matrículas por curso e, dentro do loop de matrículas, consulta usuário e pagamento separadamente.
- Impacto: consultas crescem com a quantidade de cursos e matrículas, degradando a resposta.
- Recomendação: buscar dados relacionados em lotes ou com JOIN e montar o relatório a partir dos resultados.

### [MEDIUM] `AppManager` concentra composição, persistência e lógica HTTP
- Local: `src/AppManager.js:4-138`
- Evidência: a classe inicializa banco e seeds, define schema e registra handlers com regras de checkout, pagamentos e relatórios.
- Impacto: responsabilidades não podem ser testadas/alteradas isoladamente e erros de fluxo se misturam ao transporte.
- Recomendação: separar composição e conexão, rotas/controllers e serviços de checkout/relatório; manter transações para matrícula e pagamento.

## APIs deprecated

Nenhuma API deprecated foi confirmada nos arquivos inspecionados. O `package.json` usa ranges (`^`) e não foi feita resolução/consulta à versão efetivamente instalada; qualquer migração deve confirmar a versão travada em `package-lock.json` e a documentação correspondente.

## Confirmação para refatorar

Fase 3 não iniciada. Aguardando confirmação explícita para modificar o código.