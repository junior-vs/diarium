# Registro de Decisões Técnicas (ADR)

## ADR-001: Markdown como formato de entrada e saída

**Data:** 2026-09-03
**Decisão:** Usar markdown puro como formato de entrada (diário) e saída (análise/relatório).
**Motivo:** Compatibilidade nativa com Obsidian, sem necessidade de banco de dados ou
formato proprietário. Facilita versionamento (git) e portabilidade.
**Alternativas consideradas:** Banco de dados local (SQLite), formato JSON estruturado.

## ADR-002: CLI sob demanda em vez de watch automático (v1)

**Data:** 2026-09-03
**Decisão:** v1 processa arquivos sob demanda via comando manual.
**Motivo:** Reduz complexidade inicial, evita dependência de processo em background,
dá controle explícito sobre quando enviar dados sensíveis à API externa.
**Revisão futura:** Watch automático fica no roadmap (ver roadmap.md).

## ADR-003: LLM Adapter (abstração de provedor)

**Data:** 2026-09-03
**Decisão:** Isolar chamadas ao LLM atrás de uma interface comum (adapter pattern).
**Motivo:** Requisito explícito de migração futura para modelo local (Ollama), sem
acoplar o core do sistema a uma API específica.
**Implicação:** Qualquer prompt/parsing específico de provedor fica encapsulado no adapter,
não no core.

## ADR-004: Sem interface gráfica própria (v1)

**Data:** 2026-09-03
**Decisão:** Obsidian atua como front-end de escrita/leitura; sistema é CLI puro.
**Motivo:** Foco do v1 é validar o motor de processamento LLM, não a experiência de UI.

## ADR-005: Template orientado a baixa carga cognitiva (design para TDAH)

**Data:** 2026-09-03
**Decisão:** Substituir o modelo narrativo original (5 seções abertas, ABC/ABCDE obrigatório)
por um template com: brain dump livre, prompts fixos curtos divididos em manhã/noite, e
ABC/ABCDE como seção opcional (só preenchida quando houver gatilho relevante).
**Motivo:** Journaling narrativo tradicional exige atenção sustentada e função executiva
altas, o que reduz adesão em perfil TDAH. Prompts fixos e baixa barreira de entrada
(regra dos 2 minutos) favorecem consistência de uso sobre completude do registro.
**Implicação:** O prompt de análise do LLM precisa lidar com entradas fragmentadas/curtas
sem exigir estrutura completa (ver prompts.md).

## ADR-006: Tracking de hábitos via front-matter estruturado

**Data:** 2026-09-03
**Decisão:** Rastrear hábitos (sono, estresse, energia/humor, hidratação, sol da manhã,
atividade física, leitura, estudo, MIT) como campos de front-matter, não como texto livre.
**Motivo:** Dados estruturados são lidos diretamente pelo CLI para o relatório consolidado,
sem depender de o LLM interpretar texto — mais confiável e mais barato (menos tokens).
Reduz também a carga de escrita: marcar um campo é mais rápido que descrever em texto.
**Nota:** Campos como sono e hidratação podem ser preenchidos a partir de dados de
dispositivo (celular/smartwatch) em vez de digitação manual, quando disponível.
**Alternativas consideradas:** Registrar hábitos em texto livre e deixar o LLM extrair —
descartado por gerar custo extra e risco de inconsistência na extração.

## ADR-007: Sem tabela de check-in redundante com front-matter

**Data:** 2026-09-03
**Decisão:** Manter os campos de hábito apenas uma vez no documento (checklist inline
próximo ao topo), refletindo os mesmos valores do front-matter, em vez de duplicar em
uma tabela visual separada.
**Motivo:** Preencher os mesmos dados em dois lugares (front-matter + tabela) gera trabalho
duplicado, o que vai contra o princípio de baixa fricção (ADR-005).

## ADR-009: Separação core + CLI desde o MVP

**Data:** 2026-09-03
**Decisão:** Estruturar o projeto Python em `core/` (lógica de negócio: parser, análise,
relatório, LLM adapter) separado de `cli/` (ponto de entrada). CLI chama apenas `core/`,
nunca contém regra de negócio.
**Motivo:** Mobile app e bot Telegram já estão planejados (roadmap v2/v3), não são
especulação. Separar agora tem custo baixo (organização de módulos) e evita reescrever
a lógica de análise quando um segundo ponto de entrada for adicionado.
**Alternativas consideradas:** CLI monolítico simples, refatorar depois — descartado
porque lógica de negócio tende a vazar para dentro do CLI se não isolada desde o início.

## ADR-010: Saída estruturada (JSON) do LLM, não texto livre

