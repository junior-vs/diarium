# Roadmap

## v1 (atual — escopo definido em specification.md)
- [ ] CLI para análise individual de entrada.
- [ ] CLI para relatório consolidado.
- [ ] LLM Adapter com suporte a pelo menos um provedor de API (Claude ou OpenAI).
- [ ] Biblioteca de prompts guiados e de análise.
- [ ] Documentação (README, specification, architecture, prompts, decisions, obsidian-setup).

## v2 (planejado)
- [ ] Automação: watch de pasta do Obsidian, processamento automático de novas entradas.
- [ ] Adapter para modelo local (Ollama), permitindo uso 100% offline.
- [ ] Configuração via arquivo único (`config.yaml`) com validação.

## v3 (exploratório)
- [ ] Exportação de relatório em formato adequado para compartilhar com psicólogo (ex: PDF).
- [ ] Painel simples de visualização de tendências (opcional, fora do core CLI).
- [ ] Possível interface web/mobile consumindo o mesmo core.
- [ ] Investigar classificador de risco dedicado e validado clinicamente, complementando
      a triagem atual baseada no LLM genérico (ver decisions.md ADR-022).

## Não planejado (fora de escopo indefinidamente)
- Produto comercial multiusuário.
- Armazenamento em nuvem próprio (mantém-se local/Obsidian).
