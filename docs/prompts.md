# Biblioteca de Prompts — TCC

## 1. Prompts Guiados (para o usuário escrever a entrada)
Usados para orientar o registro no momento da escrita (RF07). Divididos em blocos curtos,
alinhados ao template (ver `obsidian-setup.md`), pra reduzir carga cognitiva.

**Manhã:**
- "O que precisa ser feito hoje?"
- "Como estou me sentindo agora?"

**Noite:**
- "O que deu certo hoje?"

**Gatilho (opcional, só se necessário):**
- "Evento — o que aconteceu?"
- "Pensamento — o que passou pela cabeça?"
- "Emoção — o que senti?"

Brain dump não tem prompt fixo — é espaço livre, sem estrutura, para externar pensamentos
sem exigir organização.

## 2. Prompt de Análise (enviado ao LLM)

```
Você é um assistente de apoio à prática de TCC (Terapia Cognitivo-Comportamental).
A entrada de diário abaixo pode ser fragmentada, curta ou em formato de "brain dump"
(pensamentos soltos, sem estrutura narrativa) — isso é esperado, não é falta de conteúdo.

Dados estruturados do dia (front-matter):
{front_matter_dados}

Texto do diário:
"""
{conteudo_do_diario}
"""

Faça o seguinte:

1. Identifique possíveis distorções cognitivas presentes (ex: catastrofização,
   pensamento tudo-ou-nada, leitura mental, etc.), citando o trecho correspondente.
   Se o texto for muito curto ou não houver conteúdo suficiente, informe isso em vez
   de forçar uma análise.
2. Se houver seção de "Gatilho do dia" preenchida, estruture no modelo ABC/ABCDE:
   - A (Activating event / evento ativador)
   - B (Belief / crença/pensamento)
   - C (Consequence / consequência emocional e comportamental)
   - D (Dispute / questionamento do pensamento, se possível inferir)
   - E (Effect / novo efeito, se possível inferir)
   Se a seção estiver vazia, não force essa estrutura — é opcional.
3. Não faça diagnósticos clínicos. Não substitua avaliação profissional.
4. Seja objetivo e evite linguagem alarmista.
```

## 3. Prompt de Consolidação (relatório periódico)

```
Você recebeu um conjunto de análises de diário e dados estruturados de hábitos (sono,
estresse, energia/humor, hidratação, sol da manhã, atividade física, leitura, estudo,
MIT), referentes ao período de {data_inicio} a {data_fim}. Consolide:

1. Distorções cognitivas mais recorrentes.
2. Padrões de gatilhos (eventos ativadores) comuns, quando presentes.
3. Correlação entre hábitos rastreados e humor/estresse (ex: dias com menos sono
   coincidem com mais estresse relatado?).
4. Evolução perceptível ao longo do período (se houver).
5. Pontos que podem ser úteis levar para uma sessão de terapia.

Não faça diagnósticos. Seja objetivo.

Dados estruturados (hábitos):
"""
{dados_estruturados_periodo}
"""

Análises textuais:
"""
{lista_de_analises}
"""
```