**Data:** 2026-09-03
**Decisão:** O `LLMAdapter` retorna dados estruturados (validados via Pydantic), usando
JSON schema / function calling do provedor, em vez de texto livre parseado por regex.
**Motivo:** Texto livre é frágil de parsear e falha silenciosamente. RF13 (correlacionar
hábitos com distorções no relatório) exige dados programáticos. Resposta fora do schema
deve falhar de forma explícita, não ser aceita "quase certa".
**Implicação:** `docs/prompts.md` deve refletir os prompts como parte de uma chamada com
schema/function definido, não apenas texto de instrução solto.

## ADR-011: Gemini como primeiro provedor de LLM

**Data:** 2026-09-03
**Decisão:** Implementar `GeminiAdapter` como primeira implementação concreta de
`LLMAdapter` (via SDK `google-generativeai`), suportando saída estruturada nativamente.
**Motivo:** Escolha do usuário para o MVP. Suporte nativo a `response_schema` facilita
ADR-010 sem lógica adicional de parsing.
**Implicação:** Segundo provedor (ex: OpenAI, Claude) deve ser adicionado apenas como
novo adapter implementando a mesma interface — sem alterar os casos de uso ou o
domínio.

## ADR-012: Uso mínimo de plugins de terceiros no Obsidian

**Data:** 2026-09-03
**Decisão:** Configuração do vault prioriza plugins core (Daily notes, Templates, Tags,
Search, Backlinks), evitando Dataview, Templater e afins.
**Motivo:** Processamento e agregação de dados ficam no CLI externo; o Obsidian atua
apenas como editor/visualizador. Reduz superfície de dependência e manutenção.

## ADR-013: Status da entrada e atualizações determinísticas por append

**Data:** 2026-09-03
**Decisão:** O status canônico da nota diária passa a ser `processado`. Ao atualizar notas
ou saídas geradas, o sistema deve preservar o conteúdo existente e anexar novas seções
determinísticas no fim do arquivo, em vez de reescrever o documento inteiro.
**Motivo:** O status deve refletir claramente a etapa concluída do fluxo, e o append-only
reduz risco de perda de conteúdo autoral ao registrar novas análises ou notas geradas.

## ADR-014: Layout canônico do vault por ano e mês

**Data:** 2026-09-03
**Decisão:** O layout canônico do vault passa a ser `diary/YYYY/MMMM` para notas diárias e
`analyses/YYYY/MMMM` para análises e relatórios.
**Motivo:** A organização por ano e nome do mês facilita navegação manual no Obsidian,
mantém os arquivos agrupados por período e simplifica a filtragem do CLI por intervalo.

## ADR-015: Relatórios e análises a partir das notas brutas

**Data:** 2026-09-03
**Decisão:** O CLI deve usar as notas brutas como fonte de verdade para gerar análises e
relatórios. Ao encontrar saídas pré-existentes, deve avisar o usuário e regenerar o conteúdo
a partir das notas de origem, em vez de depender das saídas antigas como base principal.
**Motivo:** Evita acúmulo de resultados derivados como fonte secundária e garante que a
consolidação reflita a versão mais recente das entradas do diário.

## ADR-016: Prompts como ativos de código versionados separadamente

**Data:** 2026-09-03
**Decisão:** Os prompts deixam de ser tratados como texto narrativo genérico de documentação e
passam a ser considerados ativos de fonte, versionados separadamente da implementação.
**Motivo:** Mudanças de prompt são parte do comportamento do sistema e precisam ficar
auditáveis sem se misturar a refatorações de código.

## ADR-017: Adapter primeiro com implementação fake para testes

**Data:** 2026-09-03
**Decisão:** A primeira etapa de integração do LLM deve priorizar o adapter com uma
implementação fake/mock para testes, antes de conectar o provedor real.
**Motivo:** Permite validar parser, análise e relatório sem depender de API externa, reduzindo
custo e ruído durante a construção do core.

## ADR-018: Bloco de gatilho repetível e timestampado

**Data:** 2026-09-06
**Decisão:** A seção "Registro de Gatilho" deixa de ser única e opcional por nota diária
e passa a ser um bloco repetível, inserido com timestamp a qualquer momento do dia
(via comando nativo "Insert template" do Obsidian, não pela criação da nota). A nota
diária pode conter zero, um ou múltiplos blocos de gatilho, cada um com seu horário.
**Motivo:** Entrevista de necessidade (JTBD) identificou que o gatilho de uso principal
do sistema é a crise de ansiedade em si — não a reflexão noturna. Pensamento automático
relatado horas depois sofre reconstrução retrospectiva e perde fidelidade clínica;
capturar no calor do momento preserva o dado que tem valor terapêutico real. Uma seção
única por dia não comporta múltiplas crises no mesmo dia nem preserva o horário de cada
uma, informação necessária para correlação (RF13).
**Implicação:** Estrutura interna do campo (Evento/Pensamento/Emoção) permanece igual —
validado como suficiente mesmo em estado de crise. Muda apenas a cardinalidade (1→N por
dia) e a necessidade de timestamp por ocorrência. Não introduz plugin novo nem automação
(mantém ADR-002 e ADR-012): usa "Insert template" nativo com hotkey, aplicado com o
cursor já posicionado na nota do dia em aberto.
**Impacto em outros artefatos:**

