# Plano de Implementação — Diarium (baseado em specification.md)

## Fases

1. Fundação (parser + models)
2. LLM Adapter (Gemini)
3. Análise individual (RF01-RF05)
4. Relatório de período e tendência (RF06-RF09), front-matter (RF12), correlação (RF13)
5. Prompts guiados / template (RF10)
6. Config e CLI (RF11, RNF04)
7. Triagem de risco (RF15) e rodapé de limite de papel (RF18) — **pendente de implementação**, ver nota abaixo
8. Testes e validação

---

## Fase 1 — Fundação

### T1.1 — Setup de módulos `core/` e `cli/`
Criar estrutura conforme ADR-009/architecture.md:
```
diarium-app/src/diarium_app/
  core/
    models.py
    parser.py
    llm/
      base.py
      gemini_adapter.py
    analysis.py
    report.py
  cli/
    main.py
  config.py
```
Adicionar dependências no `pyproject.toml`: `pydantic`, `typer` (ou `click`), `python-frontmatter`, `google-generativeai`.

### T1.2 — Modelos Pydantic (`core/models.py`)
Implementar:
- `HabitData`: campos do front-matter (sono, estresse, energia_humor, hidratacao, sol_manha, atividade_fisica, leitura, estudo, mit) — todos `Optional`, tolerantes a ausência (AGENTS.md §8).
- `EntryData`: `data`, `conteudo` (texto sem front-matter), `habit_data`, `caminho_origem`.
- `CognitiveDistortion`: `tipo`, `trecho_citado`.
- `ABCDE`: campos `a, b, c, d, e` opcionais.
- `AnalysisResult`: `distorcoes: list[CognitiveDistortion]`, `abcde: ABCDE | None`, `resumo: str`, `entrada_origem`.
- `ReportResult`: distorções recorrentes, padrões de gatilho, correlação hábito×humor, evolução, pontos para terapia.

**Sugestão:** usar `pydantic.BaseModel` com `model_config = {"extra": "ignore"}` nos campos de front-matter para tolerar campos desconhecidos sem quebrar.

### T1.3 — Parser de Markdown (`core/parser.py`)
- Ler arquivo `.md`, separar front-matter (YAML) do corpo (texto).
- Usar `python-frontmatter` (lib madura, já resolve o split YAML/corpo) em vez de regex manual.
- Retornar `EntryData` populado; campos de hábito ausentes → `None`, nunca exceção.
- Casos de borda a cobrir (ligados a Fase 7): front-matter vazio, arquivo sem front-matter, apenas brain dump.

```python
import frontmatter
from .models import EntryData, HabitData

def parse_entry(path: str) -> EntryData:
    post = frontmatter.load(path)
    habit_data = HabitData(**{k: post.metadata.get(k) for k in HabitData.model_fields})
    return EntryData(
        data=post.metadata.get("data"),
        conteudo=post.content.strip(),
        habit_data=habit_data,
        caminho_origem=path,
    )
```

---

## Fase 2 — LLM Adapter

### T2.1 — Interface abstrata (`core/llm/base.py`)
Conforme ADR-003/architecture.md §2.3:
```python
from abc import ABC, abstractmethod

class LLMAdapter(ABC):
    @abstractmethod
    def analyze_entry(self, text: str, habit_data: dict) -> AnalysisResult: ...

    @abstractmethod
    def consolidate(self, analyses: list[AnalysisResult], habit_data: list[dict]) -> ReportResult: ...
```

### T2.2 — GeminiAdapter (`core/llm/gemini_adapter.py`)
- Usar `google-generativeai` com `response_schema` (saída estruturada), não texto livre — ADR-010/011.
- Montar `response_schema` a partir dos modelos Pydantic (`model_json_schema()` do Pydantic, adaptado ao formato aceito pela lib do Gemini).
- Validar resposta com `AnalysisResult.model_validate_json(...)`; se falhar, levantar exceção explícita (`LLMResponseValidationError`), nunca aceitar "quase certo" (ADR-010).
- Prompts vêm de `docs/prompts.md` — extrair para constantes/templates (ex: `core/llm/prompts.py` ou arquivos `.txt` carregados em runtime), com `.format()`/f-string para interpolar `{front_matter_dados}` e `{conteudo_do_diario}`.

**Sugestão:** manter os textos de prompt fora do código Python (ex: `core/llm/prompts/analise.txt`, `consolidacao.txt`) para que mudanças de prompt não exijam deploy de código e fiquem fáceis de versionar isoladamente.

