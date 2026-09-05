# diarium-app

CLI que lê entradas de diário em Markdown (Obsidian), envia para um LLM aplicando
uma abordagem de TCC (Terapia Cognitivo-Comportamental) e gera análises individuais
e relatórios consolidados por período.

> Este sistema não substitui acompanhamento profissional. É uma ferramenta de apoio
> ao autoconhecimento e ao processo terapêutico.

## Sumário

- [Requisitos](#requisitos)
- [Instalação](#instalação)
- [Configuração (.env)](#configuração-env)
- [Estrutura esperada do vault](#estrutura-esperada-do-vault)
- [Uso da CLI](#uso-da-cli)
  - [`analisar`](#analisar)
  - [`relatorio`](#relatorio)
- [Reaproveitamento de análises](#reaproveitamento-de-análises)
- [Providers de LLM suportados](#providers-de-llm-suportados)
- [Rodando os testes](#rodando-os-testes)
- [Arquitetura](#arquitetura)

## Requisitos

- Python >= 3.11
- [uv](https://docs.astral.sh/uv/) para gerenciamento de dependências e ambiente

## Instalação

```bash
cd diarium-app
uv sync
```

Isso cria o ambiente virtual e instala todas as dependências (`pydantic`,
`python-frontmatter`, `typer`, `google-genai`, etc.) declaradas no `pyproject.toml`.

Para rodar qualquer comando dentro do ambiente do projeto, prefixe com `uv run`:

```bash
uv run diario-tcc --help
```

(O mesmo binário também está registrado como `diarium-app` — os dois nomes
apontam para o mesmo entrypoint.)

## Configuração (.env)

O app lê configurações de variáveis de ambiente com prefixo `DIARIUM_`, carregadas
automaticamente de um arquivo `.env` na raiz de `diarium-app/` (já coberto pelo
`.gitignore` — não versionar segredos).

| Variável | Obrigatória | Default | Descrição |
|---|---|---|---|
| `DIARIUM_LLM_PROVIDER` | Não | `fake` | Provider de LLM: `fake` (testes/dry-run, sem chamada externa) ou `gemini`. |
| `DIARIUM_LLM_API_KEY` | Sim, se `llm_provider=gemini` | — | Chave de API do provider escolhido. |
| `DIARIUM_LLM_MODEL` | Não | default do provider (`gemini-2.5-flash` para Gemini) | Sobrepõe o modelo usado pelo provider ativo. |
| `DIARIUM_VAULT_PATH` | Não | `../diarium-vault` (relativo ao pacote) | Caminho raiz do vault Obsidian. |

Exemplo de `.env`:
```dotenv
DIARIUM_LLM_PROVIDER=gemini
DIARIUM_LLM_API_KEY=coloque-sua-chave-aqui
DIARIUM_LLM_MODEL=gemini-2.5-flash
DIARIUM_VAULT_PATH=/caminho/para/diarium-vault
```

Qualquer uma dessas variáveis também pode ser sobreposta por flag de linha de
comando (ver [Uso da CLI](#uso-da-cli)) — a flag tem prioridade sobre o `.env`.

## Estrutura esperada do vault

```
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
```

- `diary/AAAA/MM/AAAA-MM-DD.md` — entradas brutas escritas pelo usuário no Obsidian.
- `analyses/AAAA/MM/` — saída gerada pela CLI: uma análise por entrada e um
  relatório consolidado por mês/período.

Cada entrada de diário precisa ter front-matter YAML com (no mínimo) o campo
`data`; os demais campos de hábito são opcionais e tolerados ausentes:

```yaml
---
data: 2026-09-03
tags: [diario]
processado: false
mit: tarefa importante do dia
sono: 7
estresse: 3
energia_humor: 4
hidratacao: 6
sol_manha: true
atividade_fisica: false
leitura: true
estudo: false
---

## Brain Dump
Texto livre da entrada...
```

Ver [`docs/template-diario.md`](../docs/template-diario.md) para o template completo
usado no plugin Templates do Obsidian, e
[`docs/obsidian-setup.md`](../docs/obsidian-setup.md) para a configuração do vault.

## Uso da CLI

### `analisar`

Analisa uma única entrada de diário e grava o resultado em `analyses/`.

```bash
uv run diario-tcc analisar <caminho/para/entrada.md>
```

Exemplo:
```bash
uv run diario-tcc analisar /caminho/vault/diary/2026/09/2026-09-03.md
```

O comando imprime o caminho do arquivo de análise gerado e atualiza a nota de
origem, marcando `processado: true` e inserindo uma seção de resumo.

**Flags disponíveis** (todas opcionais, sobrepõem o `.env`):

| Flag | Descrição |
|---|---|
| `--provider` | Provider de LLM (`fake` ou `gemini`). |
| `--api-key` | Chave de API do provider. |
| `--model` | Modelo do provider. |
| `--vault-path` | Caminho raiz do vault. |

### `relatorio`

Gera um relatório consolidado para um intervalo de datas, cobrindo todas as
entradas de diário nesse período.

```bash
uv run diario-tcc relatorio --de 2026-09-01 --ate 2026-09-30
```

**Flags disponíveis:**

| Flag | Obrigatória | Descrição |
|---|---|---|
| `--de` | Sim | Data inicial do período (`AAAA-MM-DD`). |
| `--ate` | Sim | Data final do período (`AAAA-MM-DD`). |
| `--provider` | Não | Provider de LLM. |
| `--api-key` | Não | Chave de API do provider. |
| `--model` | Não | Modelo do provider. |
| `--vault-path` | Não | Caminho raiz do vault. |
| `--forcar` | Não | Recalcula todas as análises do período, ignorando análises já persistidas. |

## Reaproveitamento de análises

`relatorio` reaproveita automaticamente a análise já existente de cada entrada
(quando o arquivo de análise correspondente já foi gerado), evitando chamar o
LLM novamente para entradas já processadas. Use `--forcar` para ignorar esse
cache e recalcular tudo — por exemplo, depois de trocar de provider/modelo e
querer análises consistentes com o novo LLM.

## Providers de LLM suportados

- **`fake`** — `FakeLLMAdapter`, não faz chamadas externas; útil para testar o
  fluxo de ponta a ponta (CLI, leitura/escrita do vault) sem custo ou chave de API.
- **`gemini`** — `GeminiAdapter`, usa a API do Google Gemini (`google-genai`) com
  saída estruturada validada por schema Pydantic.

Suporte a **OpenAI** está desenhado mas ainda não implementado — o registro de
providers em `config.py` é extensível via `register_provider(nome, factory)` sem
precisar alterar o código existente; ver comentário em `config.py` para os
passos de adição.

## Rodando os testes

```bash
uv run pytest -q
```

Lint estático (opcional, requer `ruff` instalado):
```bash
ruff check src
```

## Arquitetura

O código segue Clean Architecture com camadas `domain/`, `ports/`, `formatters/`
(funções puras), `use_cases/`, `infrastructure/` e `cli/` (composition root).
Detalhes em [`docs/architecture.md`](../docs/architecture.md) e nas decisões
técnicas em [`docs/decisions.md`](../docs/decisions.md).
