## Fundamentação Teórica: Diário TCC Assistido por LLM

### 1. Terapia Cognitivo-Comportamental (TCC) — princípios centrais

A TCC parte da premissa de que não são os eventos em si que geram sofrimento emocional, mas a **interpretação** que fazemos deles. Esse é o núcleo do modelo cognitivo de Aaron Beck (anos 1960-70) e da Terapia Racional Emotiva de Albert Ellis, que deu origem ao modelo **ABC**:

- **A (Activating Event)** — o evento ativador, a situação objetiva.
- **B (Belief)** — a crença ou pensamento automático sobre o evento.
- **C (Consequence)** — a consequência emocional e comportamental.

Ellis expandiu o modelo para **ABCDE**, adicionando:
- **D (Dispute)** — o questionamento ativo da crença disfuncional (evidências a favor/contra).
- **E (Effect)** — o novo efeito emocional/comportamental resultante da crença revisada.

O pressuposto clínico é que a crença (B), não o evento (A), é o alvo de intervenção — e que ela pode ser identificada, questionada e substituída. É esse pressuposto que justifica pedir ao usuário (ou ao LLM) para separar "o que aconteceu" de "o que pensei sobre isso".

### 2. Questionamento socrático e o mecanismo de mudança em D

O "D" (Dispute) do ABCDE é frequentemente mal-entendido como o terapeuta (ou, neste projeto, o LLM) apresentando um contra-argumento pronto para a crença disfuncional. Clinicamente, isso inverte o mecanismo que faz o D funcionar.

**Guided discovery vs. persuasão didática:** Padesky (1993), em texto seminal sobre questionamento socrático em TCC, distingue perguntas que guiam a descoberta do próprio cliente (informativas, de escuta empática, de síntese, e por fim perguntas analíticas que levam a uma nova conclusão) de perguntas retóricas que já embutem a resposta certa. Beck descreve o mesmo princípio como **empirismo colaborativo** — terapeuta e cliente como coinvestigadores testando uma hipótese, não o terapeuta como autoridade que corrige o pensamento do cliente.

**Por que a auto-geração importa (evidência fora da clínica):** o efeito de auto-geração (Slamecka & Graf, 1978), da psicologia cognitiva, mostra que informação gerada pela própria pessoa é retida e integrada de forma mais duradoura do que informação apresentada por terceiros — mesmo quando o conteúdo final é idêntico. Aplicado ao D: uma alternativa de pensamento que o próprio usuário constrói (respondendo a "qual evidência sustenta isso?", "o que eu diria a um amigo na mesma situação?") tem mais chance de se manter do que uma frase de reasseguramento entregue pronta, ainda que bem escrita.

**Risco clínico do "D automático":** um sistema que resolve o D unilateralmente corre dois riscos. Primeiro, infantiliza o processo — o "aha" que sustenta a mudança de crença vem do esforço de encontrar a evidência, não de recebê-la. Segundo, arrisca invalidação: uma resposta genérica pode não caber no raciocínio real da pessoa, e ferramentas automatizadas de TCC já são criticadas por esse tipo de superficialidade (ver seção 9, sobre limites do LLM).

**Implicação para o projeto:** a saída do LLM para o campo D não deveria ser uma resposta finalizada, mas 2-3 perguntas abertas — deixando o preenchimento como parte do processo do próprio usuário (ver `prompts.md`). Isso também preserva, como dado bruto para a sessão de terapia, o ponto exato onde a pessoa ficou presa — informação mais valiosa clinicamente do que uma resposta já resolvida.

### 3. O componente comportamental — o elo que falta na reestruturação cognitiva

A TCC não opera só no eixo pensamento-emoção; o modelo original é uma tríade cognitivo-comportamental, em que pensamento, comportamento e emoção se retroalimentam. Um sistema que só rastreia distorções e sentimentos captura dois terços do modelo.

**Por que a ansiedade se mantém (reforço negativo):** a teoria dos dois fatores de Mowrer (1960) explica que evitar uma situação temida reduz o desconforto imediatamente (reforço negativo), mas impede a desconfirmação da crença catastrófica — o medo nunca é testado contra a realidade, então persiste. A crença não se mantém forte por si só; o comportamento de evitação a protege de ser refutada.

**Comportamentos de segurança:** Salkovskis (1991) descreve uma versão mais sutil — mesmo sem evitar totalmente, a pessoa usa estratégias "de proteção" (checar o celular, ficar perto da saída, pedir reasseguramento) que impedem a mesma desconfirmação, porque o alívio é atribuído à estratégia, não ao fato de que o medo era infundado. É tão relevante quanto a evitação total e mais fácil de passar despercebido — inclusive pelo próprio paciente.

