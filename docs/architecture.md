# Arquitetura: Diário TCC Assistido por LLM

## 1. Visão Geral da Arquitetura

CLI que orquestra leitura de arquivos markdown, chamada a um LLM via adapter configurável,
e geração de arquivos markdown de saída (análise individual e relatórios consolidados).

```
[Diário .md no Obsidian]
        │
        ▼
   [CLI Script] ──► [LLM Adapter] ──► [API do LLM]
        │                                  │
        ▼                                  ▼
[Leitura/parsing]                 [Resposta estruturada]
        │                                  │
        └──────────────┬───────────────────┘
                        ▼
          [Geração de markdown de análise]
                        │
                        ▼
          [Relatório consolidado periódico]
```

## 2. Componentes

### 2.0 Estrutura de Projeto (`diarium_app` + CLI)

O código é organizado separando domínio, portas, formatação, casos de uso, infraestrutura
e ponto de entrada, preparando reuso futuro por mobile app e bot Telegram sem reescrever
a lógica de análise.

```
diarium_app/
  domain/
    models.py          # Pydantic: EntryData, AnalysisResult, HabitData
    entry_date.py      # Resolução de datas da entrada
  ports/
    llm_adapter.py     # Interface abstrata LLMAdapter
    entry_repository.py
  formatters/
    analysis_markdown.py
    report_markdown.py
    source_note.py
  use_cases/
    analyze_entry.py   # Orquestra análise individual
    generate_period_report.py
  infrastructure/
    filesystem_entry_repository.py
    llm/
      fake_adapter.py
      gemini_adapter.py
      prompt_loader.py
      prompts/
  cli/
    main.py            # Comandos `analisar` e `relatorio`, composition root
  config.py            # Carrega provedor/API key (env var / config file)
```

Regra: CLI (e futuramente o backend de mobile/bot) chama apenas os casos de uso em
`use_cases/`. Nenhum ponto de entrada deve chamar o `LLMAdapter` diretamente.

### 2.1 CLI

Ponto de entrada. Comandos principais:

- `analisar --arquivo <path>` — processa uma entrada individual.
- `relatorio --de <data> --ate <data>` — consolida múltiplas entradas em relatório periódico.

### 2.2 Leitor/Parser de Markdown

Responsável por ler o arquivo do diário e extrair o conteúdo textual relevante
(ignorando front-matter/metadados do Obsidian quando presentes).

### 2.3 LLM Adapter

Camada de abstração entre o core do sistema e o provedor de LLM. Define uma interface
comum implementada por adapters específicos:

```python
class LLMAdapter(ABC):
    def screen_risk(self, text: str) -> RiskScreeningResult: ...
    def analyze_entry(self, text: str, habit_data: dict) -> AnalysisResult: ...
    def consolidate(self, analyses: list[AnalysisResult], habit_data: list[dict]) -> ReportResult: ...
```

`screen_risk` é chamado antes e independentemente de `analyze_entry`, para toda entrada
e cada bloco de gatilho isoladamente (ver ADR-022). Retorna um resultado estruturado
(`sem_indicio` / `possivel_risco`), nunca texto livre — a resposta mostrada ao usuário
quando há possível risco é conteúdo fixo (`bloco-seguranca.md`), controlado pelo
Gerador de Saída, não pelo LLM.

Primeira implementação: **Gemini** (via `google-generativeai`), usando saída estruturada
(JSON schema / function calling) — não texto livre parseado por regex. A resposta é
validada contra o schema Pydantic no boundary; resposta fora do schema falha de forma
explícita, não é aceita silenciosamente.

Objetivo: trocar de provedor (ou migrar para modelo local) alterando apenas configuração
e adicionando um novo adapter, sem tocar no domínio ou nos casos de uso.

### 2.4 Motor de Análise TCC

Contém os prompts estruturados (ver `prompts.md`) enviados ao LLM Adapter, e o parsing
da resposta em estrutura de dados (distorções identificadas, ABC/ABCDE, resumo).

### 2.5 Gerador de Saída

- **Análise individual:** gera um novo arquivo markdown vinculado à entrada original e,
  quando configurado, pode anexar uma seção determinística na nota de origem sem
  sobrescrever o conteúdo existente. Quando a triagem de risco (`screen_risk`) indicar
  `possivel_risco` para a entrada ou algum bloco de gatilho, insere no topo o conteúdo
  fixo de `bloco-seguranca.md` — nunca texto gerado pelo LLM (ver ADR-022) — sem
  suprimir a análise TCC normal.
- **Relatório consolidado:** agrega as notas brutas de um intervalo, identifica padrões
  recorrentes, gera markdown único e respeita o layout canônico `analyses/YYYY/MMMM`.

## 3. Fluxo de Dados

### Análise individual

1. Usuário roda `analisar --arquivo entrada.md`.
2. CLI lê o arquivo.
3. Para a entrada geral e para cada bloco de gatilho isoladamente, o Motor de Análise
   primeiro executa a triagem de risco via LLM Adapter (`screen_risk`).
4. Motor de Análise monta o prompt de análise TCC e envia ao LLM Adapter.
5. LLM Adapter chama a API configurada.
6. Resposta é parseada e formatada.
7. Gerador de Saída escreve markdown de análise, inserindo o bloco de segurança fixo
   no topo quando a triagem indicar `possivel_risco` (ver ADR-022).

### Relatório consolidado

1. Usuário roda `relatorio --de X --ate Y`.
2. CLI localiza as notas brutas do intervalo como fonte de verdade. Se houver análises ou
  relatórios pré-existentes, o usuário é avisado e o conteúdo é regenerado a partir das
  entradas originais.
3. Motor de Análise monta prompt de consolidação.
4. LLM Adapter processa.
5. Gerador de Saída escreve relatório único.

## 4. Configuração

- Provedor de LLM, API key, modelo: via arquivo de config (ex: `.env` ou `config.yaml`).
- Caminhos de entrada/saída: configuráveis.

## 5. Decisões Arquiteturais Chave

- **CLI em vez de watch automático:** simplicidade v1, controle explícito do usuário. (ver decisions.md)
- **Adapter pattern para LLM:** preparar migração futura para modelo local sem refatoração.
- **Markdown como formato universal:** compatibilidade nativa com Obsidian, sem dependência de banco de dados.

## 6. Extensibilidade Futura

- Watch de pasta (automação).
- Adapter para modelo local (Ollama).
- App mobile e bot Telegram consumindo `core/` — nesse momento, `core/` provavelmente
  precisa ser exposto via API (REST/RPC), já que mobile e bot não têm acesso direto ao
  filesystem do vault Obsidian. Isso é uma mudança de camada de acesso, não do core em si.
