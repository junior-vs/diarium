# Especificação do Projeto: Diário TCC Assistido por LLM

## 1. Visão Geral
Sistema para processar diários pessoais (escritos em Markdown no Obsidian) usando um LLM,
aplicando abordagem TCC (Terapia Cognitivo-Comportamental) para identificar possíveis
padrões de pensamento e estruturar registros no modelo ABC/ABCDE. Uso pessoal, com output
também aproveitável pelo psicólogo do usuário.

O Diarium é um **registro estruturado de pensamentos** (thought record) com acúmulo
longitudinal de diário narrativo livre — não é uma implementação de *expressive writing*
(Pennebaker) nem reivindica seus efeitos, que na literatura são pequenos e heterogêneos
(`theoretical-background.md` §6).

## 2. Objetivos
- Ajudar o usuário a registrar e refletir sobre pensamentos/eventos diários, com baixa
  carga cognitiva (perfil TDAH), sem apresentar isso como tratamento (§7).
- Identificar possíveis padrões de pensamento nos registros como hipóteses de
  investigação, nunca como classificação definitiva (§4).
- Estruturar entradas livres no modelo ABC/ABCDE quando aplicável, sem apresentar essa
  estrutura como equivalente ao modelo cognitivo de Beck (§1.2).
- Executar triagem de risco separada da análise cognitiva, como requisito de segurança
  não-negociável (§10).
- Gerar relatórios de período e de tendência com correlações formuladas como associação
  observada, nunca como causalidade (§8.6).
- Garantir, de forma determinística (não dependente do LLM), que toda saída deixe claro
  seu limite de papel (§9).

## 3. Escopo (v1 — conforme `roadmap.md`)

### Incluso
- CLI para análise individual de entrada (`diario-tcc analisar`).
- CLI para relatório de período, com presets diário/semanal/mensal (`diario-tcc relatorio`).
- CLI para relatório de tendência, para intervalos longos (trimestral/semestral/anual).
- LLM Adapter com suporte a pelo menos um provedor de API, isolado por interface.
- Biblioteca de prompts guiados (registro) e de análise/consolidação.
- Triagem de risco separada da análise TCC, com bloco de segurança determinístico.
- Rodapé de limite de papel, fixo e incondicional, em toda saída.
- Template de diário com front-matter estruturado para hábitos (sono, energia, estresse,
  hidratação, sol, atividade física, leitura, estudo, MIT) e ativação comportamental
  (atividade + prazer/domínio percebido), como variáveis de contexto autorrelatadas.
- Bloco opcional de Positive Data Log.
- Status canônico da entrada diária: `processado`.

### Fora do escopo (v1)
- Automação/watch de pasta (ADR-002; v2).
- App mobile/web dedicado; interface gráfica própria (usa Obsidian como front-end).
- Modelo local (Ollama) (v2).
- Distinção entre pensamento automático pontual e processos cíclicos de
  preocupação/ruminação (Terapia Metacognitiva, Wells — §3.4). Fundamentação já
  registrada na teoria, sem requisito funcional correspondente neste v1.
- Classificador de risco validado clinicamente fora do LLM genérico (v3).

