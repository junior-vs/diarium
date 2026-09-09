# diarium-app

CLI que lê registros de diário em Markdown no [Obsidian](https://obsidian.md), processa o conteúdo através de um LLM configurável aplicando a abordagem da **TCC (Terapia Cognitivo-Comportamental)** e gera análises individuais, relatórios de período e relatórios longitudinais de tendência.

> [!IMPORTANT]
> **Limite de Papel (RF18):** Este sistema **NÃO é uma ferramenta clínica de diagnóstico** e **NÃO substitui psicoterapia ou atendimento psiquiátrico profissional**. Toda saída do sistema tem caráter estritamente reflexivo e de hipótese para investigação colaborativa (inclusive com o psicólogo do usuário), terminando em um rodapé fixo incondicional.

---

## Sumário

- [Requisitos](#requisitos)
- [Instalação](#instalação)
- [Configuração (.env)](#configuração-env)
- [Estrutura do Vault e Templates](#estrutura-do-vault-e-templates)
- [Uso da CLI](#uso-da-cli)
  - [`analisar` (Análise Individual)](#analisar)
  - [`relatorio` (Relatório de Período e Presets)](#relatorio)
  - [`tendencia` (Relatório Longitudinal de Tendência)](#tendencia)
- [Salvaguardas Clínicas e Determinísticas](#salvaguardas-clínicas-e-determinísticas)
  - [Triagem de Risco Independente (RF15 / ADR-022)](#triagem-de-risco-independente-rf15--adr-022)
  - [Modelo ABCDE com Perguntas Socráticas (ADR-018, 019, 020)](#modelo-abcde-com-perguntas-socráticas-adr-018-019-020)
  - [Guarda de Dados Mínimos (RF09)](#guarda-de-dados-mínimos-rf09)
  - [Tema Recorrente sem Rótulo Clínico (RF14 / ADR-021)](#tema-recorrente-sem-rótulo-clínico-rf14--adr-021)
  - [Rodapé Fixo Incondicional (RF18)](#rodapé-fixo-incondicional-rf18)
- [Reaproveitamento de Análises](#reaproveitamento-de-análises)
- [Providers de LLM Suportados](#providers-de-llm-suportados)
- [Rodando os Testes](#rodando-os-testes)
- [Arquitetura e Documentação](#arquitetura-e-documentação)

---

## Requisitos

- Python >= 3.11
- [uv](https://docs.astral.sh/uv/) para gerenciamento de dependências e ambiente

---

## Instalação

```bash
cd diarium-app
uv sync
```

Isso cria o ambiente virtual e instala as dependências (`pydantic`, `pydantic-settings`, `python-frontmatter`, `typer`, `google-genai`, etc.) declaradas no `pyproject.toml`.

Para executar qualquer comando no ambiente virtual, use o prefixo `uv run`:

```bash
uv run diario-tcc --help
```

*(O entrypoint também pode ser invocado como `diarium-app`.)*

---

## Configuração (.env)

O aplicativo lê configurações de variáveis de ambiente com prefixo `DIARIUM_`, carregadas automaticamente de um arquivo `.env` na pasta `diarium-app/`:

| Variável | Obrigatória | Default | Descrição |
| --- | --- | --- | --- |
| `DIARIUM_LLM_PROVIDER` | Não | `fake` | Provider de LLM: `fake` (testes/dry-run, offline) ou `gemini`. |
| `DIARIUM_LLM_API_KEY` | Sim (se `gemini`) | — | Chave de API do provedor. |
| `DIARIUM_LLM_MODEL` | Não | `gemini-2.5-flash` | Modelo do provider ativo. |
| `DIARIUM_VAULT_PATH` | Não | `../diarium-vault` | Caminho raiz do vault Obsidian. |

Exemplo de `.env`:

```dotenv
DIARIUM_LLM_PROVIDER=gemini
DIARIUM_LLM_API_KEY=AIzaSy...
DIARIUM_LLM_MODEL=gemini-2.5-flash
DIARIUM_VAULT_PATH=/caminho/para/diarium-vault
```

As variáveis de ambiente também podem ser sobrepostas pontualmente através de flags na linha de comando (`--provider`, `--api-key`, `--model`, `--vault-path`).

---

## Estrutura do Vault e Templates

O sistema segue convenções estritas de Markdown puro (ADR-001) sem banco de dados intermediário:

```plan-text
<vault>/
  diary/
    2026/
      09/
        2026-09-03.md
        2026-09-04.md
  analyses/
    2026/
      09/
        2026-09-03-analise.md
        2026-09-relatorio.md
      2026-07-01_2026-09-30-tendencia.md
```

### Formato da Nota de Entrada (`diary/AAAA/MM/AAAA-MM-DD.md`)

As notas diárias contêm front-matter YAML estruturado para variáveis de contexto (hábitos, ativação comportamental e positive data log):

```yaml
---
data: 2026-09-03
tags: [diario]
processado: false
mit: Finalizar proposta de arquitetura
sono: 7.5
estresse: 3
energia_humor: 4
hidratacao: 6
sol_manha: true
atividade_fisica: true
leitura: false
estudo: true
atividade_significativa:
  descricao: Caminhada no parque com amigos
  prazer: 4
  dominio: 3
positive_data_log: Consegui manter a calma durante a apresentação técnica.
---

## Brain Dump
Hoje o dia começou um pouco tenso, com receio da apresentação...

### 14:30 — Gatilho
- **Evento:** O diretor fez uma pergunta inesperada sobre o cronograma.
- **Pensamento:** Eu deveria ter previsto isso, vou parecer despreparado.
- **Emoção:** Ansiedade (7/10), calor no peito.
- **Comportamento:** Pedi desculpas excessivas e apressei a resposta.
```

---

## Uso da CLI

### `analisar`

Processa uma única entrada de diário, executando triagem de risco e análise TCC.

```bash
uv run diario-tcc analisar /caminho/vault/diary/2026/09/2026-09-03.md
```

**O que o comando faz:**

1. Executa a **triagem de risco independente** (RF15). Se houver indício de crise, insere deterministicamente o bloco de segurança estático no topo da saída.
2. Identifica possíveis **distorções cognitivas**, citando o trecho correspondente (RF03).
3. Estrutura cada bloco de gatilho timestampado no modelo **ABC/ABCDE**, mantendo o campo Comportamento e gerando 2 a 3 **perguntas socráticas abertas** no Dispute (D), deixando o Efeito (E) em aberto (RF04 / ADR-018, 019, 020).
4. Grava a análise em `analyses/AAAA/MM/AAAA-MM-DD-analise.md` com o rodapé fixo de RF18.
5. Atualiza a nota de diário original, marcando `processado: true` e anexando um resumo da análise com link bidirecional (ADR-008).

---

### `relatorio`

Gera um relatório consolidado por período a partir de múltiplas notas diárias.

```bash
# Via intervalo explícito
uv run diario-tcc relatorio --de 2026-09-01 --ate 2026-09-30

# Via preset de conveniência (diario, semanal, mensal, trimestral, semestral, anual)
uv run diario-tcc relatorio --preset mensal --referencia 2026-09-15
uv run diario-tcc relatorio --preset semanal
```

**Flags disponíveis:**

| Flag | Descrição |
| --- | --- |
| `--de` | Data inicial (`AAAA-MM-DD`). |
| `--ate` | Data final (`AAAA-MM-DD`). |
| `--preset` | Preset de conveniência: `diario`, `semanal`, `mensal`, `trimestral`, `semestral`, `anual`. |
| `--referencia` | Data de referência para o cálculo do preset (padrão: data de hoje). |
| `--forcar` | Recalcula todas as análises individuais do período, ignorando persistências anteriores. |
| `--tendencia` | Força a execução como relatório de tendência agregada sobre sub-períodos. |

> [!TIP]
> **Detecção Automática de Tendência:** Se o intervalo informado (ou derivado do preset) ultrapassar **45 dias** (ex: presets `trimestral`, `semestral`, `anual`), o comando `relatorio` automaticamente gera um **Relatório de Tendência** sobre os sub-períodos já processados (RF07).

---

### `tendencia`

Gera um relatório longitudinal comparativo agregando sobre **sub-períodos mensais já processados** (não entradas brutas), evidenciando variações de padrões ao longo do tempo.

```bash
uv run diario-tcc tendencia --preset trimestral --referencia 2026-09-15
uv run diario-tcc tendencia --de 2026-01-01 --ate 2026-06-30
```

**Comportamento:**

- Decompõe o período em meses civis (`AAAA-MM`).
- Localiza relatórios consolidados mensais pré-existentes.
- **Identificação de faltantes (RF08):** Se algum sub-período do intervalo não tiver sido processado, ele é listado explicitamente na seção `### Sub-períodos ausentes`, sem mascarar dados incompletos.
- **Variação de padrões (RF07 / RNF07):** Apresenta variações de distorções e correlações em linguagem epistêmica observada (ex: *"A distorção X apareceu com mais frequência em 2026-01 do que nos demais sub-períodos"*), sem afirmações causais ou diagnósticas.

---

## Salvaguardas Clínicas e Determinísticas

O `diarium` foi desenhado sob princípios rigorosos para evitar riscos éticos de ferramentas de IA em saúde mental:

### Triagem de Risco Independente (RF15 / ADR-022)

A verificação de ideação suicida ou desesperança grave ocorre em uma chamada isolada (`screen_risk`), executada **antes** e de forma independente da análise TCC. Quando detectado possível risco:

- O sistema insere no topo do arquivo o conteúdo estático versionado de [`docs/bloco-seguranca.md`](../docs/bloco-seguranca.md), contendo contatos como o CVV (188) e SAMU (192).
- Essa inserção é feita **por código**, nunca gerada por IA.
- A análise normal do diário é mantida integralmente abaixo do bloco de segurança.

### Modelo ABCDE com Perguntas Socráticas (ADR-018, 019, 020)

- Suporte a múltiplos blocos de gatilhos por dia, cada um timestampado (`### HH:MM — Gatilho`).
- Campo **Comportamento** explícito (evitação / comportamento de segurança).
- O campo **Dispute (D)** não recebe respostas prontas da IA; são geradas 2 a 3 **perguntas socráticas abertas** que convidam o usuário a examinar a própria crença.
- O campo **Effect (E)** permanece em aberto por padrão.

### Guarda de Dados Mínimos (RF09)

Correlações hábito × humor (RF13) e temas recorrentes (RF14) dependem de acúmulo de dados para terem valor. Se o período contiver **menos de 5 entradas**, o sistema aplica uma guarda determinística no código, exibindo explicitamente:
`"- Dados insuficientes para identificar tema recorrente (mínimo de entradas não atingido)."`

### Tema Recorrente sem Rótulo Clínico (RF14 / ADR-021)

O relatório identifica temas transversais entre diferentes situações, mas os formula sempre como **perguntas abertas para reflexão**, nunca atribuindo rótulos diagnósticos ou nomes de taxonomias clínicas (como esquemas desadaptativos precoces).

### Rodapé Fixo Incondicional (RF18)

Todas as saídas (`analisar`, `relatorio`, `tendencia`) incluem o rodapé incondicional versionado em [`docs/rodape.md`](../docs/rodape.md), reforçando o limite de papel da ferramenta e que ela não substitui profissionais qualificados.

---

## Reaproveitamento de Análises

O comando `relatorio` verifica se a entrada diária já possui uma análise correspondente em `analyses/` com carga útil (`analysis_json`) válida. Em caso positivo, reutiliza o resultado existente, economizando tokens e chamadas à API. Para forçar o reprocessamento completo, utilize a flag `--forcar`.

---

## Providers de LLM Suportados

- **`fake`**: `FakeLLMAdapter`, ideal para desenvolvimento e testes automatizados. Roda 100% local e sem chamadas de rede.
- **`gemini`**: `GeminiAdapter`, integra com o Google Gemini (`google-genai`) usando JSON schema estruturado via Pydantic para `AnalysisResult`, `ReportResult` e `RiskScreeningResponse`.

O registro em `config.py` segue o princípio Aberto/Fechado (OCP): novos provedores (ex: OpenAI, Ollama) podem ser registrados via `register_provider` sem modificar o core da aplicação.

---

## Rodando os Testes

A suíte completa de testes unitários e de integração cobre todas as regras de negócio, formatters puros, repositório, CLI e sincronismo dos prompts:

```bash
uv run pytest
```

Para rodar com verbosidade:

```bash
uv run pytest -v
```

---

## Arquitetura e Documentação

O projeto implementa **Clean Architecture**:

- `domain/`: Modelos Pydantic ricos (`EntryData`, `HabitData`, `AnalysisResult`, `ReportResult`, `TrendReportResult`) e funções puras de data/período.
- `ports/`: Interfaces abstratas (`LLMAdapter`, `EntryRepository`).
- `formatters/`: Funções estritamente puras para renderização em Markdown (`analysis_markdown`, `report_markdown`, `trend_markdown`, `source_note`).
- `use_cases/`: Casos de uso específicos (`analyze_entry`, `generate_period_report`, `generate_trend_report`).
- `infrastructure/`: Implementações concretas de repositório de arquivos (`FileSystemEntryRepository`), adaptadores de LLM (`GeminiAdapter`, `FakeLLMAdapter`) e carregadores de assets e prompts.
- `cli/`: Ponto de composição e comandos Typer (`main.py`).

Documentos complementares no diretório `docs/`:

- [`specification.md`](../docs/specification.md) — Requisitos funcionais (RF01–RF18) e não-funcionais (RNF01–RNF07).
- [`architecture.md`](../docs/architecture.md) — Visão técnica detalhada e decisões arquiteturais.
- [`decisions.md`](../docs/decisions.md) — Registro de Decisões de Arquitetura (ADRs 001 a 022).
- [`prompts.md`](../docs/prompts.md) — Biblioteca normativa de prompts TCC.
- [`template-diario.md`](../docs/template-diario.md) — Template de entrada diária para o Obsidian.
- [`obsidian-setup.md`](../docs/obsidian-setup.md) — Guia de configuração do Obsidian e plugins.
- [`bloco-seguranca.md`](../docs/bloco-seguranca.md) — Conteúdo fixo de segurança para triagem de risco (RF15).
- [`rodape.md`](../docs/rodape.md) — Texto fixo de limite de papel (RF18).
- [`roadmap.md`](../docs/roadmap.md) — Evolução planejada do projeto.