**Preocupação como evitação:** Borkovec (1998) propõe que ruminar sobre cenários hipotéticos é, funcionalmente, um comportamento de evitação verbal — evita o processamento emocional mais intenso de uma imagem ou memória concreta. Relevante para diferenciar brain dump (processamento) de ruminação (evitação disfarçada de processamento).

**Ativação comportamental (o ciclo inverso, ligado a humor/energia):** Lewinsohn (1974) e Jacobson, Martell & Dimidjian (2001) descrevem retraimento de atividades → menos reforço positivo disponível → humor mais baixo → mais retraimento. Dimidjian et al. (2006) mostraram que ativação comportamental isolada tem eficácia comparável à terapia cognitiva e à medicação em depressão moderada-grave — mudança de comportamento altera afeto por uma via independente da cognição. A variável clínica relevante não é "fez ou não fez" a atividade, mas prazer e domínio percebidos nela.

**Nota terminológica:** o ABC usado neste projeto é o de Ellis (Activating event – Belief – Consequence), um modelo cognitivo. Existe um ABC homônimo na análise do comportamento aplicada (Antecedent – Behavior – Consequence, Skinner), que é funcional — descreve o que reforça um comportamento, não uma crença. Os dois coexistem na mesma entrada quando um campo de comportamento é adicionado; tratar como modelos distintos evita confusão de quem for ler `prompts.md` ou o código depois.

### 4. Distorções cognitivas — o que o sistema procura identificar

Beck e, mais tarde, David Burns (*Feeling Good*, 1980) catalogaram padrões recorrentes de pensamento distorcido — atalhos cognitivos que parecem lógicos na hora, mas sistematicamente distorcem a realidade contra o próprio indivíduo:

- **Catastrofização** — assumir o pior desfecho possível.
- **Pensamento tudo-ou-nada** — avaliar em extremos, sem meio-termo.
- **Leitura mental** — presumir o que o outro está pensando, sem evidência.
- **Hipergeneralização** — extrapolar um evento isolado para um padrão universal ("sempre", "nunca").
- **Personalização** — atribuir a si a responsabilidade por eventos fora de controle.
- **Imperativos ("deveria/tenho que")** — regras rígidas autoimpostas que geram culpa desproporcional.

O papel do LLM no sistema não é apenas narrar o que a pessoa sentiu, mas **apontar o padrão** por trás da narrativa — o mesmo movimento que um terapeuta faz ao "nomear a distorção" numa sessão.

### 5. Níveis de crença: por que uma distorção pontual não é a mesma coisa que uma crença nuclear

O modelo cognitivo de Beck opera em três camadas, não duas. As seções 1 e 4 cobrem só a mais superficial:

- **Pensamentos automáticos** — a interpretação momentânea de uma situação específica (o "B" do ABC). É o que o LLM já analisa por entrada.
- **Crenças intermediárias** — regras condicionais e pressupostos mais estáveis que geram os pensamentos automáticos ("se eu falhar, isso prova que sou incompetente"; imperativos do tipo "devo sempre..."). Aparecem repetidas vezes, em situações diferentes, com a mesma estrutura condicional.
- **Crenças nucleares (core beliefs / schemas)** — crenças globais, rígidas e absolutas sobre si, os outros ou o mundo ("não sou capaz", "serei abandonado"), geralmente formadas na infância, normalmente latentes e ativadas só quando uma situação "casa" com o tema (Judith Beck, *Cognitive Therapy: Basics and Beyond*, 1995).

Uma distorção cognitiva (catastrofização, leitura mental etc.) é o *mecanismo* de erro; a crença nuclear é o *conteúdo temático* que se repete por trás de mecanismos diferentes. Uma pessoa pode catastrofizar sobre o trabalho numa semana e fazer leitura mental sobre um relacionamento na outra — mecanismos distintos, mas a mesma crença de fundo ("não sou capaz") pode estar operando nos dois. É essa camada que um relatório que só soma "distorções mais recorrentes" por tipo não enxerga.

**Como a crença nuclear normalmente é acessada — e por que isso importa pro desenho do sistema:** a técnica clássica é a *seta descendente* (Burns, 1980): perguntar repetidamente "se isso fosse verdade, o que isso diria sobre você?" a partir de um pensamento automático, descendo camada por camada até a crença nuclear. É, por definição, um processo de diálogo iterativo e responsivo — cada pergunta depende da resposta anterior. Isso não é replicável numa análise em lote (batch) de uma entrada estática; exigiria um LLM conversacional em tempo real, fora do escopo do CLI atual (ver ADR-002, ADR-004).