- `template-diario.md`: seção de gatilho vira exemplo de bloco repetível.
- Novo `templates/gatilho-rapido.md`: template parcial para inserção pontual.
- `prompts.md` §2: prompt de análise deve assumir N blocos de gatilho por entrada,
  cada um estruturado em ABC/ABCDE independentemente.
- `obsidian-setup.md`: documentar fluxo de "Insert template" + hotkey.
**Alternativas consideradas:** Manter seção única e aceitar perda de granularidade —
descartado por comprometer diretamente RF13 e o job principal identificado na entrevista.
Nota separada por gatilho (fora da nota do dia) — descartado por fragmentar a fonte de
verdade e complicar o parsing do CLI sem ganho claro sobre o append timestampado.

## ADR-019: Campo "Comportamento" no bloco de gatilho

**Data:** 2026-09-06
**Decisão:** O bloco de gatilho (ver ADR-018) ganha um quarto campo, "Comportamento",
registrando o que a pessoa fez ou evitou fazer em resposta ao evento/pensamento/emoção.
Estrutura final do bloco: Evento, Pensamento, Emoção, Comportamento.
**Motivo:** O modelo ABC de Ellis captura o eixo cognitivo-emocional mas deixa implícita
a "consequência comportamental" — nunca é um campo preenchível, depende do LLM inferir
de texto livre (se presente). A manutenção de ansiedade por reforço negativo (Mowrer,
1960) e comportamentos de segurança (Salkovskis, 1991) — ver `theoretical-background.md`
§2 — só é visível se o comportamento de resposta (evitação, checagem, busca de
reasseguramento) for registrado explicitamente, não inferido. Sem esse dado, o sistema
vê o "instantâneo" emocional mas não o ciclo que mantém o padrão ao longo do tempo.
**Implicação:** Validado com o usuário que 4 campos ainda são aceitáveis em estado de
crise (mesmo nível de fricção percebido dos 3 campos anteriores). Prompt de análise
(`prompts.md` §2) e templates (`template-diario.md`, `templates/gatilho-rapido.md`)
precisam refletir o campo adicional.
**Nota terminológica:** este "Comportamento" não transforma o bloco no ABC funcional de
Skinner (Antecedent-Behavior-Consequence) — os dois modelos coexistem na mesma entrada,
mas descrevem coisas diferentes (crença vs. reforço). Ver `theoretical-background.md` §2
para a distinção completa.
**Alternativas consideradas:** Deixar o LLM inferir comportamento do texto livre do
Evento/Pensamento — descartado por já ter sido a motivação de ADR-010 (dado estruturado
> parseamento de texto livre) e por comportamento de segurança sutil raramente aparecer
explícito em texto não solicitado.

## ADR-020: Dispute (D) como perguntas socráticas, não resposta pronta

**Data:** 2026-09-06
**Decisão:** Por padrão, o LLM Adapter não resolve o campo D (Dispute) do ABCDE com uma
resposta pronta. Em vez disso, gera de 2 a 3 perguntas socráticas abertas por bloco de
gatilho, deixando o questionamento da crença como processo do próprio usuário. O campo
E (Effect) permanece em aberto na análise automática, já que depende da resposta do
usuário às perguntas de D, ainda inexistente no momento da análise. Uma variante que
resolve D/E diretamente é mantida como opção de configuração não-padrão, não como
comportamento default.
**Motivo:** Evidência de questionamento socrático (Padesky, 1993) e empirismo
colaborativo (Beck) mostra que o mecanismo terapêutico do D depende de a conclusão ser
auto-gerada pelo cliente, não entregue por uma autoridade externa — reforçado pelo
efeito de auto-geração (Slamecka & Graf, 1978) da psicologia cognitiva geral. Um D
resolvido unilateralmente pelo LLM também apaga o dado clinicamente mais valioso pro
psicólogo: o ponto exato onde a pessoa trava ao tentar questionar a própria crença.
Ver `theoretical-background.md` §2.
**Implicação:** `prompts.md` §2 reformulado — D vira geração de perguntas, não resposta;
E fica em aberto. A resposta do usuário às perguntas (quando houver) fica registrada
como nova entrada / bloco subsequente, não como parte da análise automática original.
**Alternativas consideradas:** Manter D/E resolvidos automaticamente como padrão —
descartado por contrariar o mecanismo de mudança que a própria técnica pretende ativar,
e por reduzir o valor do dado levado à sessão de terapia (RF04, critério de sucesso do
usuário identificado na entrevista JTBD).

