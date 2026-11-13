# Heurísticas de análise de projeto

## Escopo e evidências

Comece por manifests e configurações (`pyproject.toml`, `requirements*.txt`, `Pipfile`, `package.json`, lockfiles, arquivos de configuração do framework, Docker/compose, CI). Use versões travadas quando disponíveis; lockfile prevalece sobre intervalos do manifest. Inspecione código-fonte, entrypoints, rotas, dependências de dados e testes. Exclua `node_modules`, `.venv`, `venv`, `dist`, `build`, caches e `.git`. Não execute código desconhecido durante a análise.

Registre para cada conclusão uma evidência: arquivo de configuração, import, declaração ou uso. Diferencie dependência declarada de framework efetivamente usado. Não conte arquivos gerados como fonte.

## Detecção de stack

| Evidência | Indício |
|---|---|
| `.py`, `requirements.txt`, `pyproject.toml` | Python; verifique imports e versões |
| `from flask import Flask` / dependência Flask | Flask |
| `from fastapi import FastAPI` | FastAPI |
| `package.json`, `.js`, `.cjs`, `.mjs`, `.ts` | Node.js; veja `type`, scripts e lockfile |
| `require('express')` / `from 'express'` | Express |
| Prisma, Sequelize, SQLAlchemy, sqlite3 | ORM/driver; confirme no uso real |
| `sqlite3.connect`, DATABASE_URL, pool config | possível banco; identifique pelo driver/configuração |

Identifique linguagem/framework de templates ou frontend se estiverem presentes. A ausência de um framework deve ser registrada como tal.

## Mapeamento arquitetural

Siga uma requisição da rota até a resposta e a persistência. Registre diretórios e responsabilidades existentes:

- entrypoint/composição e inicialização;
- rotas/controllers/handlers;
- modelos/entidades e acesso a dados;
- serviços/regras de negócio;
- views/templates/serialização;
- middleware, autenticação, validação e tratamento de erros;
- configuração e integrações externas.

Descreva o que o código faz, não apenas o que os nomes sugerem. Aponte dependências direcionais e concentração de responsabilidades. Um app pequeno não precisa ganhar camadas vazias: priorize limites que removam acoplamento ou permitam testar regras.

## Inventário de domínio e execução

Use rotas, modelos, nomes de tabelas, README e payloads para identificar domínio. Use scripts e arquivos de deploy para detectar comando de boot e porta. Não assuma que banco/serviços externos estão disponíveis. Liste endpoints observados por método e caminho, sem disparar chamadas mutáveis na fase de análise.

## Resumo mínimo

Projeto; linguagem/framework/versões e evidências; dependências principais; banco/driver (ou desconhecido); domínio; arquitetura atual; entrypoint e comando de execução encontrados; quantidade de arquivos de código inspecionados e limites da inspeção.
