# AGENTS.md — Diretrizes para Agentes de IA

Este documento define o contexto do projeto, princípios arquiteturais, restrições clínicas e de privacidade, convenções de código e fluxo de trabalho para qualquer agente de IA que atue neste repositório.

---

## 1. Visão Geral do Projeto

**Diário TCC Assistido por LLM** (`diarium`) é uma ferramenta pessoal que processa registros de diário escritos em Markdown no [Obsidian](https://obsidian.md) através de um LLM configurável, aplicando a abordagem da **TCC (Terapia Cognitivo-Comportamental)**.

### Objetivos Principais
- Ajudar o usuário a registrar pensamentos e eventos cotidianos de forma estruturada.
- Identificar automaticamente possíveis distorções cognitivas nas anotações, como hipótese, nunca como diagnóstico.
- Estruturar cada ocorrência de gatilho no modelo ABC/ABCDE, com D como perguntas socráticas.
- Executar triagem de risco separada da análise cognitiva.
- Gerar relatórios de período e de tendência que auxiliem no autoconhecimento e possam ser levados a sessões com o psicólogo/terapeuta do usuário.

---

## 2. Restrições Éticas, Clínicas e de Privacidade

> [!CAUTION]
> **Privacidade de Dados Sensíveis (RNF01):** Entradas de diário contêm reflexões íntimas e dados sensíveis. O sistema nunca deve persistir, expor ou enviar diários para serviços externos além da chamada direta e estritamente necessária à API de LLM configurada pelo usuário. Nunca armazene logs contendo o texto bruto dos diários.

> [!IMPORTANT]
> **Caráter Não-Diagnóstico e Reforço Estrutural (RF15, RF18, RNF07):**
> - O sistema **NÃO é uma ferramenta clínica de diagnóstico** e **NÃO substitui psicoterapia ou atendimento psiquiátrico profissional**.
> - Essa garantia **não pode depender só do LLM obedecer ao prompt**. RF18 exige rodapé fixo, não gerado pelo LLM, em toda saída. RF15 exige triagem de risco determinística com bloco de segurança estático (`docs/bloco-seguranca.md`), inserido por código, nunca pelo LLM.
> - Toda saída interpretativa (distorções, função de comportamento, tema recorrente, correlações) usa linguagem hedged: hipótese, pergunta, associação observada — nunca afirmação categórica, causal ou rótulo clínico (RNF07).
> - Contagem/frequência de distorções é dado descritivo, nunca indicador de gravidade.

---

## 3. Arquitetura e Decisões Técnicas (ADRs)

Ao modificar ou criar código, respeite rigorosamente as decisões arquiteturais registradas em [`docs/decisions.md`](docs/decisions.md). Resumo das mais relevantes para código:

1. **Markdown Puro (ADR-001/RNF03):** entrada/saída exclusivamente `.md`, sem banco de dados.
2. **CLI Sob Demanda (ADR-002/RNF04):** processamento manual via `diario-tcc`; sem watch/daemon na v1.
3. **LLM Adapter (ADR-003/RNF02):** `core` agnóstico de provedor; toda chamada passa pela interface `LLMAdapter` (`ports/llm_adapter.py`), que inclui `analyze_entry`, `consolidate` **e `screen_risk`** (ADR-022) — qualquer novo adapter concreto implementa os três.
4. **Sem Interface Gráfica Própria (ADR-004):** front-end é o Obsidian.
5. **Template de Baixa Carga Cognitiva (ADR-005):** ABC/ABCDE opcional por gatilho, nunca obrigatório por entrada; N blocos por dia, cada um timestampado (ADR-018/019).
6. **D como pergunta, não resposta (ADR-020):** por padrão, o campo D de cada `ABCDETrigger` é uma lista de 2-3 perguntas socráticas; E fica em aberto. Nunca resolver D/E automaticamente sem explicitar essa é uma mudança de decisão (exigiria novo ADR).
7. **Tracking de Hábitos via Front-matter (ADR-006):** hábitos são campos estruturados, lidos diretamente pelo CLI — nunca extraídos de texto livre pelo LLM.
8. **Tema recorrente sem rótulo de schema (ADR-021):** `ReportResult.tema_recorrente` é sempre formulado como pergunta; nunca nomear taxonomia clínica (ex: Early Maladaptive Schemas).
9. **Triagem de risco separada e determinística (ADR-022):** `screen_risk` roda antes e independentemente de `analyze_entry`; resultado é enum estruturado (`RiskScreeningResult`), nunca texto livre; bloco de segurança é conteúdo estático versionado, inserido por código.
10. **Sem Redundância entre Front-matter e Conteúdo Visual (ADR-007).**
11. **Plugins Core no Obsidian (ADR-008).**

---

## 4. Premissas de Código

O projeto segue **Clean Architecture** (domain → ports → use_cases → infrastructure/cli), com as seguintes premissas obrigatórias para qualquer contribuição:

### Orientação a Objetos
- Modelos de domínio são objetos de valor ricos (Pydantic `BaseModel`), nunca dicionários soltos passando entre camadas.
- Toda integração externa (LLM, filesystem) é abstraída por uma interface ABC (`ports/`) e implementada por uma classe concreta (`infrastructure/`) — nunca acoplar `use_cases/` a uma biblioteca externa diretamente.

### Programação Funcional
- Funções em `domain/` (ex: `entry_date.py`, `report_period.py`) e `formatters/` são **puras**: mesma entrada → mesma saída, sem I/O, sem estado mutável compartilhado. Isso as torna testáveis sem mocks.
- Formatters nunca leem arquivo nem chamam API — todo conteúdo (inclusive textos estáticos como o rodapé de RF18 e o bloco de segurança de RF15) é passado como parâmetro, carregado na borda (`infrastructure/` ou `cli/`).

### SOLID
- **SRP:** cada use case tem uma responsabilidade (`analyze_entry`, `generate_period_report`, `generate_trend_report` são casos de uso separados, não um único "processar" genérico). `ReportResult` (período) e `TrendReportResult` (tendência) são modelos separados, não um único modelo sobrecarregado.
- **OCP:** novo provedor de LLM = nova classe em `infrastructure/llm/` + registro em `config.py` (`register_provider`), sem alterar `use_cases/` nem `ports/`. Ver comentário em `config.py`.
- **LSP:** qualquer implementação de `LLMAdapter` deve honrar os três métodos (`analyze_entry`, `consolidate`, `screen_risk`) com o mesmo contrato — inclusive `FakeLLMAdapter` usado em teste.
- **ISP:** não dividir `LLMAdapter` em interfaces menores especulativamente — só separar quando houver um adapter concreto que realisticamente implemente apenas parte do contrato (YAGNI até lá).
- **DIP:** `use_cases/` dependem de `ports/` (abstrações), nunca de `infrastructure/` diretamente. `cli/main.py` é o único lugar que resolve a implementação concreta (via `config.build_adapter`).

### Clean Code
- Nomes de domínio em português, consistentes com a documentação (`gatilho`, `distorcao`, `habito`) — não misturar com termos em inglês no mesmo nível de abstração.
- `model_config = {"extra": "ignore"}` em todo modelo que reflete front-matter do usuário — tolerância a campo desconhecido é requisito, não acidente.
- Toda função pública tem docstring de uma linha explicando o "quê", comentários explicam o "porquê" quando a decisão não é óbvia (ver padrão já usado em `filesystem_entry_repository.py`).

---

## 5. Estrutura do Vault e Convenções de Arquivos

*(inalterado — ver versão anterior)*

---

## 6. Modelo TCC e Prompts

- **Modelo ABC/ABCDE** aplicado por bloco de gatilho (não por entrada inteira): A (evento), B (pensamento), C (emoção/reação), Comportamento (evitação/segurança — ADR-019), D (2-3 perguntas socráticas, não resposta — ADR-020), E (aberto por padrão).
- Baseie-se em [`docs/prompts.md`](docs/prompts.md) para o texto exato; os arquivos `.txt` reais em `infrastructure/llm/prompts/` **devem espelhar esse documento** — qualquer edição de prompt real sem atualizar `docs/prompts.md` no mesmo commit é considerada incompleta.
- **Distorções Cognitivas Frequentes:** Catastrofização, pensamento polarizado, leitura mental, adivinhação do futuro, raciocínio emocional, hipergeneralização, filtros mentais, personalização, rotulação, imperativos.

---

## 7. Escopo: v1 vs Futuras Versões

Ver [`docs/roadmap.md`](docs/roadmap.md). V1 inclui triagem de risco (RF15) e rodapé de limite de papel (RF18) como requisitos bloqueantes, não opcionais — não considerar a v1 "completa" sem eles implementados e testados.

---

## 8. Fluxo de Trabalho para Agentes

- **Documentação e código andam juntos.** Mudança de requisito, arquitetura, prompt ou template exige atualizar `docs/` no mesmo conjunto de alterações.
- **Antes de implementar, leia `docs/decisions.md` e `docs/specification.md`.**
- **Mudança de decisão arquitetural exige novo ADR** — não editar ADR existente; marcar como "Superado por ADR-00X" se aplicável.
- **Não expanda o escopo da v1 sem solicitação explícita.**
- **Divergência entre `.txt` de prompt real e `docs/prompts.md` é bug, não liberdade de implementação** — reportar/corrigir, nunca silenciar.

## 9. Convenções de Código

*(inalterado, + nota:)* Qualquer novo campo de domínio que reflita front-matter do template deve ser adicionado simultaneamente em `HabitData`/`EntryData`, `docs/template-diario.md` e `docs/obsidian-setup.md`.

## 10. Testes e Validação

- Mudanças no `LLMAdapter` (incluindo `screen_risk`) devem ser testáveis via `FakeLLMAdapter`, sem chamada real.
- `screen_risk` precisa de teste cobrindo `possivel_risco` → bloco de segurança presente + análise normal preservada.
- Relatório com menos de `MIN_ENTRIES_FOR_PATTERNS` entradas precisa de teste confirmando `dados_insuficientes=True` e seções vazias, não inventadas.
- Antes de considerar uma tarefa concluída, validar contra os Critérios de Aceite em `docs/specification.md`.

## 11. Referência da Documentação

- [`docs/specification.md`](docs/specification.md) — RF01–RF18, RNF01–RNF07.
- [`docs/architecture.md`](docs/architecture.md), [`docs/decisions.md`](docs/decisions.md), [`docs/prompts.md`](docs/prompts.md), [`docs/obsidian-setup.md`](docs/obsidian-setup.md), [`docs/roadmap.md`](docs/roadmap.md), [`docs/template-diario.md`](docs/template-diario.md), [`docs/bloco-seguranca.md`](docs/bloco-seguranca.md).