### T2.3 — Mecanismo de mock/stub para testes
Criar `FakeLLMAdapter(LLMAdapter)` em `tests/` que retorna respostas fixas — usado pelos testes de `analysis.py`/`report.py` sem chamada real (AGENTS.md §9).

---

## Fase 3 — Análise individual (RF01–RF05)

### T3.1 — Orquestração (`core/analysis.py`)
```python
def analyze(path: str, adapter: LLMAdapter) -> AnalysisResult:
    entry = parse_entry(path)          # RF01
    result = adapter.analyze_entry(     # RF02, RF03, RF04
        entry.conteudo, entry.habit_data.model_dump()
    )
    result.entrada_origem = entry.data
    return result
```
Regra ADR-009: só `analysis.py` chama o `LLMAdapter`; CLI não chama diretamente.

### T3.2 — Gerador de saída (`core/report.py` ou `core/writer.py`)
- Serializar `AnalysisResult` em markdown com front-matter (`data`, `tags: [analise-tcc]`, `entrada_origem: "[[YYYY-MM-DD]]"`) conforme AGENTS.md §4.
- Escrever em `analyses/YYYY/MMMM/YYYY-MM-DD-analise.md`.
- Quando a nota de origem for atualizada, anexar uma seção determinística ao final em vez de reescrever todo o arquivo.
- Marcar a entrada original como `processado: true` após o sucesso da análise, preservando o conteúdo existente e apenas alterando o front-matter da nota.

**Sugestão de lib:** `python-frontmatter` também serve para escrever (`frontmatter.dump`), mantendo consistência com o parser.

---

## Fase 4 — Relatório de período e tendência (RF06-RF09, RF12, RF13)

### T4.1 — Coleta de dados do período (`core/report.py`)
- Localizar as notas brutas em `diary/YYYY/MMMM` como fonte de verdade; se houver análises ou relatórios pré-existentes no intervalo, avisar o usuário e regenerar a partir das notas originais.
- Ler campos de hábito **diretamente do front-matter das entradas** (RF12) — nunca pedir ao LLM para extrair.

### T4.2 — Consolidação via LLM (RF13)
- Montar `dados_estruturados_periodo` (lista de `HabitData` serializados) + `lista_de_analises` (resumos das `AnalysisResult`).
- Chamar `adapter.consolidate(...)`.
- Correlação hábito×humor: **decisão de implementação** — correlação pode ser (a) inteiramente delegada ao LLM via prompt (como está em `prompts.md`), ou (b) pré-calculada em Python (ex: correlação simples sono×estresse) e passada como dado extra ao LLM. Sugestão: começar com (a) por ser mais simples e já coberto pelo prompt existente; abrir ADR se depois quiser (b).

### T4.3 — Escrita do relatório
- Gerar `analyses/YYYY/MMMM/YYYY-MM-relatorio.md` com front-matter próprio e links `[[YYYY-MM-DD]]` para as entradas cobertas (ADR-008).

---

## Fase 5 — Prompts guiados / template (RF10)

### T5.1 — Comando de scaffold de entrada (opcional, avaliar se está no escopo v1)
Specification não define um comando explícito para *criar* a entrada do dia — isso é responsabilidade do Obsidian (Templates core plugin) conforme ADR-004/012. **Ação:** não implementar comando de criação de arquivo no CLI; apenas garantir que `docs/template-diario.md` seja o template configurado no plugin Templates do Obsidian. Task real aqui é de configuração, não de código.

### T5.2 — Validar template em uso
Conferir que `diarium-vault` tem o template instalado conforme `docs/obsidian-setup.md` e front-matter bate com `HabitData` (T1.2) — se divergir, atualizar os dois juntos (AGENTS §7).

---

## Fase 6 — Config e CLI (RF11, RNF04)

### T6.1 — `config.py`
- Carregar provedor + API key de variável de ambiente ou `config.yaml`/`.env` (já no `.gitignore`).
- Sugestão: `pydantic-settings` (`BaseSettings`) para validação de config com pouco boilerplate.
```python
class Settings(BaseSettings):
    llm_provider: str = "gemini"
    llm_api_key: str
    vault_path: str
    class Config:
        env_file = ".env"
```

### T6.2 — CLI (`cli/main.py`)
- Usar `typer` (ergonomia melhor que `argparse` puro, gera `--help` automático).
```python
app = typer.Typer()

@app.command()
def analisar(arquivo: str):
    adapter = get_adapter(settings)
    result = analysis.analyze(arquivo, adapter)
    report.write_analysis(result)

@app.command()
def relatorio(de: str, ate: str):
    ...
```
- Registrar entrypoint `diario-tcc` no `pyproject.toml` (`[project.scripts]`) — **corrigir a inconsistência atual**: hoje está `diarium-app`, README documenta `diario-tcc`.

