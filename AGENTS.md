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
5. **Template de Baixa Carga Cognitiva (ADR-005):**
   - O template de entrada é desenhado para reduzir função executiva exigida (perfil TDAH): brain dump livre, prompts fixos curtos (manhã/noite), sem exigência de texto narrativo longo.
   - O modelo ABC/ABCDE é **opcional**, preenchido apenas quando houver um gatilho relevante — nunca obrigatório por entrada.
6. **Tracking de Hábitos via Front-matter (ADR-006):**
   - Hábitos e métricas (sono, estresse, energia/humor, hidratação, sol da manhã, atividade física, leitura, estudo, MIT) são campos estruturados no front-matter, não texto livre.
   - O CLI deve ler esses campos diretamente para compor o relatório consolidado — nunca depender do LLM para extrair esses dados de texto.
   - Campos como `sono` e `hidratacao` podem ser preenchidos a partir de dados de dispositivo (celular/smartwatch); não assumir que serão sempre digitados manualmente.
7. **Sem Redundância entre Front-matter e Conteúdo Visual (ADR-007):**
   - Não duplicar os mesmos dados em dois formatos (ex: front-matter + tabela). Se um checklist visual for necessário para leitura humana, ele deve espelhar o front-matter, nunca ser uma segunda fonte de verdade.
8. **Plugins Core no Obsidian (ADR-008):**
   - O vault utiliza apenas plugins nativos do Obsidian (Daily notes, Templates, Tags, Search, Backlinks).
   - O script externo lê o frontmatter e escreve links `[[YYYY-MM-DD]]` para backlinks automáticos. Evitar dependência de plugins comunitários como Dataview ou Templater.

---

## 4. Estrutura do Vault e Convenções de Arquivos

Conforme detalhado em [`docs/obsidian-setup.md`](file:///e:/develop/repos/misc/diarium/docs/obsidian-setup.md), a estrutura de pastas esperada pelo sistema é:

```text
/diarium-vault (vault root)
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
  mit: 
  sono: 
  estresse: 
  energia_humor: 
  hidratacao: 
  sol_manha: false
  atividade_fisica: false
  leitura: false
  estudo: false
  ---
  ```
  Ver template completo em `docs/template-diario.md`. Não remover ou renomear campos
  sem atualizar `docs/obsidian-setup.md`, `docs/prompts.md` e o parser do CLI juntos.
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

## 7. Fluxo de Trabalho para Agentes

- **Documentação e código andam juntos.** Se uma mudança altera requisito, arquitetura,
  prompt ou template, atualize o(s) arquivo(s) correspondente(s) em `docs/` no mesmo
  conjunto de alterações — nunca deixe a documentação desatualizada "para depois".
- **Antes de implementar, leia a documentação relevante.** Não assuma decisões — verifique
  `docs/decisions.md` antes de introduzir dependência, dado persistido ou mudança de fluxo.
- **Mudança de decisão arquitetural exige novo ADR.** Não edite um ADR existente para
  refletir uma nova decisão; adicione um novo ADR e, se o anterior for substituído,
  marque-o explicitamente como superado (ex: "Superado por ADR-00X").
- **Não expanda o escopo da v1 sem solicitação explícita.** Ver Seção 6. Se uma tarefa
  parecer exigir algo fora do escopo (ex: watcher, GUI), sinalize isso em vez de implementar.

## 8. Convenções de Código

- **Stack ainda não fixada.** Antes de introduzir uma linguagem/framework, verificar se já
  existe uma decisão registrada em `docs/decisions.md`; se não houver, registrar um ADR
  justificando a escolha antes de prosseguir.
- **Segredos e configuração:** API keys e endpoints de LLM devem vir de variáveis de
  ambiente ou arquivo de config não versionado (ex: `.env`, `config.yaml` no `.gitignore`).
  Nunca hardcode credenciais, nunca commit arquivos de config com valores reais.
- **LLM Adapter:** qualquer código que chame um provedor de LLM deve implementar a
  interface comum do adapter (ver ADR-003) — nunca acoplar lógica de negócio a uma API
  específica.
- **Parsing de front-matter:** deve ser tolerante a campos ausentes ou vazios (o usuário
  pode não preencher todos os hábitos todo dia); nunca falhar o processamento por um
  campo opcional vazio.

## 9. Testes e Validação

- Mudanças no LLM Adapter devem ser testáveis sem chamada real à API (usar mock/stub).
- Mudanças no parser de markdown/front-matter devem ter casos de teste cobrindo: campos
  ausentes, front-matter vazio, e entradas com apenas brain dump (sem gatilho preenchido).
- Antes de considerar uma tarefa concluída, validar contra os Critérios de Aceite em
  `docs/specification.md`.

## 10. Referência da Documentação

Para aprofundar qualquer tema, consulte os arquivos em `docs/`:
- [`docs/specification.md`](docs/specification.md) — Requisitos funcionais (RF01–RF10) e não-funcionais (RNF01–RNF05).
- [`docs/architecture.md`](docs/architecture.md) — Fluxo de dados, componentes e interfaces.
- [`docs/decisions.md`](docs/decisions.md) — ADRs detalhadas com contexto e justificativas.
- [`docs/prompts.md`](docs/prompts.md) — Biblioteca de prompts de escrita, análise e consolidação.
- [`docs/obsidian-setup.md`](docs/obsidian-setup.md) — Configuração do Obsidian e templates.
- [`docs/roadmap.md`](docs/roadmap.md) — Planejamento de versões.
- [`docs/template-diario.md`](docs/template-diario.md) — Template canônico da entrada diária.