## ADR-021: Observação de tema recorrente em vez de rotulagem de schema

**Data:** 2026-09-06
**Decisão:** O relatório consolidado pode evidenciar que o mesmo conteúdo de crença
aparece em situações/entradas superficialmente diferentes ao longo do período, mas o
sistema não atribui esse padrão a um nome de schema de nenhuma taxonomia clínica (ex:
os 18 Early Maladaptive Schemas de Young). A saída descreve o padrão observado em
linguagem simples e o formula como pergunta aberta para reflexão do usuário — nunca
como conclusão fechada ou rótulo.
**Motivo:** Crença nuclear (schema) é normalmente acessada por técnica de diálogo
iterativo (seta descendente, Burns 1980) e/ou instrumento validado de ~200 itens (Young
Schema Questionnaire) interpretado clinicamente. Um LLM inferindo isso a partir de
fragmentos de diário de algumas semanas, em análise batch (sem diálogo responsivo), faz
um salto de validade sem lastro. Rotular alguém com um schema tem risco equivalente ou
maior que um diagnóstico: pode ancorar prematuramente a autopercepção da pessoa a um
rótulo impreciso. Ver `theoretical-background.md` §5.
**Implicação:** `prompts.md` §3 (consolidação) ganha item de "tema recorrente", com
instrução explícita de não nomear schema e de formular como pergunta, não afirmação.
`specification.md` ganha RF14 registrando esse requisito e um risco correspondente na
seção 7.
**Alternativas consideradas:** Mapear diretamente para a taxonomia de Young (18
schemas) — descartado por exigir instrumento validado que o projeto não usa, e por
converter observação em rótulo clínico, contrariando a postura de não-diagnóstico já
estabelecida no projeto (seção 9 de `theoretical-background.md`, AGENTS.md).

## ADR-022: Triagem de risco separada da análise TCC, com resposta de segurança determinística

**Data:** 2026-09-06
**Decisão:** O `LLMAdapter` ganha um método dedicado de triagem de risco (ex:
`screen_risk(text) -> RiskScreeningResult`), executado ANTES e independentemente de
`analyze_entry`, para qualquer texto de entrada (incluindo cada bloco de gatilho
isoladamente). O resultado é um campo estruturado e validado (enum `sem_indicio` /
`possivel_risco`), nunca texto livre. Quando `possivel_risco` é retornado, o CLI insere
deterministicamente — via código, não via saída do LLM — um bloco de segurança fixo e
pré-revisado, com recursos de ajuda, no topo da análise gerada. A análise TCC da
entrada continua rodando normalmente; o bloco de segurança é adicionado, não substitui
a saída existente.
**Motivo:** Ver `theoretical-background.md` §10. Misturar triagem de risco na mesma
chamada que identifica distorções cognitivas expõe uma decisão de segurança à mesma
fragilidade de texto livre já resolvida para o restante do sistema em ADR-010 — mas
aqui uma falha silenciosa tem consequência mais grave. O conteúdo de resposta não deve
ser gerado pelo LLM a cada chamada: precisa ser fixo, revisado previamente, e
controlado pelo código, para garantir consistência e evitar respostas inadequadas ou
alarmistas.
**Implicação:**

- Novo campo estruturado para o resultado de triagem (schema irmão de `AnalysisResult`,
  validado via Pydantic, ver ADR-010).
- Limiar de decisão deliberadamente conservador (favorece falso positivo sobre falso
  negativo) — ver `theoretical-background.md` §10.
- O bloco de segurança é conteúdo estático, versionado como ativo do projeto (mesmo
  princípio de ADR-016 para prompts) — ver `bloco-seguranca.md`.
- `specification.md` ganha RF15, RF18 e RNF06 formalizando o requisito.
- Documentar explicitamente que o sistema NÃO é uma ferramenta de intervenção em tempo
  real (ADR-002 já implica isso, mas aqui a implicação é mais sensível e merece estar
  explícita).
**Alternativas consideradas:** Deixar a triagem de risco como parte implícita do prompt
de análise geral — é o comportamento atual, e é exatamente o gap que motivou este ADR.
Delegar a triagem a um classificador de risco dedicado e validado clinicamente (fora do
LLM Adapter) — desejável a longo prazo, mas fora do escopo do MVP; fica registrado como
direção futura (ver roadmap.md).
