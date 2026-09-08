# Roadmap

## v1 (atual — escopo definido em specification.md)
- [ ] CLI para análise individual de entrada.
- [ ] CLI para relatório de período (diário/semanal/mensal), com guarda de dado mínimo.
- [ ] CLI para relatório de tendência (trimestral/semestral/anual), agregando sub-períodos.
- [ ] LLM Adapter com suporte a pelo menos um provedor de API.
- [ ] Biblioteca de prompts guiados e de análise.
- [ ] Triagem de risco independente, com bloco de segurança determinístico (ADR-022).
- [ ] Rodapé fixo de limite de papel em toda saída (não gerado pelo LLM).
- [ ] Documentação (README, specification, architecture, prompts, decisions, obsidian-setup).

## v2 (planejado)
- [ ] Automação: watch de pasta do Obsidian, processamento automático de novas entradas.
- [ ] Adapter para modelo local (Ollama), permitindo uso 100% offline.
- [ ] Configuração via arquivo único (`config.yaml`) com validação.
- [ ] Distinção entre pensamento automático pontual e preocupação/ruminação cíclica
      (Terapia Metacognitiva, Wells — ver theoretical-background.md §3.4).

## v3 (exploratório)
- [ ] Exportação de relatório em formato adequado para compartilhar com psicólogo (ex: PDF).
- [ ] Painel simples de visualização de tendências (opcional, fora do core CLI).
- [ ] Possível interface web/mobile consumindo o mesmo core.
- [ ] Investigar classificador de risco dedicado e validado clinicamente, complementando
      a triagem atual baseada no LLM genérico (ver decisions.md ADR-022).

## Não planejado (fora de escopo indefinidamente)
- Produto comercial multiusuário.
- Armazenamento em nuvem próprio (mantém-se local/Obsidian).
