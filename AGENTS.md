# AGENTS.md — Diretrizes para Agentes de IA

Este documento define o contexto do projeto, princípios arquiteturais, restrições clínicas e de privacidade, convenções de código e fluxo de trabalho para qualquer agente de IA que atue neste repositório.

---

## 1. Visão Geral do Projeto

**Diário TCC Assistido por LLM** (`diarium`) é uma ferramenta pessoal que processa registros de diário escritos em Markdown no [Obsidian](https://obsidian.md) através de um LLM configurável, aplicando a abordagem da **TCC (Terapia Cognitivo-Comportamental)**.

### Objetivos Principais
- Ajudar o usuário a registrar pensamentos e eventos cotidianos de forma estruturada.
- Identificar automaticamente distorções cognitivas nas anotações.
- Estruturar entradas no modelo **ABC / ABCDE** da TCC.
- Gerar relatórios periódicos consolidados que auxiliem no autoconhecimento e possam ser levados a sessões com o psicólogo/terapeuta do usuário.

---

## 2. Restrições Éticas, Clínicas e de Privacidade

> [!CAUTION]
> **Privacidade de Dados Sensíveis (RNF01):** Entradas de diário contêm reflexões íntimas e dados sensíveis. O sistema nunca deve persistir, expor ou enviar diários para serviços externos além da chamada direta e estritamente necessária à API de LLM configurada pelo usuário. Nunca armazene logs contendo o texto bruto dos diários.

> [!IMPORTANT]
> **Caráter Não-Diagnóstico:**
> - O sistema **NÃO é uma ferramenta clínica de diagnóstico** e **NÃO substitui psicoterapia ou atendimento psiquiátrico profissional**.
> - Toda resposta, análise gerada e relatório deve manter tom objetivo, construtivo, sem alarmismo e conter o aviso de que se trata de uma ferramenta de apoio ao autoconhecimento.
> - O LLM deve apontar *possíveis* distorções e sugerir reflexões, nunca rotular o usuário ou emitir laudos.

---

## 3. Arquitetura e Decisões Técnicas (ADRs)

Ao modificar ou criar código, respeite rigorosamente as decisões arquiteturais registradas em [`docs/decisions.md`](file:///e:/develop/repos/misc/diarium/docs/decisions.md):

1. **Markdown Puro como Formato Universal (ADR-001 / RNF03):**
   - Entrada e saída são exclusivamente arquivos `.md` compatíveis com o Obsidian.
   - Não introduzir dependências de bancos de dados relacionais, SQLite ou formatos binários/proprietários para armazenamento de notas.
2. **CLI Sob Demanda (ADR-002 / RNF04):**
   - O processamento na v1 é executado manualmente pelo usuário via CLI (`diario-tcc`).
   - Não implementar daemons, watch automático de pastas ou processos em background contínuos na v1 (planejado apenas para v2).
3. **Padrão LLM Adapter (ADR-003 / RNF02):**
   - O núcleo da aplicação (`core`) deve ser totalmente agnóstico de provedor de LLM.
   - Todas as chamadas à API devem passar por uma interface/abstração (`LLMAdapter`), permitindo alternar entre provedores (OpenAI, Anthropic Claude, Gemini) ou modelos locais (Ollama no futuro) via configuração, sem alterar a regra de negócio.
4. **Sem Interface Gráfica Própria (ADR-004):**
   - O front-end de leitura e escrita é o próprio Obsidian. Não criar GUIs ou aplicações web/mobile na v1.
5. **Plugins Core no Obsidian (ADR-005):**
   - O vault utiliza apenas plugins nativos do Obsidian (Daily notes, Templates, Tags, Search, Backlinks).
   - O script externo lê o frontmatter e escreve links `[[YYYY-MM-DD]]` para backlinks automáticos. Evitar dependência de plugins comunitários como Dataview ou Templater.

---

## 4. Estrutura do Vault e Convenções de Arquivos

Conforme detalhado em [`docs/obsidian-setup.md`](file:///e:/develop/repos/misc/diarium/docs/obsidian-setup.md), a estrutura de pastas esperada pelo sistema é:

```text
/ (vault root)
├── diario/          # Entradas brutas escritas pelo usuário (YYYY-MM-DD.md)
├── analises/        # Saídas geradas pelo CLI (YYYY-MM-DD-analise.md)
├── relatorios/      # Consolidações periódicas (YYYY-MM-relatorio.md)
├── templates/       # Modelos de nota do Obsidian (template-diario.md)
└── docs/            # Documentação técnica do projeto
```

### Front-matter e Metadados
- **Entrada diária (`/diario/YYYY-MM-DD.md`):**
  ```markdown
  ---
  data: YYYY-MM-DD
  tags: [diario]
  analisado: false
  ---
  ```
- **Análise individual (`/analises/YYYY-MM-DD-analise.md`):**
  ```markdown
  ---
  data: YYYY-MM-DD
  tags: [analise-tcc]
  entrada_origem: "[[YYYY-MM-DD]]"
  ---
  ```

---

## 5. Modelo TCC e Prompts

Ao trabalhar no motor de análise ou nos prompts, baseie-se em [`docs/prompts.md`](file:///e:/develop/repos/misc/diarium/docs/prompts.md):

- **Modelo ABC / ABCDE:**
  - **A (Activating Event):** O evento, situação ou gatilho.
  - **B (Beliefs):** Pensamentos automáticos, crenças e interpretações.
  - **C (Consequences):** Reações emocionais e comportamentais consequentes.
  - **D (Disputation):** Questionamento racional e evidências contrárias ao pensamento distorcido.
  - **E (Effective New Belief / Effect):** Nova perspectiva equilibrada e resposta adaptativa.
- **Distorções Cognitivas Frequentes:** Catastrofização, pensamento polarizado (tudo-ou-nada), leitura mental, adivinhação do futuro, raciocínio emocional, hipergeneralização, filtros mentais, personalização, rotulação e imperativos ("deveria/tenho que").

---

## 6. Escopo: v1 vs Futuras Versões

Respeite as fronteiras de versão descritas em [`docs/roadmap.md`](file:///e:/develop/repos/misc/diarium/docs/roadmap.md):

- **Escopo Atual (v1):**
  - CLI funcional: `diario-tcc analisar --arquivo <path>` e `diario-tcc relatorio --de <data> --ate <data>`.
  - Leitor/parser de Markdown (ignora frontmatter na extração do texto).
  - LLM Adapter com pelo menos um provedor (ex: Claude ou OpenAI).
  - Geração de arquivos `.md` de análise e relatório periódico com links e frontmatter corretos.
- **Fora de Escopo na v1 (Não implementar sem solicitação explícita):**
  - Watcher/automação contínua de pastas (v2).
  - Execução local via Ollama (v2).
  - Exportação para PDF ou interfaces gráficas (v3).

---

## 7. Referência da Documentação

Para aprofundar qualquer tema, consulte os arquivos em `docs/`:
- [`docs/specification.md`](file:///e:/develop/repos/misc/diarium/docs/specification.md) — Requisitos funcionais (RF01–RF08) e não-funcionais (RNF01–RNF04).
- [`docs/architecture.md`](file:///e:/develop/repos/misc/diarium/docs/architecture.md) — Fluxo de dados, componentes e interfaces.
- [`docs/decisions.md`](file:///e:/develop/repos/misc/diarium/docs/decisions.md) — ADRs detalhadas com contexto e justificativas.
- [`docs/prompts.md`](file:///e:/develop/repos/misc/diarium/docs/prompts.md) — Biblioteca de prompts de escrita, análise e consolidação.
- [`docs/obsidian-setup.md`](file:///e:/develop/repos/misc/diarium/docs/obsidian-setup.md) — Configuração do Obsidian e templates.
- [`docs/roadmap.md`](file:///e:/develop/repos/misc/diarium/docs/roadmap.md) — Planejamento de versões.
