---
name: refactor-arch
description: Audita uma codebase e, após autorização explícita, refatora sua arquitetura para MVC com validação da aplicação. Use quando solicitado a analisar/refatorar arquitetura, detectar code smells ou aplicar MVC.
---

# Refatoração arquitetural para MVC

Trabalhe na raiz do projeto solicitado. Adapte as decisões à stack detectada; nunca presuma Python, Flask, Node.js ou Express. Preserve comportamento e contratos públicos. Não edite arquivos durante as fases 1 e 2.

Consulte as referências nesta ordem, conforme necessário: `references/project-analysis.md`, `references/anti-pattern-catalog.md`, `references/report-template.md`, `references/mvc-guidelines.md`, `references/refactoring-playbook.md`.

## Fase 1 — Análise (somente leitura)

1. Liste arquivos de código e configuração relevantes, ignorando ambientes virtuais, dependências vendorizadas, build outputs, caches e `.git`.
2. Inspecione manifests, pontos de entrada, rotas, modelos, serviços, acesso a dados, testes e configurações. Determine linguagem, framework e versão quando comprovável, dependências, banco, domínio, comandos existentes e arquitetura atual.
3. Não infira fatos sem evidência. Marque itens não determinados como “não identificado”. Conte os arquivos efetivamente inspecionados.
4. Imprima um resumo claro: projeto, stack, dependências relevantes, domínio, banco, arquitetura e escopo analisado.

## Fase 2 — Auditoria (somente leitura)

1. Compare o código ao `anti-pattern-catalog.md`. Procure também APIs deprecated: confirme a obsolescência usando a versão instalada e fontes locais/documentação disponível; informe alternativa compatível. Não classifique API como deprecated só por ser antiga.
2. Para cada ocorrência real, informe severidade, título, arquivo e linha(s), evidência concreta, impacto e recomendação. Não invente linhas; se não puder determinar uma linha exata, informe o símbolo/trecho e diga isso.
3. Deduplicate causas iguais, separe ocorrências independentes e classifique por consequência observada. Gere o relatório conforme `report-template.md` em `reports/audit-project-{1,2,3}.md` somente se o usuário pediu relatório ou essa localização fizer parte da tarefa. Criar o relatório não autoriza mudanças no código.
4. Apresente a contagem por severidade e findings. Ao terminar, pause antes de alterar qualquer arquivo do projeto. Peça confirmação explícita para a Fase 3, indicando o escopo. Sem confirmação, encerre após a auditoria.

## Fase 3 — Refatoração (requer confirmação explícita)

Só prossiga após resposta afirmativa inequívoca à proposta de refatoração. Siga o `mvc-guidelines.md` e aplique padrões pertinentes do `refactoring-playbook.md`.

1. Planeje alterações mínimas, preserve rotas, payloads, status codes, regras de negócio, persistência e compatibilidade. Não altere schema/dados nem remova endpoints sem autorização específica.
2. Extraia configuração e segredos para configuração externa segura; nunca imprima valores secretos. Não adicione dependências sem necessidade e compatibilidade verificada.
3. Mantenha lógica de negócio fora de rotas/controllers quando houver benefício claro; adapte MVC ao framework e mantenha a estrutura existente quando já for adequada.
4. Faça alterações incrementais. Atualize imports, wiring e documentação de execução se necessário.
5. Valide usando os comandos e testes existentes: compile/syntax check, inicialização/boot da aplicação e verificações dos endpoints. Prefira testes automatizados e cliente HTTP já presentes; não invente sucesso quando serviço externo/segredo não está disponível. Não execute comandos destrutivos.
6. Relate arquivos alterados, decisões, comandos executados e resultados. Liste limitações de validação e findings que permaneceram.

## Regras de segurança e escopo

- Não exponha, copie para relatórios ou registre credenciais. Redija evidências sensíveis.
- Não modifique dados de produção ou recursos remotos.
- Se a confirmação não vier, não inicie mudanças; se a tarefa do usuário já autorizar diretamente a refatoração integral, essa instrução explícita vale como confirmação.
- Só declare um problema corrigido após conferir a alteração e validar o resultado pertinente.
