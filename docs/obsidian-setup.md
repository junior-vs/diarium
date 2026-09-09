# Wiki: Configuração do Obsidian

Guia de configuração do vault para uso com o sistema de Diário TCC. Prioriza plugins
core (nativos) do Obsidian, evitando dependência de plugins de terceiros — já que o
processamento pesado (análise TCC) fica a cargo do script/CLI externo, não do Obsidian.

## 1. Estrutura do Vault

```
/vault
  /diary
    /2026
      /September
        2026-09-01.md
        2026-09-02.md
    ...
  /analyses
    /2026
      /September
        2026-09-01-analise.md
        2026-09-02-analise.md
    ...
  /templates
    template-diario.md
    gatilho-rapido.md
```

- **/diary/YYYY/MMMM** — entradas brutas escritas pelo usuário.
- **/analyses/YYYY/MMMM** — saídas geradas pelo CLI, incluindo análises e relatórios.
- **/templates** — modelos reutilizáveis (plugin core "Templates"). `template-diario.md`
  é aplicado uma vez, na criação da nota do dia; `gatilho-rapido.md` é inserido pontualmente,
  quantas vezes for preciso (ver §5).

## 2. Plugins Core Necessários

Ativar em `Configurações > Plugins principais`:

| Plugin | Uso |
|--------|-----|
| **Daily notes** | Cria a entrada do dia automaticamente na pasta `/diary/YYYY/MMMM`, com nome padronizado por data. |
| **Templates** | Aplica o template de diário (estrutura ABC/ABCDE guiada) ao criar nova entrada, e insere o bloco de gatilho rápido no cursor a qualquer momento. |
| **Tags** | Organiza entradas por tags (ex: `#tcc`, `#ansiedade`) sem precisar de plugin externo. |
| **Search** | Busca full-text nativa — suficiente para localizar entradas/análises sem plugin de terceiros. |
| **Backlinks** | Vincula automaticamente análise ↔ entrada original (usando `[[link]]`). |

## 3. Configuração do Daily Notes

`Configurações > Daily notes`:
- **Local:** `/diary/YYYY/MMMM`
- **Formato do nome:** `YYYY-MM-DD`
- **Template:** `/templates/template-diario.md`

## 4. Template de Diário

Template revisado para baixa carga cognitiva (ver ADR-005 em `decisions.md`), com brain
dump livre, prompts fixos manhã/noite, e tracking de hábitos via front-matter. A seção
de Gatilho não vem mais preenchida como bloco único — ela é o ponto de ancoragem onde
blocos de captura rápida (§5) são inseridos, um por ocorrência, ao longo do dia
(ver ADR-018).

Conteúdo de `/templates/template-diario.md`:

```markdown
---
data: {{date}}
tags: [diario]
processado: false
mit: 
sono: 
estresse: 
energia_humor: 
hidratacao: 
sol_manha: false
atividade_fisica: false
leitura: false
estudo: false
---

## 📊 Check-in Rápido
- [ ] **MIT (Prioridade do Dia):** 
- [ ] **Sono:** ___ hrs | **Energia/Humor (1-5):** ___ | **Estresse (1-5):** ___
- [ ] **Hábitos:** Sol ☀️ | Ativ. Física 🏃 | Leitura 📚 | Estudo 📖 | Água 💧 (copos: )

---

## 🧠 Brain Dump
<!-- Espaço livre, sem regras. Solte tudo que estiver na cabeça. -->


---

## ☀️ Manhã
- **O que precisa ser feito hoje?**
- **Como estou me sentindo agora?**

## 🌙 Noite
- **O que deu certo hoje?**

---

## 🎯 Registro de Gatilho
<!-- Use quando sentir necessidade de processar uma emoção forte. Pode repetir
     quantas vezes for preciso ao longo do dia — cada ocorrência é um bloco novo,
     inserido via "Insert template" > gatilho-rapido (ver obsidian-setup.md §5). -->
```

### Campos do front-matter

