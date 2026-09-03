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

## ADR-005: Template orientado a baixa carga cognitiva (design para TDAH)
**Data:** 2026-09-03
**Decisão:** Substituir o modelo narrativo original (5 seções abertas, ABC/ABCDE obrigatório)
por um template com: brain dump livre, prompts fixos curtos divididos em manhã/noite, e
ABC/ABCDE como seção opcional (só preenchida quando houver gatilho relevante).
**Motivo:** Journaling narrativo tradicional exige atenção sustentada e função executiva
altas, o que reduz adesão em perfil TDAH. Prompts fixos e baixa barreira de entrada
(regra dos 2 minutos) favorecem consistência de uso sobre completude do registro.
**Implicação:** O prompt de análise do LLM precisa lidar com entradas fragmentadas/curtas
sem exigir estrutura completa (ver prompts.md).

## ADR-006: Tracking de hábitos via front-matter estruturado
**Data:** 2026-09-03
**Decisão:** Rastrear hábitos (sono, estresse, energia/humor, hidratação, sol da manhã,
atividade física, leitura, estudo, MIT) como campos de front-matter, não como texto livre.
**Motivo:** Dados estruturados são lidos diretamente pelo CLI para o relatório consolidado,
sem depender de o LLM interpretar texto — mais confiável e mais barato (menos tokens).
Reduz também a carga de escrita: marcar um campo é mais rápido que descrever em texto.
**Nota:** Campos como sono e hidratação podem ser preenchidos a partir de dados de
dispositivo (celular/smartwatch) em vez de digitação manual, quando disponível.
**Alternativas consideradas:** Registrar hábitos em texto livre e deixar o LLM extrair —
descartado por gerar custo extra e risco de inconsistência na extração.

## ADR-007: Sem tabela de check-in redundante com front-matter
**Data:** 2026-09-03
**Decisão:** Manter os campos de hábito apenas uma vez no documento (checklist inline
próximo ao topo), refletindo os mesmos valores do front-matter, em vez de duplicar em
uma tabela visual separada.
**Motivo:** Preencher os mesmos dados em dois lugares (front-matter + tabela) gera trabalho
duplicado, o que vai contra o princípio de baixa fricção (ADR-005).

## ADR-009: Separação core + CLI desde o MVP
**Data:** 2026-09-03
**Decisão:** Estruturar o projeto Python em `core/` (lógica de negócio: parser, análise,
relatório, LLM adapter) separado de `cli/` (ponto de entrada). CLI chama apenas `core/`,
nunca contém regra de negócio.
**Motivo:** Mobile app e bot Telegram já estão planejados (roadmap v2/v3), não são
especulação. Separar agora tem custo baixo (organização de módulos) e evita reescrever
a lógica de análise quando um segundo ponto de entrada for adicionado.
**Alternativas consideradas:** CLI monolítico simples, refatorar depois — descartado
porque lógica de negócio tende a vazar para dentro do CLI se não isolada desde o início.

## ADR-010: Saída estruturada (JSON) do LLM, não texto livre
**Data:** 2026-09-03
**Decisão:** O `LLMAdapter` retorna dados estruturados (validados via Pydantic), usando
JSON schema / function calling do provedor, em vez de texto livre parseado por regex.
**Motivo:** Texto livre é frágil de parsear e falha silenciosamente. RF10 (correlacionar
hábitos com distorções no relatório) exige dados programáticos. Resposta fora do schema
deve falhar de forma explícita, não ser aceita "quase certa".
**Implicação:** `docs/prompts.md` deve refletir os prompts como parte de uma chamada com
schema/function definido, não apenas texto de instrução solto.

## ADR-011: Gemini como primeiro provedor de LLM
**Data:** 2026-09-03
**Decisão:** Implementar `GeminiAdapter` como primeira implementação concreta de
`LLMAdapter` (via SDK `google-generativeai`), suportando saída estruturada nativamente.
**Motivo:** Escolha do usuário para o MVP. Suporte nativo a `response_schema` facilita
ADR-010 sem lógica adicional de parsing.
**Implicação:** Segundo provedor (ex: OpenAI, Claude) deve ser adicionado apenas como
novo adapter implementando a mesma interface — sem alterar `core/analysis.py` ou
`core/report.py`.

## ADR-012: Uso mínimo de plugins de terceiros no Obsidian
**Data:** 2026-09-03
**Decisão:** Configuração do vault prioriza plugins core (Daily notes, Templates, Tags,
Search, Backlinks), evitando Dataview, Templater e afins.
**Motivo:** Processamento e agregação de dados ficam no CLI externo; o Obsidian atua
apenas como editor/visualizador. Reduz superfície de dependência e manutenção.
