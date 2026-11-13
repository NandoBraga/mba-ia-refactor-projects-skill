# Modelo do relatório de auditoria

Grave como Markdown em `reports/audit-project-{1,2,3}.md` quando solicitado. Substitua os campos; não deixe exemplos como achados reais.

```markdown
# Relatório de Auditoria Arquitetural

- Projeto: <nome>
- Data: <AAAA-MM-DD>
- Stack: <linguagem/framework/versões e evidência>
- Escopo: <arquivos inspecionados / limites>
- Arquitetura: <descrição breve>
- Domínio: <domínio>

## Resumo

| Severidade | Quantidade |
|---|---:|
| CRITICAL | 0 |
| HIGH | 0 |
| MEDIUM | 0 |
| LOW | 0 |
| **Total** | **0** |

## Findings

### [<SEVERIDADE>] <padrão>
- Local: `caminho/arquivo.ext:<linha ou intervalo>`
- Evidência: <fato concreto; redigir segredos>
- Impacto: <efeito observado>
- Recomendação: <ação específica>
- Deprecated: <somente quando aplicável: API, versão, substituto e evidência>

## Pontos não confirmados
- <itens que dependem de ambiente/versão, ou “Nenhum”>

## Confirmação para refatorar
Fase 3 não iniciada. Aguardando confirmação explícita para modificar o código.
```

Ordene findings por severidade e depois por localização. Contagens precisam bater com os achados. Se nenhuma ocorrência existir, registre zero; nunca fabrique achados para atingir uma meta.
