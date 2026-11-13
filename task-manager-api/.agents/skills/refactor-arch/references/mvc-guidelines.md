# Guidelines de arquitetura MVC

MVC é uma separação de responsabilidades, não uma exigência de diretórios idênticos em todas as linguagens.

## Model

Representa entidades, regras/invariantes do domínio e/ou persistência conforme as convenções do framework. Evite dependência de objetos HTTP, templates e variáveis globais. Separe repositório/DAO quando isso tornar consultas substituíveis ou testáveis; não crie camadas sem uso.

## View / Routes

Em API, rotas/handlers desempenham o papel de fronteira de entrada e saída: definem método/caminho, extraem e validam entrada, chamam o fluxo apropriado e traduzem resultado em status/payload. Templates e serializadores são views. Não concentre regra de negócio ou SQL diretamente na rota.

## Controller / caso de uso

Orquestra a operação: aplica regras de fluxo, coordena modelos/serviços/repositórios e devolve resultado. Deve ser testável sem servidor quando viável, não conhecer detalhes de transporte além do necessário. Em frameworks onde controller é o handler HTTP, mantenha-o fino e delegue domínio a serviços.

## Responsabilidades transversais

- Config/composição: monta dependências e inicializa a aplicação; segredo vem de mecanismo seguro externo.
- Middleware: autenticação/autorização, logging redigido, validação transversal e tratamento de erros.
- Serviço: regra de negócio/caso de uso coeso, sem acoplamento à resposta HTTP.
- Persistência: consultas parametrizadas e transações com escopo explícito.

## Direção e compatibilidade

Dependências apontam para dentro: rotas chamam casos de uso; casos de uso dependem de contratos de domínio/persistência. Preserve métodos, caminhos, formatos de payload, códigos HTTP, regras e esquema existentes. Estruture por domínio quando isso melhora localização do código. Projetos já bem separados devem receber apenas correções localizadas; evite reescrever ou criar abstrações vazias.