**Por que não usar uma taxonomia fechada de schemas:** Young (*Schema Therapy: A Practitioner's Guide*, 2003) cataloga 18 Esquemas Mal-Adaptativos Precoces (Early Maladaptive Schemas) organizados em 5 domínios, normalmente avaliados por um instrumento validado de ~200 itens (o Young Schema Questionnaire), preenchido pelo próprio paciente e interpretado clinicamente. Um LLM tentando mapear fragmentos de diário de algumas semanas para um desses 18 rótulos está fazendo um salto de validade que a ferramenta não tem lastro para sustentar — e rotular alguém com um "schema" tem o mesmo risco (ou maior) que um diagnóstico: pode ancorar prematuramente a autopercepção da pessoa a um rótulo que talvez nem seja preciso.

**Ajuste de escopo:** o valor real e alcançável para este projeto não é *nomear* a crença nuclear, mas *evidenciar o tema recorrente* — apontar, com base em dados, que o mesmo conteúdo aparece em situações superficialmente diferentes, sem convertê-lo em rótulo clínico. Isso segue o mesmo princípio já adotado para o "D" (ADR-020, seção 2): o sistema observa e devolve a pergunta ("isso te parece familiar?"), não entrega a conclusão. Aqui a observação é sobre conteúdo recorrente entre entradas ao longo do tempo, não sobre uma crença única dentro de uma entrada.

### 6. Journaling como técnica terapêutica — evidência e mecanismo

O registro escrito de pensamentos e emoções (*expressive writing*) tem respaldo empírico desde os estudos de James Pennebaker (anos 1980-90): escrever sobre experiências emocionalmente carregadas está associado a melhora de bem-estar psicológico e até indicadores fisiológicos de estresse, mesmo sem intervenção de um terapeuta.

Dentro da TCC especificamente, o "registro de pensamentos" (*thought record*) é uma das técnicas mais usadas — é essencialmente o modelo ABC aplicado à escrita diária, e frequentemente prescrito como tarefa entre sessões (*homework*), porque:
- Externaliza o pensamento automático, tornando-o observável (em vez de vivido como "verdade").
- Cria um registro histórico que permite ao terapeuta (ou à própria pessoa) identificar padrões ao longo do tempo — não apenas eventos isolados.
- Treina, por repetição, a habilidade de distanciar-se do próprio pensamento (defusão cognitiva).

Esse é o racional por trás do RF06 do projeto (relatório consolidado): o valor terapêutico não está só no registro individual, mas no padrão que emerge ao longo de semanas.

### 7. Por que o modelo tradicional de journaling falha no TDAH

O TDAH é caracterizado por prejuízo nas **funções executivas**: memória de trabalho, iniciação de tarefa, atenção sustentada e regulação de esforço (Barkley, *Executive Functions*, 2012). Um diário narrativo tradicional exige exatamente essas funções:
- Manter o fio da narrativa (memória de trabalho).
- Iniciar a tarefa sem procrastinar (iniciação).
- Sustentar atenção por texto longo (atenção sustentada).
- Organizar pensamento em frases coerentes (função executiva de planejamento).

Isso cria uma barreira de entrada alta — e a inconsistência de uso (abandonar o diário após dias) não é falta de disciplina, é a arquitetura da tarefa não encaixando no perfil cognitivo. Daí a decisão de projeto (ADR-005) de substituir a narrativa obrigatória por:
- **Brain dump** — reduz carga porque não exige estrutura nem coerência, apenas descarrega.
- **Prompts fixos curtos** — elimina a "paralisia da página em branco" (a decisão sobre o que escrever já está tomada).
- **Regra dos 2 minutos / MIT** — reduz a barreira de entrada ao ponto em que procrastinar custa mais esforço do que simplesmente fazer.

### 8. Rastreamento de hábitos e neuromodulação

A escolha das métricas do template (sono, luz solar, hidratação, estresse, energia) não é genérica — cada uma tem relação direta com regulação de dopamina e cortisol, sistemas já disfuncionais na fisiologia do TDAH:

- **Sono** — privação de sono reduz função executiva e piora impulsividade no dia seguinte; é consistentemente apontado como o gatilho mais forte de piora sintomática.
- **Exposição à luz solar matinal** — regula o ritmo circadiano e a curva de cortisol, com efeito indireto sobre humor e alerta cognitivo.
- **Hidratação** — desidratação leve já está associada a queda de concentração e fadiga mental.
- **MIT (Most Important Tasks)** — opera sobre a mesma lógica dos prompts fixos: reduzir sobrecarga de decisão, não aumentar produtividade por si só.

O valor de registrar esses dados junto ao diário emocional é permitir correlação: por exemplo, identificar que dias de sono ruim antecedem consistentemente relatos de maior estresse ou mais distorções cognitivas — informação que tanto o usuário quanto o psicólogo podem usar clinicamente (RF10 do projeto).

### 9. Papel e limites do LLM nesse desenho

O LLM entra como **substituto parcial do olhar externo do terapeuta** entre sessões — não como terapeuta. A literatura de TCC computacional (ex: chatbots terapêuticos como Woebot) mostra que ferramentas automatizadas podem apoiar adesão à técnica (nomear distorções, estruturar ABC/ABCDE) mas não substituem julgamento clínico, aliança terapêutica ou manejo de crise. Por isso as restrições do projeto (AGENTS.md): o LLM aponta *possíveis* distorções, nunca diagnostica, e todo output mantém o aviso de que é ferramenta de apoio.

O mecanismo do D — questionamento socrático que leva a uma conclusão auto-gerada, não uma resposta didática entregue pronta — está detalhado na seção 2, e é o motivo pelo qual o LLM não deve resolver o D/E unilateralmente. O mesmo princípio — evidenciar padrão, não entregar conclusão fechada — vale para o nível de crença nuclear (seção 5): o sistema aponta tema recorrente entre entradas, nunca atribui um rótulo de schema ou diagnóstico à pessoa. A incorporação de experimentos comportamentais reais (testar a previsão catastrófica na prática, não só argumentar contra ela — Bennett-Levy et al., *Oxford Guide to Behavioural Experiments in Cognitive Therapy*, 2004) permanece como direção futura, fora do escopo atual do CLI.

### 10. Segurança clínica: triagem de risco como requisito de design, não comportamento emergente

Ferramentas de saúde mental digital que processam texto livre enfrentam um problema estrutural: qualquer conteúdo que descreva sofrimento intenso pode, em tese, incluir ideação de dano a si mesmo — e um sistema que só "analisa distorções cognitivas" trata isso como mais um dado de entrada, não como um sinal que exige resposta diferente.

**Por que não pode ser um comportamento implícito do prompt de análise:** a literatura de TCC computacional (chatbots como Woebot — Fitzpatrick, Darcy & Vierhile, 2017; Wysa — Inkster et al., 2018) trata triagem de risco como uma função separada da conversa terapêutica geral, com protocolo de escalonamento próprio — não uma inferência acidental do mesmo modelo que aponta distorções. Misturar as duas funções no mesmo prompt cria dois problemas: (1) o resultado da triagem fica sujeito à mesma variabilidade de texto livre já identificada como problema em ADR-010 (saída não-estruturada, risco de falha silenciosa) — aqui a "falha silenciosa" tem consequência muito mais grave que num campo de análise cognitiva; (2) a resposta a um sinal de risco (o que mostrar, como mostrar) não deveria ser decidida pelo LLM em texto livre a cada chamada — precisa ser conteúdo fixo, revisado previamente, e disparado deterministicamente pelo código, não gerado.

**Por que não é avaliação de gravidade:** instrumentos clínicos validados como a Columbia-Suicide Severity Rating Scale (C-SSRS) estruturam a avaliação de risco em perguntas específicas e hierárquicas, aplicadas e interpretadas por profissional treinado. Um LLM lendo texto livre não replica esse instrumento — o mesmo argumento já usado para não mapear crenças a schemas de Young (seção 5) se aplica aqui: o sistema não deve se comportar como se estivesse avaliando gravidade clínica, só reconhecendo a possibilidade de risco e direcionando a ajuda humana.

**Sensibilidade sobre especificidade:** qualquer classificador de risco (LLM ou modelo dedicado) tem uma zona de incerteza. Errar para o lado de mostrar o bloco de segurança com frequência maior que o estritamente necessário (falso positivo) tem custo baixo — uma mensagem de apoio a mais. Errar para o lado de não mostrar quando havia risco real (falso negativo) tem custo potencialmente irreversível. Esse desequilíbrio de custos justifica um limiar de decisão deliberadamente conservador, mesmo sabendo que isso gera mais falsos positivos.

**A limitação arquitetural que precisa ficar explícita:** o sistema roda sob demanda (ADR-002) — a triagem de risco só acontece quando o usuário decide rodar o comando `analisar`, o que pode ser horas ou dias depois da entrada ter sido escrita (inclusive um bloco de gatilho registrado em crise, ADR-018). Isso significa que o sistema não é, e não pode se apresentar como, uma ferramenta de intervenção em tempo real — não substitui uma linha de crise, e o bloco de segurança não deve ser escrito como se endereçasse uma emergência "agora" (o momento agudo já pode ter passado). O objetivo realista é reconhecer o sinal e reforçar, de forma calma e não alarmista, o caminho para ajuda humana — não gerenciar a crise.

**O papel do sistema termina no reconhecimento, não na resposta:** convergindo com a postura já estabelecida na seção 9, o sistema aponta a possibilidade de risco e direciona a ajuda humana qualificada — nunca tenta avaliar gravidade, oferecer suporte emocional substitutivo, ou decidir se a situação é ou não uma emergência. Essa decisão é sempre da pessoa e de quem ela buscar.
