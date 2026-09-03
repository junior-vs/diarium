# Diário TCC Assistido por LLM

Sistema para processar diários pessoais (escritos em Markdown no Obsidian) usando um LLM,
aplicando abordagem TCC (Terapia Cognitivo-Comportamental).

## O que faz
- Lê entradas de diário em markdown.
- Envia para um LLM configurável (API) com prompts de análise TCC.
- Identifica distorções cognitivas e estrutura o registro no modelo ABC/ABCDE.
- Gera relatórios periódicos consolidados.

## Uso
```bash
# Analisar uma entrada
diario-tcc analisar --arquivo caminho/para/entrada.md

# Gerar relatório consolidado
diario-tcc relatorio --de 2026-08-01 --ate 2026-08-31
```

## Configuração
Ver seção de configuração em `architecture.md` para setup de API key e provedor de LLM.

## Documentação
- [specification.md](./specification.md) — requisitos e escopo
- [architecture.md](./architecture.md) — arquitetura técnica
- [prompts.md](./prompts.md) — biblioteca de prompts TCC
- [decisions.md](./decisions.md) — decisões técnicas (ADR)
- [roadmap.md](./roadmap.md) — evolução planejada
- [obsidian-setup.md](./obsidian-setup.md) — configuração do vault no Obsidian

## Aviso
Este sistema não substitui acompanhamento profissional. É uma ferramenta de apoio
ao autoconhecimento e ao processo terapêutico.
