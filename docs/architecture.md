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

### 2.1 CLI
Ponto de entrada. Comandos principais:
- `analisar --arquivo <path>` — processa uma entrada individual.
- `relatorio --de <data> --ate <data>` — consolida múltiplas entradas em relatório periódico.

### 2.2 Leitor/Parser de Markdown
Responsável por ler o arquivo do diário e extrair o conteúdo textual relevante
(ignorando front-matter/metadados do Obsidian quando presentes).

### 2.3 LLM Adapter
Camada de abstração entre o core do sistema e o provedor de LLM. Define uma interface
comum (ex: `analisar(texto: string): AnaliseResult`) implementada por adapters específicos
(Claude, OpenAI, e futuramente modelo local via Ollama).

Objetivo: trocar de provedor alterando apenas configuração, sem tocar no core.

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
- Possível interface web/mobile consumindo o mesmo core.