## 4. Requisitos Funcionais
| ID | Requisito |
|----|-----------|
| RF01 | O sistema deve ler um arquivo markdown de entrada (diário) via caminho informado pelo usuário. |
| RF02 | O sistema deve enviar o conteúdo ao LLM configurado via API, com prompt estruturado para análise TCC. |
| RF03 | O sistema deve identificar possíveis distorções cognitivas, citando o trecho correspondente, e apresentá-las como hipótese ("pode haver um padrão de..."), nunca como diagnóstico. A contagem/frequência é dado descritivo, não indicador de gravidade clínica (§4.2–§4.4). |
| RF04 | O sistema deve estruturar cada ocorrência de gatilho da entrada (podendo haver mais de uma por dia, timestampada) no modelo ABC/ABCDE, incluindo Comportamento (evitação, comportamento de segurança). A função hipotética desse comportamento deve ser formulada como pergunta investigativa, nunca como afirmação categórica (§3.3, §3.6). Por padrão, D é gerado como 2–3 perguntas socráticas abertas; E permanece em aberto. |
| RF05 | O sistema deve gerar um arquivo markdown de saída com a análise, salvo em local configurável. |
| RF06 | O sistema deve permitir gerar relatório de período a partir de múltiplas entradas, com intervalo configurável livremente e presets de conveniência (diário, semanal, mensal). Processa as entradas do intervalo diretamente. |
| RF07 | Para intervalos longos (preset trimestral, semestral, anual, ou intervalo customizado acima de um limiar configurável, ex: 45 dias), o sistema deve gerar um relatório de tendência: agrega sobre sub-períodos já processados (não entradas brutas) e evidencia variação entre eles (ex: tema mais/menos presente, mudança na correlação hábito-humor). Segue a mesma restrição de linguagem de RNF07 ("apareceu com mais frequência", nunca "piorou"/"causou"). |
| RF08 | O relatório de tendência depende de sub-períodos já processados; se faltarem, o sistema deve indicar quais em vez de agregar dados incompletos silenciosamente. |
| RF09 | As seções de correlação de hábitos (RF13) e tema recorrente (RF14) só devem ser geradas quando o número de entradas do período/sub-período atingir um mínimo configurável (default: 5). Abaixo disso, indicar "dados insuficientes" explicitamente. |
| RF10 | O sistema deve oferecer prompts guiados (biblioteca pré-definida) para auxiliar o usuário a escrever a entrada. |
| RF11 | O provedor de LLM deve ser configurável (API key + endpoint/modelo), permitindo troca futura sem alterar o core. |
| RF12 | O sistema deve ler campos estruturados do front-matter (hábitos, humor, sono, etc.) para compor os relatórios, sem depender do LLM para extrair esses dados. |
| RF13 | Os relatórios devem relacionar hábitos rastreados (sono, estresse, energia) com padrões emocionais/distorções do período, usando exclusivamente linguagem de associação observada. Nunca linguagem causal ou mecanismo neurobiológico (§8.6). |
| RF14 | Os relatórios devem evidenciar temas ou crenças recorrentes por trás de distorções/situações aparentemente distintas, como observação para reflexão (pergunta aberta), nunca como rótulo clínico, nome de schema ou crença nuclear (§5.5, ADR-021). |
| RF15 | O sistema deve executar triagem de risco de forma independente da análise de distorções, para cada entrada e cada bloco de gatilho. Ao detectar possível risco, inclui um bloco de segurança fixo e pré-revisado (não gerado pelo LLM), sem suprimir a análise normal. Parte do escopo v1, não um adicional pós-lançamento (§10, ADR-022). |
| RF16 | O sistema deve registrar, via front-matter, a atividade mais significativa do dia e níveis de prazer e domínio percebidos (escala 0-5), e os relatórios devem correlacionar esses dados com humor/estresse (ativação comportamental), seguindo a mesma restrição de linguagem de RF13. |
| RF17 | O sistema deve oferecer uma seção opcional de preenchimento livre para registrar evidências que contrariem um pensamento negativo recorrente (positive data log), não obrigatória. |
| RF18 | Toda saída do sistema (análise individual, relatório de período, relatório de tendência) deve incluir um rodapé fixo, não gerado pelo LLM, reafirmando: (1) o conteúdo é hipótese de investigação, não diagnóstico; (2) o sistema não substitui avaliação ou acompanhamento profissional. Incondicional — independente do bloco de RF15, que é condicional a risco detectado. |

## 5. Requisitos Não-Funcionais
| ID | Requisito |
|----|-----------|
| RNF01 | Dados sensíveis (diários) não devem ser persistidos fora do ambiente local do usuário, exceto na chamada à API do LLM. |
| RNF02 | Arquitetura deve isolar a camada de LLM (adapter/interface) para permitir troca de provedor sem refatoração ampla. |
| RNF03 | Formato de entrada/saída deve ser markdown puro, compatível com Obsidian. |
| RNF04 | Execução via linha de comando (CLI), sem dependência de interface gráfica própria. |
| RNF05 | O template de entrada deve minimizar carga cognitiva e função executiva exigida. Hipótese de design orientada a TDAH, não alegação de eficácia clínica (§7.2, §7.4). |
| RNF06 | O sistema não deve se apresentar como ferramenta de resposta a emergências em tempo real — a triagem ocorre apenas quando o CLI é executado sob demanda (ADR-002). |
| RNF07 | Toda saída interpretativa do LLM (RF03, RF04, RF13, RF14) deve seguir linguagem epistêmica hedged (hipótese revisável, pergunta, associação observada), nunca linguagem categórica, causal ou de conclusão clínica fechada (§3.6, §4.2, §5.5, §8.6, §9). |

## 6. Critérios de Aceite
- Rodar o comando sobre um arquivo de diário gera análise coerente com TCC, sem linguagem categórica ou causal, terminando no rodapé de RF18.
- Uma entrada com conteúdo de risco simulado produz saída com o bloco de segurança de `bloco-seguranca.md` no topo, análise normal preservada abaixo, e o rodapé de RF18 ao final.
- Relatório de período com menos de 5 entradas indica "dados insuficientes" nas seções de correlação/tema, em vez de omiti-las ou forçar conclusão.
- Relatório de tendência sobre um semestre com sub-períodos mensais faltantes indica quais faltam, em vez de agregar parcialmente sem aviso.
- Nenhuma saída do sistema nomeia schema clínico, crença nuclear ou diagnóstico.
- Trocar o provedor de LLM (via config) não exige alteração no código core.

## 7. Riscos / Pontos de Atenção
- **Privacidade:** conteúdo sensível trafega para API externa.
- **Qualidade clínica:** análise de LLM não substitui avaliação profissional — reforçado estruturalmente por RF18, não apenas por instrução de prompt.
- **Rotulagem indevida:** RF14 não deve nomear schema/crença nuclear.
- **Causalidade indevida:** RF13/RF16 não devem sugerir causa ou mecanismo neurobiológico.
- **Detecção tardia de risco:** RF15 só age quando o CLI roda (RNF06).
- **Drift prompt-vs-documentação:** já observado neste projeto (D resolvido em vez de socrático em `analysis.txt`) — recomenda-se teste de sincronização doc↔prompt real como salvaguarda de RNF07.