---

## Fase 7 — Triagem de risco (RF15) e rodapé de limite de papel (RF18)

**Status:** não implementado no código atual — `LLMAdapter` hoje só expõe `analyze_entry`
e `consolidate`; não há `screen_risk`, nenhum enum de risco, e `bloco-seguranca.md` não é
referenciado em nenhum módulo Python. Isso diverge de ADR-022, que trata esse requisito
como não-negociável para o v1.

### T7.1 — `screen_risk` na interface (`core/llm/base.py`)
```python
class RiskScreeningResult(str, Enum):
    SEM_INDICIO = "sem_indicio"
    POSSIVEL_RISCO = "possivel_risco"

class LLMAdapter(ABC):
    @abstractmethod
    def screen_risk(self, text: str) -> RiskScreeningResult: ...
```
Chamado em `core/analysis.py` ANTES e independentemente de `analyze_entry`, para o texto
completo e para cada bloco de gatilho isoladamente (ADR-022).

### T7.2 — Inserção determinística do bloco de segurança
Quando `POSSIVEL_RISCO`, `core/report.py` deve prefixar a saída com o conteúdo estático
de `docs/bloco-seguranca.md` (carregado de arquivo, nunca gerado pelo LLM), preservando a
análise normal abaixo.

### T7.3 — Rodapé fixo (RF18)
Toda saída (`analisar`, `relatorio` de período, `relatorio` de tendência) recebe um
rodapé estático de 2-3 linhas (hipótese/não-diagnóstico, não substitui profissional),
carregado de arquivo, incondicional — independente do bloco de T7.2.

### T7.4 — Teste de sincronização doc↔prompt
Cobrir o gap já identificado nesta revisão: os arquivos `.txt` reais em
`infrastructure/llm/prompts/` divergiram de `docs/prompts.md` (D resolvido em vez de
socrático). Adicionar teste que compare os `.txt` carregados em runtime contra um
snapshot derivado do markdown, para travar build em caso de nova deriva silenciosa.

---

## Fase 8 — Testes e validação (AGENTS §9)

| Alvo | Casos |
|---|---|
| `parser.py` | front-matter ausente, front-matter vazio, entrada só com brain dump, campos de hábito parcialmente preenchidos |
| `LLMAdapter` | mock/stub (T2.3), sem chamada real; validar erro explícito em resposta fora do schema |
| `analysis.py` / `report.py` | fluxo completo com `FakeLLMAdapter`, verificação de markdown de saída (front-matter correto, link `[[YYYY-MM-DD]]`) |
| Critérios de aceite (specification §6) | testes de integração: rodar `analisar` sobre fixture real gera output coerente; rodar `relatorio` sobre intervalo consolida múltiplas entradas; trocar adapter via config não altera `core/` |
| Triagem de risco (T7) | fixture com conteúdo de risco simulado produz bloco de segurança no topo + rodapé RF18 ao final; fixture sem risco produz apenas o rodapé RF18 |

**Sugestão:** `pytest` + fixtures de arquivos `.md` de exemplo em `tests/fixtures/`.

---

## Ordem sugerida de execução

1. T1.1 → T1.2 → T1.3 (fundação testável isoladamente)
2. T2.1 → T2.3 (interface + mock, antes de mexer com API real)
3. T3.1 → T3.2 (fluxo de análise individual ponta a ponta, usando mock)
4. T6.1 → T6.2 (CLI mínimo para `analisar`, já validável manualmente)
5. T2.2 (Gemini real, plugado por último — reduz custo de iteração com API paga)
6. T4.1 → T4.2 → T4.3 (relatório)
7. T5.2 (checagem de template/vault)
8. T7.1 → T7.2 → T7.3 → T7.4 (triagem de risco e rodapé — bloqueador de v1 por ADR-022, priorizar antes de fechar o release, não deixar para o final)
9. Fase 8 (testes) em paralelo desde o T1.3

## Riscos/decisões em aberto a sinalizar antes de codar
- Quem confirma a atualização do front-matter `processado: true` na entrada de origem (T3.2) — o fluxo precisa ser implementado de forma determinística.
- Formato de `response_schema` do Gemini pode exigir schema JSON diferente do gerado por Pydantic — validar cedo com uma chamada real pequena.
- Nome do entrypoint CLI (`diario-tcc` vs `diarium-app`) precisa ser decidido e corrigido no `pyproject.toml`.
