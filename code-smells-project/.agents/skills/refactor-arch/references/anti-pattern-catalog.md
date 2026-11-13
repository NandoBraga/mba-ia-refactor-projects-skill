# Catálogo de anti-patterns

Severidade depende de evidência e impacto real. Registre arquivo e linha do código-fonte; não reporte padrões não encontrados. Uma ocorrência pode corresponder a mais de um padrão quando impactos forem distintos, sem duplicar o mesmo defeito.

| Padrão / severidade inicial | Sinais verificáveis | Impacto e orientação |
|---|---|---|
| Segredo hardcoded — CRITICAL | Senha, token, chave privada ou chave de sessão literal usada como credencial | Risco de comprometimento. Redigir valor, revogar/rotacionar fora do código e usar secret manager/env seguro. Não confundir chave pública ou placeholder. |
| Injeção SQL/command — CRITICAL | Entrada concatenada/interpolada em SQL ou comando shell executável | Injeção e acesso/execução indevida. Usar parâmetros/APIs seguras e validação contextual. |
| God class/module ou responsabilidade misturada — CRITICAL/HIGH | Um módulo mistura roteamento, regras, persistência e formatação; classe/método concentra fluxos desconexos | Mudança arriscada e difícil isolamento. Extrair limites coesos, preservar contrato. CRITICAL só para concentração extrema que causa impacto grave comprovável; caso contrário HIGH. |
| Lógica de negócio em rota/controller — HIGH | Handler contém regras, cálculos, loops de domínio ou várias operações de persistência | Testes e reutilização difíceis. Mover caso de uso para serviço/controller apropriado, deixando transporte fino. |
| Acoplamento forte / estado global mutável — HIGH | Dependências concretas construídas em vários pontos, singleton global mutável, estado compartilhado entre requisições | Testes frágeis, vazamento de estado ou concorrência. Introduzir composição/injeção simples e escopo adequado. |
| Autorização/validação ausente — CRITICAL/HIGH/MEDIUM | Endpoint sensível sem checagem de identidade/permissão ou dados não validados antes do uso | Escalar conforme dado/operação expostos. Distinguir autenticação de autorização e validar no limite. Não inferir ausência sem inspecionar middleware/fluxo. |
| Exposição de dados/erros — HIGH/MEDIUM | Resposta inclui segredos/PII; stack trace/SQL interno devolvido ao cliente | Vazamento. Resposta mínima e tratamento central com logs redigidos. |
| API deprecated/obsoleta — MEDIUM/HIGH | Uso documentado como removido/deprecated para versão efetiva (ex.: API de runtime/driver) | Quebra futura ou suporte ausente. Registrar prova, versão e substituto moderno compatível. Severidade aumenta se já falha na versão-alvo. |
| Query N+1 / acesso em loop — MEDIUM | Consulta repetida por item de coleção ou padrão equivalente comprovável | Latência/carga. Buscar em lote, join/eager load ou agregação. |
| Duplicação / tratamento inconsistente de erros — MEDIUM | Regra repetida ou handlers similares divergentes; erros sem fronteira coerente | Correções inconsistentes. Extrair abstração pequena e centralizar mapeamento de erro. |
| Ausência de separação de configuração / defaults perigosos — HIGH/MEDIUM | Configuração operacional/segredo em código, modo debug aberto, CORS permissivo | Exposição e deploy frágil. Configuração por ambiente com defaults seguros. Nunca repetir segredos no finding. |
| Magic numbers/strings e nomenclatura ambígua — LOW | Literais não autoexplicativos ou identificadores sem significado contextual | Leitura/manutenção mais custosa. Nomear constantes e melhorar nomes sem alterar comportamento. |
| Funções/rotas sem contrato ou validação de entrada — MEDIUM/LOW | Tipos/formato/limites não verificados em fronteira; classificação depende da consequência | Erros e comportamento inconsistente. Validar payload/parâmetros com mecanismo disponível. |

## Regras de APIs deprecated

Confirme a API e a versão pelo lockfile/runtime e documentação do fabricante disponível no repositório. Descreva símbolo, arquivo/linha, situação (deprecated/removida), fonte/evidência, versão afetada e substituto. Se não conseguir confirmar, marque como ponto a verificar, sem finding conclusivo. Não prescreva uma migração incompatível com a versão do projeto.
