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

### 2.0 Estrutura de Projeto (core + CLI)
O código é organizado separando lógica de negócio (`core/`) do ponto de entrada (`cli/`),
preparando reuso futuro por mobile app e bot Telegram sem reescrever a lógica de análise
(ver ADR-009).

```
diarium/
  core/
    models.py          # Pydantic: EntryData, AnalysisResult, HabitData
    parser.py           # Leitura de markdown + front-matter (independente de LLM)
    llm/
      base.py           # Interface abstrata LLMAdapter
      gemini_adapter.py # Implementação Gemini (JSON schema / function calling)
    analysis.py          # Orquestra: parser + adapter → AnalysisResult
    report.py            # Consolidação periódica (usa dados estruturados + LLM)
  cli/
    main.py             # Comandos `analisar` e `relatorio`, chama core/
  config.py              # Carrega provedor/API key (env var / config file)
```

Regra: CLI (e futuramente o backend de mobile/bot) chama apenas `core/analysis.py` e
`core/report.py`. Nenhum ponto de entrada deve chamar o `LLMAdapter` diretamente.

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
    def analyze_entry(self, text: str, habit_data: dict) -> AnalysisResult: ...
    def consolidate(self, analyses: list[AnalysisResult], habit_data: list[dict]) -> ReportResult: ...
```

Primeira implementação: **Gemini** (via `google-generativeai`), usando saída estruturada
(JSON schema / function calling) — não texto livre parseado por regex. A resposta é
validada contra o schema Pydantic no boundary; resposta fora do schema falha de forma
explícita, não é aceita silenciosamente.

Objetivo: trocar de provedor (ou migrar para modelo local) alterando apenas configuração
e adicionando um novo adapter, sem tocar no core.

### 2.4 Motor de Análise TCC
Contém os prompts estruturados (ver `prompts.md`) enviados ao LLM Adapter, e o parsing
da resposta em estrutura de dados (distorções identificadas, ABC/ABCDE, resumo).

### 2.5 Gerador de Saída
- **Análise individual:** gera um novo arquivo markdown vinculado à entrada original.
- **Relatório consolidado:** agrega análises de um intervalo, identifica padrões recorrentes,
  gera markdown único.

## 3. Fluxo de Dados

### Análise individual
1. Usuário roda `analisar --arquivo entrada.md`.
2. CLI lê o arquivo.
3. Motor de Análise monta prompt e envia ao LLM Adapter.
4. LLM Adapter chama a API configurada.
5. Resposta é parseada e formatada.
6. Gerador de Saída escreve markdown de análise.

### Relatório consolidado
1. Usuário roda `relatorio --de X --ate Y`.
2. CLI localiza análises individuais já geradas no intervalo (ou entradas brutas, se ainda não analisadas).
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
