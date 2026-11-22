# Stack Tecnológica (v2)

## 1. Propósito

Descreve a stack escolhida e como ela atende à `specification.md`. A especificação não
prescreve tecnologia (ADR-028); as escolhas e seus motivos estão em `decisions.md`.

## 2. Decididas

| Tecnologia | Papel | Atende | Decisão |
| ---------- | ----- | ------ | ------- |
| LangChain | Acesso ao LLM, multi-provedor (Claude, Gemini, OpenAI etc.), selecionável por configuração | RF11, RNF02 | ADR-025 |
| LangGraph | Orquestração do fluxo de processamento | RF02, RF15 (fluxo detalhado em `architecture.md`) | ADR-026 |

## 3. Herdadas da v1 (a confirmar)

| Tecnologia | Uso na v1 | Atende |
| ---------- | --------- | ------ |
| Python ≥ 3.11 | Linguagem | n/a |
| uv | Gestão de dependências e ambiente | n/a |
| Pydantic | Validação da saída estruturada do LLM | ADR-010 |
| Typer | Interface de linha de comando | RNF04 |
| python-frontmatter | Leitura do front-matter das entradas | RF12 |
| pytest | Testes | n/a |

## 4. Em aberto

- Mecanismo de saída estruturada no LangChain [verificar].
- Substituto do fake de LLM para testes (ADR-017).
- Ferramenta de avaliação (RNF08–RNF12) [a decidir].
- Rastreamento (tracing) de chamadas: o que seria enviado para fora do ambiente local,
  considerando RNF01 [a decidir].

## 5. Versões

Fixar após conferir a documentação atual de LangChain e LangGraph [verificar]. As duas
bibliotecas mudam rápido; não usar versões de memória.
