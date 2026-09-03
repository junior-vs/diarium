# Wiki: Configuração do Obsidian

Guia de configuração do vault para uso com o sistema de Diário TCC. Prioriza plugins
core (nativos) do Obsidian, evitando dependência de plugins de terceiros — já que o
processamento pesado (análise TCC) fica a cargo do script/CLI externo, não do Obsidian.

## 1. Estrutura do Vault

```
/vault
  /diario
    2026-09-01.md
    2026-09-02.md
    ...
  /analises
    2026-09-01-analise.md
    2026-09-02-analise.md
    ...
  /relatorios
    2026-09-relatorio.md
    ...
  /templates
    template-diario.md
```

- **/diario** — entradas brutas escritas pelo usuário.
- **/analises** — saídas geradas pelo CLI (uma por entrada).
- **/relatorios** — saídas consolidadas periódicas.
- **/templates** — modelos reutilizáveis (plugin core "Templates").

## 2. Plugins Core Necessários

Ativar em `Configurações > Plugins principais`:

| Plugin | Uso |
|--------|-----|
| **Daily notes** | Cria a entrada do dia automaticamente na pasta `/diario`, com nome padronizado por data. |
| **Templates** | Aplica o template de diário (estrutura ABC/ABCDE guiada) ao criar nova entrada. |
| **Tags** | Organiza entradas por tags (ex: `#tcc`, `#ansiedade`) sem precisar de plugin externo. |
| **Search** | Busca full-text nativa — suficiente para localizar entradas/análises sem plugin de terceiros. |
| **Backlinks** | Vincula automaticamente análise ↔ entrada original (usando `[[link]]`). |

## 3. Configuração do Daily Notes

`Configurações > Daily notes`:
- **Local:** `/diario`
- **Formato do nome:** `YYYY-MM-DD`
- **Template:** `/templates/template-diario.md`

## 4. Template de Diário

Conteúdo de `/templates/template-diario.md`:

```markdown
---
data: {{date}}
tags: [diario]
analisado: false
---

## Evento
<!-- O que aconteceu hoje que gerou uma reação emocional forte? -->

## Pensamento
<!-- Que pensamento passou pela sua cabeça nesse momento? -->

## Emoção
<!-- Que emoção você sentiu, e em que intensidade (0-10)? -->

## Reação
<!-- Como você reagiu (comportamento)? -->

## Reflexão
<!-- Existe alguma outra forma de interpretar essa situação? -->
```

O front-matter (`data`, `tags`, `analisado`) é lido pelo script externo para localizar
e filtrar entradas — sem exigir plugin de terceiros (Dataview, etc.) dentro do Obsidian.

## 5. Convenção de Vínculo Análise ↔ Entrada

No arquivo gerado em `/analises`, o CLI deve incluir um link nativo do Obsidian para
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
3. Fora do Obsidian, rodar o CLI: `diario-tcc analisar --arquivo diario/2026-09-01.md`.
4. CLI gera `analises/2026-09-01-analise.md`, já linkado à entrada original.
5. Reabrir no Obsidian para ver o backlink e a análise.