| Campo | Tipo | Origem sugerida |
| --- | --- | --- |
| `mit` | texto curto | manual |
| `sono` | número (horas) | dispositivo (celular/smartwatch), quando disponível |
| `estresse` | escala 1-5 | manual |
| `energia_humor` | escala 1-5 | manual |
| `hidratacao` | número (copos) | dispositivo, quando disponível |
| `sol_manha` | booleano | manual |
| `atividade_fisica` | booleano | manual |
| `leitura` | booleano | manual |
| `estudo` | booleano | manual |

O checklist "Check-in Rápido" reflete os mesmos valores do front-matter — preencher em
um lugar só (recomendado: front-matter, já que é o que o CLI lê) evita trabalho duplicado
(ver ADR-007).

O front-matter completo (`data`, `tags`, `processado`, + campos de hábito) é lido pelo
script externo para localizar, filtrar entradas e compor o relatório consolidado — sem
exigir plugin de terceiros (Dataview, etc.) dentro do Obsidian.

## 5. Captura rápida de gatilho (Insert template)

Diferente do template principal (aplicado uma vez, na criação da nota do dia via Daily
Notes), o bloco de gatilho usa o comando nativo **"Insert template"** (plugin core
Templates), que insere conteúdo no cursor de uma nota já aberta — permitindo múltiplos
registros no mesmo dia, cada um timestampado (ver ADR-018, ADR-019).

Conteúdo de `/templates/gatilho-rapido.md`:

```markdown
### {{time}} — Gatilho
- **Evento:**
- **Pensamento:**
- **Emoção:**
- **Comportamento:**
```

**Configuração:**

1. `Configurações > Atalhos de teclado` → buscar "Insert template" → atribuir um atalho
   (ex: `Ctrl/Cmd + Shift + G`).
2. Em crise ou evento importante: abrir a nota do dia, posicionar o cursor no fim,
   acionar o atalho, selecionar `gatilho-rapido`.
3. O bloco `### HH:MM — Gatilho` é inserido com o horário atual; preencher os 4 campos
   (Evento, Pensamento, Emoção, Comportamento).

Funciona igual no Obsidian mobile (plugins core, incluindo Templates, têm paridade com
desktop) — relevante porque crise não espera acesso a um computador.

## 6. Convenção de Vínculo Análise ↔ Entrada

No arquivo gerado em `/analyses/YYYY/MMMM`, o CLI deve incluir um link nativo do Obsidian para
a entrada original:

```markdown
---
data: 2026-09-01
tags: [analise-tcc]
entrada_origem: "[[2026-09-01]]"
---

## Análise
...
```

Isso cria backlink automático (via plugin core "Backlinks"), sem necessidade de Dataview.

## 7. Sobre Plugins de Terceiros (evitados)

| Plugin comum | Por que não é necessário aqui |
|---------------|-------------------------------|
| **Dataview** | Consultas/agregações ficam no script externo, que já lê os `.md` diretamente. |
| **Templater** | O plugin core "Templates" cobre o caso de uso (template estático com `{{date}}`/`{{time}}`, e inserção pontual no cursor). |
| **QuickAdd** | Fluxo de criação é simples o suficiente para o Daily Notes nativo. |

Se, no futuro, alguma necessidade não for coberta pelos plugins core (ex: automação
de front-matter dinâmico), reavaliar nesse momento — e documentar a exceção aqui,
com justificativa.

## 8. Fluxo de Uso

1. Abrir Obsidian → criar nota do dia (Daily Notes aplica template automaticamente).
2. Ao longo do dia, se ocorrer uma crise ou evento importante: inserir um bloco de
   gatilho rápido (§5) na nota do dia já aberta, quantas vezes for necessário.
3. Preencher a entrada seguindo a estrutura guiada (Brain Dump, Manhã/Noite).
4. Fora do Obsidian, rodar o CLI: `diario-tcc analisar --arquivo diary/2026/September/2026-09-01.md`.
5. CLI gera `analyses/2026/September/2026-09-01-analise.md`, já linkado à entrada original,
   com um ABC/ABCDE por bloco de gatilho encontrado.
6. Reabrir no Obsidian para ver o backlink e a análise.
