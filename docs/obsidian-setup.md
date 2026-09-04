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
```

- **/diary/YYYY/MMMM** — entradas brutas escritas pelo usuário.
- **/analyses/YYYY/MMMM** — saídas geradas pelo CLI, incluindo análises e relatórios.
- **/templates** — modelos reutilizáveis (plugin core "Templates").

## 2. Plugins Core Necessários

Ativar em `Configurações > Plugins principais`:

| Plugin | Uso |
|--------|-----|
| **Daily notes** | Cria a entrada do dia automaticamente na pasta `/diary/YYYY/MMMM`, com nome padronizado por data. |
| **Templates** | Aplica o template de diário (estrutura ABC/ABCDE guiada) ao criar nova entrada. |
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
dump livre, prompts fixos manhã/noite, e tracking de hábitos via front-matter.

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

## 🎯 Registro de Gatilho (Opcional)
<!-- Use apenas se sentir necessidade de processar uma emoção forte -->
- **Evento:** 
- **Pensamento:** 
- **Emoção:**
```

### Campos do front-matter

| Campo | Tipo | Origem sugerida |
|---|---|---|
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

## 5. Convenção de Vínculo Análise ↔ Entrada

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

## 6. Sobre Plugins de Terceiros (evitados)

| Plugin comum | Por que não é necessário aqui |
|---------------|-------------------------------|
| **Dataview** | Consultas/agregações ficam no script externo, que já lê os `.md` diretamente. |
| **Templater** | O plugin core "Templates" cobre o caso de uso (template estático com `{{date}}`). |
| **QuickAdd** | Fluxo de criação é simples o suficiente para o Daily Notes nativo. |

Se, no futuro, alguma necessidade não for coberta pelos plugins core (ex: automação
de front-matter dinâmico), reavaliar nesse momento — e documentar a exceção aqui,
com justificativa.

## 7. Fluxo de Uso

1. Abrir Obsidian → criar nota do dia (Daily Notes aplica template automaticamente).
2. Preencher a entrada seguindo a estrutura guiada.
3. Fora do Obsidian, rodar o CLI: `diario-tcc analisar --arquivo diary/2026/September/2026-09-01.md`.
4. CLI gera `analyses/2026/September/2026-09-01-analise.md`, já linkado à entrada original.
5. Reabrir no Obsidian para ver o backlink e a análise.
