# Registro de Decisões Técnicas (ADR)

## ADR-001: Markdown como formato de entrada e saída
**Data:** 2026-09-03
**Decisão:** Usar markdown puro como formato de entrada (diário) e saída (análise/relatório).
**Motivo:** Compatibilidade nativa com Obsidian, sem necessidade de banco de dados ou
formato proprietário. Facilita versionamento (git) e portabilidade.
**Alternativas consideradas:** Banco de dados local (SQLite), formato JSON estruturado.

## ADR-002: CLI sob demanda em vez de watch automático (v1)
**Data:** 2026-09-03
**Decisão:** v1 processa arquivos sob demanda via comando manual.
**Motivo:** Reduz complexidade inicial, evita dependência de processo em background,
dá controle explícito sobre quando enviar dados sensíveis à API externa.
**Revisão futura:** Watch automático fica no roadmap (ver roadmap.md).

## ADR-003: LLM Adapter (abstração de provedor)
**Data:** 2026-09-03
**Decisão:** Isolar chamadas ao LLM atrás de uma interface comum (adapter pattern).
**Motivo:** Requisito explícito de migração futura para modelo local (Ollama), sem
acoplar o core do sistema a uma API específica.
**Implicação:** Qualquer prompt/parsing específico de provedor fica encapsulado no adapter,
não no core.

## ADR-004: Sem interface gráfica própria (v1)
**Data:** 2026-09-03
**Decisão:** Obsidian atua como front-end de escrita/leitura; sistema é CLI puro.
**Motivo:** Foco do v1 é validar o motor de processamento LLM, não a experiência de UI.

## ADR-005: Uso mínimo de plugins de terceiros no Obsidian
**Data:** 2026-09-03
**Decisão:** Configuração do vault prioriza plugins core (Daily notes, Templates, Tags,
Search, Backlinks), evitando Dataview, Templater e afins.
**Motivo:** Processamento e agregação de dados ficam no CLI externo; o Obsidian atua
apenas como editor/visualizador. Reduz superfície de dependência e manutenção.
