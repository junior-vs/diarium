# Plano de Refatoração — Diarium

Baseado em: OOP, Programação Funcional, SOLID, Clean Architecture.

## Diagnóstico

| Problema | Local | Princípio violado |
|---|---|---|
| Path, formatação markdown, I/O de arquivo, varredura do vault e mutação de nota-fonte no mesmo módulo | `core/report.py` | SRP |
| Use cases importam `frontmatter` e escrevem em disco diretamente | `core/analysis.py`, `core/report.py` | DIP |
| Funções privadas (`_resolve_entry_date`, `_require_entry_date`) consumidas fora do módulo de origem | `core/report.py` importando de `core/analysis.py` | Encapsulamento vazado |
| Cadeia `if/elif` para seleção de provider LLM | `config.py::build_adapter` | OCP |
| Não existe port para persistência (só existe para LLM) | ausência de `EntryRepository` | DIP / Clean Architecture |

O que já está correto e é mantido: `LLMAdapter` como ABC (Strategy + DIP corretos), `models.py` como entidades/DTOs, funções `build_*_markdown` já são puras (só precisam mudar de lugar), `FakeLLMAdapter` como test double.

## Estrutura nova

```
diarium_app/
  domain/
    models.py
    entry_date.py
  ports/
    llm_adapter.py
    entry_repository.py
  formatters/
    analysis_markdown.py
    report_markdown.py
    source_note.py
  use_cases/
    analyze_entry.py
    generate_period_report.py
  infrastructure/
    filesystem_entry_repository.py
    llm/
      fake_adapter.py
      gemini_adapter.py
      prompt_loader.py
      prompts/
        analysis.txt
        consolidation.txt
  cli/
    main.py
  config.py
```

## Mapeamento de movimentação

| Origem | Destino |
|---|---|
| `core/models.py` | `domain/models.py` (conteúdo idêntico) |
| `core/llm/base.py` | `ports/llm_adapter.py` |
| `core/parser.py` + parte de I/O de `core/report.py` | `infrastructure/filesystem_entry_repository.py` |
| `core/llm/fake.py` | `infrastructure/llm/fake_adapter.py` |
| `core/llm/gemini_adapter.py` | `infrastructure/llm/gemini_adapter.py` |
| `core/llm/prompt_loader.py` + `core/llm/prompts/` | `infrastructure/llm/prompt_loader.py` + `infrastructure/llm/prompts/` |
| `core/analysis.py` | `use_cases/analyze_entry.py` |
| parte de orquestração de `core/report.py` | `use_cases/generate_period_report.py` |
| parte de formatação pura de `core/report.py` | `formatters/analysis_markdown.py`, `formatters/report_markdown.py`, `formatters/source_note.py` |

`core/` deixa de existir como pacote único; é dividido em `domain/`, `ports/`, `formatters/`, `use_cases/`, `infrastructure/`.

---

## Código

### `domain/models.py`
Conteúdo idêntico ao `core/models.py` atual — apenas move de pacote, sem alteração de linhas.

### `domain/entry_date.py`
```python
from __future__ import annotations

import re
from datetime import date, datetime
from pathlib import Path

from .models import EntryData


def resolve_entry_date(entry: EntryData) -> date | None:
	if entry.data is not None:
		return entry.data
	return _infer_date_from_path(entry.caminho_origem)


def require_entry_date(entry: EntryData) -> date:
	entry_date = resolve_entry_date(entry)
	if entry_date is None:
		raise ValueError(f"Could not determine entry date for {entry.caminho_origem}")
	return entry_date


def _infer_date_from_path(path_value: str) -> date | None:
	stem = Path(path_value).stem
	match = re.search(r"\d{4}-\d{2}-\d{2}", stem)
	if not match:
		return None
	try:
		return datetime.strptime(match.group(0), "%Y-%m-%d").date()
	except ValueError:
		return None
```
Ambas as funções eram privadas (`_resolve_entry_date`, `_require_entry_date`) dentro de `analysis.py` e importadas com underscore por `report.py`. Agora são um serviço de domínio público, sem import de função privada entre módulos.

### `ports/llm_adapter.py`
```python
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Mapping

from ..domain.models import AnalysisResult, ReportResult


class LLMResponseValidationError(ValueError):
	"""Raised when the provider returns a payload that does not match the schema."""


class LLMAdapter(ABC):
	@abstractmethod
	def analyze_entry(self, text: str, habit_data: Mapping[str, Any]) -> AnalysisResult:
		"""Analyze a single diary entry and return a structured result."""

	@abstractmethod
	def consolidate(
		self,
		analyses: list[AnalysisResult],
		habit_data: list[Mapping[str, Any]],
	) -> ReportResult:
		"""Consolidate multiple analyses into a report result."""
```
Sem alteração de lógica — só o import relativo (`..domain.models`).

### `ports/entry_repository.py` (novo)
```python
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from pathlib import Path

from ..domain.models import AnalysisResult, EntryData, ReportResult


class EntryRepository(ABC):
	@abstractmethod
	def load_entry(self, path: str | Path) -> EntryData:
		"""Load and parse a single diary entry from storage."""

	@abstractmethod
	def list_entries_in_range(self, start: date, end: date) -> list[EntryData]:
		"""Return all diary entries whose date falls within [start, end]."""

	@abstractmethod
	def save_analysis(self, entry: EntryData, analysis: AnalysisResult) -> Path:
		"""Persist the analysis for a single entry and return its path."""

	@abstractmethod
	def save_report(
		self,
		start: date,
		end: date,
		report: ReportResult,
		entries: list[EntryData],
	) -> Path:
		"""Persist a consolidated report and return its path."""

	@abstractmethod
	def mark_source_processed(self, entry: EntryData, analysis: AnalysisResult, analysis_path: Path) -> None:
		"""Update the source diary note to reflect that it has been analyzed."""
```

### `formatters/analysis_markdown.py`
```python
from __future__ import annotations

from typing import Any

import frontmatter

from ..domain.entry_date import require_entry_date
from ..domain.models import AnalysisResult, EntryData


def build_analysis_markdown(entry: EntryData, analysis: AnalysisResult) -> str:
	entry_date = require_entry_date(entry)
	metadata: dict[str, Any] = {
		"data": entry_date.isoformat(),
		"tags": ["analise-tcc"],
		"entrada_origem": f"[[{entry_date.isoformat()}]]",
	}
	sections = [
		"## Análise",
		"",
		"### Resumo",
		analysis.resumo.strip() or "Sem resumo gerado.",
		"",
		"### Distorções cognitivas",
	]
	if analysis.distorcoes:
		for distortion in analysis.distorcoes:
			sections.append(f"- **{distortion.tipo}**: {distortion.trecho_citado}")
	else:
		sections.append("- Nenhuma distorção identificada.")
	sections.extend(["", "### ABCDE"])
	if analysis.abcde is None or not any(
		[analysis.abcde.a, analysis.abcde.b, analysis.abcde.c, analysis.abcde.d, analysis.abcde.e]
	):
		sections.append("- Não estruturado para esta entrada.")
	else:
		sections.extend([
			f"- **A**: {analysis.abcde.a or ''}",
			f"- **B**: {analysis.abcde.b or ''}",
			f"- **C**: {analysis.abcde.c or ''}",
			f"- **D**: {analysis.abcde.d or ''}",
			f"- **E**: {analysis.abcde.e or ''}",
		])
	post = frontmatter.Post("\n".join(sections).strip() + "\n", **metadata)
	return frontmatter.dumps(post)
```

### `formatters/report_markdown.py`
```python
from __future__ import annotations

from datetime import date
from typing import Any

import frontmatter

from ..domain.entry_date import require_entry_date
from ..domain.models import EntryData, ReportResult


def build_report_markdown(
	start_date: date,
	end_date: date,
	report: ReportResult,
	entries: list[EntryData],
) -> str:
	metadata: dict[str, Any] = {
		"data_inicio": start_date.isoformat(),
		"data_fim": end_date.isoformat(),
		"tags": ["relatorio-tcc"],
	}
	lines = [
		"## Relatório Consolidado",
		"",
		f"**Período:** {start_date.isoformat()} a {end_date.isoformat()}",
		"",
		"### Distorções recorrentes",
	]
	lines.extend(_render_bullets(report.distorcoes_recorrentes, "Nenhuma distorção recorrente identificada."))
	lines.extend(["", "### Padrões de gatilho"])
	lines.extend(_render_bullets(report.padroes_de_gatilho, "Nenhum padrão de gatilho identificado."))
	lines.extend(["", "### Correlações hábito x humor"])
	if report.correlacoes_habito_humor:
		for correlation in report.correlacoes_habito_humor:
			lines.append(f"- **{correlation.habito}**: {correlation.relacao}")
	else:
		lines.append("- Nenhuma correlação identificada.")
	lines.extend(["", "### Evolução"])
	lines.append(report.evolucao.strip() or "Sem evolução observável.")
	lines.extend(["", "### Pontos para terapia"])
	lines.extend(_render_bullets(report.pontos_para_terapia, "Sem pontos específicos registrados."))
	lines.extend(["", "### Entradas cobertas"])
	for entry in entries:
		entry_date = require_entry_date(entry)
		lines.append(f"- [[{entry_date.isoformat()}]]")
	post = frontmatter.Post("\n".join(lines).strip() + "\n", **metadata)
	return frontmatter.dumps(post)


def _render_bullets(items: list[str], empty_message: str) -> list[str]:
	if not items:
		return [f"- {empty_message}"]
	return [f"- {item}" for item in items]
```

### `formatters/source_note.py`
```python
from __future__ import annotations

import re
from datetime import date
from pathlib import Path

from ..domain.models import AnalysisResult

SOURCE_BLOCK_START = "<!-- diarium:analysis:start -->"
SOURCE_BLOCK_END = "<!-- diarium:analysis:end -->"

_SECTION_PATTERN = re.compile(
	rf"{re.escape(SOURCE_BLOCK_START)}.*?{re.escape(SOURCE_BLOCK_END)}\n?",
	re.DOTALL,
)


def build_source_note_section(entry_date: date, analysis: AnalysisResult, analysis_path: Path) -> str:
	lines = [
		SOURCE_BLOCK_START,
		"## Análise processada",
		f"- **Data:** {entry_date.isoformat()}",
		f"- **Arquivo gerado:** [[{analysis_path.stem}]]",
		f"- **Resumo:** {analysis.resumo.strip() or 'Sem resumo gerado.'}",
		"",
		"### Distorções",
	]
	if analysis.distorcoes:
		for distortion in analysis.distorcoes:
			lines.append(f"- **{distortion.tipo}**: {distortion.trecho_citado}")
	else:
		lines.append("- Nenhuma distorção identificada.")
	lines.append(SOURCE_BLOCK_END)
	return "\n".join(lines).strip() + "\n"


def upsert_generated_section(content: str, generated_section: str) -> str:
	clean_content = content.rstrip()
	if _SECTION_PATTERN.search(clean_content):
		return _SECTION_PATTERN.sub(generated_section, clean_content)
	if clean_content:
		return f"{clean_content}\n\n{generated_section}"
	return generated_section
```

### `infrastructure/filesystem_entry_repository.py` (novo — concentra todo I/O de vault)
```python
from __future__ import annotations

import warnings
from datetime import date
from pathlib import Path
from typing import cast

import frontmatter

from ..domain.entry_date import require_entry_date, resolve_entry_date
from ..domain.models import AnalysisResult, EntryData, HabitData, ReportResult
from ..formatters.analysis_markdown import build_analysis_markdown
from ..formatters.report_markdown import build_report_markdown
from ..formatters.source_note import build_source_note_section, upsert_generated_section
from ..ports.entry_repository import EntryRepository

MONTH_NAMES = (
	"January", "February", "March", "April", "May", "June",
	"July", "August", "September", "October", "November", "December",
)


class FileSystemEntryRepository(EntryRepository):
	def __init__(self, vault_path: str | Path) -> None:
		self._vault_path = Path(vault_path)

	def load_entry(self, path: str | Path) -> EntryData:
		post = frontmatter.load(str(path))
		metadata = post.metadata
		habit_data = HabitData(
			mit=cast("str | None", metadata.get("mit")),
			sono=cast("float | None", metadata.get("sono")),
			estresse=cast("int | None", metadata.get("estresse")),
			energia_humor=cast("int | None", metadata.get("energia_humor")),
			hidratacao=cast("int | None", metadata.get("hidratacao")),
			sol_manha=cast("bool | None", metadata.get("sol_manha")),
			atividade_fisica=cast("bool | None", metadata.get("atividade_fisica")),
			leitura=cast("bool | None", metadata.get("leitura")),
			estudo=cast("bool | None", metadata.get("estudo")),
		)
		return EntryData(
			data=cast("date | None", metadata.get("data")),
			conteudo=post.content.strip(),
			habit_data=habit_data,
			caminho_origem=str(path),
		)

	def list_entries_in_range(self, start: date, end: date) -> list[EntryData]:
		diary_root = self._vault_path / "diary"
		entries: list[EntryData] = []
		for path in sorted(diary_root.rglob("*.md")):
			entry = self.load_entry(path)
			entry_date = resolve_entry_date(entry)
			if entry_date is None:
				continue
			if start <= entry_date <= end:
				entries.append(entry)
		if entries:
			self._warn_if_existing_derived_outputs(start)
		return entries

	def save_analysis(self, entry: EntryData, analysis: AnalysisResult) -> Path:
		entry_date = require_entry_date(entry)
		path = self._analysis_path_for_date(entry_date)
		path.parent.mkdir(parents=True, exist_ok=True)
		path.write_text(build_analysis_markdown(entry, analysis), encoding="utf-8")
		return path

	def save_report(
		self,
		start: date,
		end: date,
		report: ReportResult,
		entries: list[EntryData],
	) -> Path:
		path = self._report_path_for_date(start)
		path.parent.mkdir(parents=True, exist_ok=True)
		path.write_text(build_report_markdown(start, end, report, entries), encoding="utf-8")
		return path

	def mark_source_processed(self, entry: EntryData, analysis: AnalysisResult, analysis_path: Path) -> None:
		source_path = Path(entry.caminho_origem)
		if not source_path.exists():
			return
		post = frontmatter.load(str(source_path))
		post.metadata["processado"] = True
		section = build_source_note_section(require_entry_date(entry), analysis, analysis_path)
		post.content = upsert_generated_section(post.content, section)
		source_path.write_text(frontmatter.dumps(post), encoding="utf-8")

	def _warn_if_existing_derived_outputs(self, start: date) -> None:
		analysis_dir = self._analysis_dir_for_date(start)
		if analysis_dir.exists() and any(analysis_dir.glob("*.md")):
			warnings.warn("Preexisting analyses or reports found; regenerating from raw diary notes.")

	def _analysis_path_for_date(self, entry_date: date) -> Path:
		return self._analysis_dir_for_date(entry_date) / f"{entry_date.isoformat()}-analise.md"

	def _report_path_for_date(self, entry_date: date) -> Path:
		return self._analysis_dir_for_date(entry_date) / f"{entry_date.year:04d}-{entry_date.month:02d}-relatorio.md"

	def _analysis_dir_for_date(self, entry_date: date) -> Path:
		return self._vault_path / "analyses" / f"{entry_date.year:04d}" / _month_name(entry_date)


def _month_name(entry_date: date) -> str:
	return MONTH_NAMES[entry_date.month - 1]
```
Única classe que importa `frontmatter` e toca `Path.write_text`/`mkdir`. Toda a formatação continua delegada aos `formatters/` (puros, sem I/O) — separação clara entre "o que" (conteúdo) e "onde/como" (persistência).

### `infrastructure/llm/fake_adapter.py`
Conteúdo idêntico ao `core/llm/fake.py`, ajustando imports:
```python
from ..domain.models import ABCDE, AnalysisResult, CognitiveDistortion, HabitMoodCorrelation, ReportResult
from ..ports.llm_adapter import LLMAdapter
```
(restante do corpo da classe sem alteração)

### `infrastructure/llm/gemini_adapter.py`
Conteúdo idêntico ao `core/llm/gemini_adapter.py`, ajustando imports:
```python
from ..domain.models import AnalysisResult, ReportResult
from ..ports.llm_adapter import LLMAdapter, LLMResponseValidationError
from .prompt_loader import build_analysis_prompt, build_consolidation_prompt
```
(restante do corpo sem alteração)

### `infrastructure/llm/prompt_loader.py`
Conteúdo idêntico ao `core/llm/prompt_loader.py`, ajustando o pacote de recursos:
```python
PROMPTS_PACKAGE = "diarium_app.infrastructure.llm.prompts"
```
Os arquivos `analysis.txt` e `consolidation.txt` movem junto para `infrastructure/llm/prompts/`.

### `use_cases/analyze_entry.py`
```python
from __future__ import annotations

from pathlib import Path

from ..domain.entry_date import resolve_entry_date
from ..domain.models import AnalysisResult, EntryData
from ..ports.entry_repository import EntryRepository
from ..ports.llm_adapter import LLMAdapter


def analyze_entry(
	path: str | Path,
	llm: LLMAdapter,
	repo: EntryRepository,
) -> tuple[EntryData, AnalysisResult, Path]:
	entry = repo.load_entry(path)
	result = run_analysis(entry, llm)
	analysis_path = repo.save_analysis(entry, result)
	repo.mark_source_processed(entry, result, analysis_path)
	return entry, result, analysis_path


def run_analysis(entry: EntryData, llm: LLMAdapter) -> AnalysisResult:
	result = llm.analyze_entry(entry.conteudo, entry.habit_data.model_dump(mode="json"))
	result.entrada_origem = resolve_entry_date(entry)
	return result
```
`run_analysis` é reaproveitada por `generate_period_report` — sem I/O, fácil de testar isoladamente com `FakeLLMAdapter`.

### `use_cases/generate_period_report.py`
```python
from __future__ import annotations

from datetime import date
from pathlib import Path

from ..domain.models import AnalysisResult, ReportResult
from ..ports.entry_repository import EntryRepository
from ..ports.llm_adapter import LLMAdapter
from .analyze_entry import run_analysis


def generate_period_report(
	llm: LLMAdapter,
	repo: EntryRepository,
	start_date: date,
	end_date: date,
) -> tuple[ReportResult, Path]:
	entries = repo.list_entries_in_range(start_date, end_date)
	if not entries:
		raise ValueError("No diary entries found for the requested period")
	analyses: list[AnalysisResult] = []
	for entry in entries:
		analysis = run_analysis(entry, llm)
		analyses.append(analysis)
		analysis_path = repo.save_analysis(entry, analysis)
		repo.mark_source_processed(entry, analysis, analysis_path)
	report = llm.consolidate(
		analyses,
		[entry.habit_data.model_dump(mode="json") for entry in entries],
	)
	report_path = repo.save_report(start_date, end_date, report, entries)
	return report, report_path
```
Nota: o parâmetro `update_source` que existia em `write_analysis`/`generate_period_report` foi removido nesta versão por simplicidade. Se ainda for necessário desligar a atualização da nota-fonte, adicionar um parâmetro `update_source: bool = True` neste use case e condicionar a chamada a `repo.mark_source_processed`.

### `config.py`
```python
from __future__ import annotations

from collections.abc import Callable
from datetime import date
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .infrastructure.llm.fake_adapter import FakeLLMAdapter
from .infrastructure.llm.gemini_adapter import GeminiAdapter
from .ports.llm_adapter import LLMAdapter


def _default_vault_path() -> Path:
	return Path(__file__).resolve().parents[3] / "diarium-vault"


class Settings(BaseSettings):
	model_config = SettingsConfigDict(env_prefix="DIARIUM_", env_file=".env", extra="ignore")

	llm_provider: str = "fake"
	llm_api_key: str | None = None
	llm_model: str = "gemini-2.5-flash"
	vault_path: Path = Field(default_factory=_default_vault_path)
	default_report_start: date | None = None
	default_report_end: date | None = None


ProviderFactory = Callable[[Settings], LLMAdapter]

_PROVIDERS: dict[str, ProviderFactory] = {}


def register_provider(name: str, factory: ProviderFactory) -> None:
	_PROVIDERS[name.lower()] = factory


def build_adapter(settings: Settings) -> LLMAdapter:
	factory = _PROVIDERS.get(settings.llm_provider.lower())
	if factory is None:
		raise ValueError(f"Unsupported llm_provider: {settings.llm_provider}")
	return factory(settings)


def _build_gemini_adapter(settings: Settings) -> LLMAdapter:
	if not settings.llm_api_key:
		raise ValueError("DIARIUM_LLM_API_KEY is required when llm_provider=gemini")
	return GeminiAdapter(api_key=settings.llm_api_key, model_name=settings.llm_model)


register_provider("fake", lambda settings: FakeLLMAdapter())
register_provider("gemini", _build_gemini_adapter)


def load_settings() -> Settings:
	return Settings()
```
Novo provider passa a ser `register_provider("nome", factory)` — sem editar `build_adapter` (OCP). `parents[3]` mantido pois `config.py` continua em `src/diarium_app/config.py`, mesma profundidade de antes.

### `cli/main.py`
```python
from __future__ import annotations

from datetime import date
from pathlib import Path

import typer

from ..config import Settings, build_adapter, load_settings
from ..infrastructure.filesystem_entry_repository import FileSystemEntryRepository
from ..use_cases.analyze_entry import analyze_entry as run_analyze_entry
from ..use_cases.generate_period_report import generate_period_report

app = typer.Typer(help="Diarium CLI")


@app.command()
def analisar(
	arquivo: Path,
	provider: str | None = typer.Option(None, help="Override llm provider"),
	api_key: str | None = typer.Option(None, help="Override llm api key"),
	model: str | None = typer.Option(None, help="Override llm model"),
	vault_path: Path | None = typer.Option(None, help="Override vault path"),
) -> None:
	settings = _load_overrides(provider, api_key, model, vault_path)
	llm = build_adapter(settings)
	repo = FileSystemEntryRepository(settings.vault_path)
	_, _, analysis_path = run_analyze_entry(arquivo, llm, repo)
	typer.echo(str(analysis_path))


@app.command()
def relatorio(
	de: str = typer.Option(..., "--de", help="Start date"),
	ate: str = typer.Option(..., "--ate", help="End date"),
	provider: str | None = typer.Option(None, help="Override llm provider"),
	api_key: str | None = typer.Option(None, help="Override llm api key"),
	model: str | None = typer.Option(None, help="Override llm model"),
	vault_path: Path | None = typer.Option(None, help="Override vault path"),
) -> None:
	settings = _load_overrides(provider, api_key, model, vault_path)
	llm = build_adapter(settings)
	repo = FileSystemEntryRepository(settings.vault_path)
	start_date = date.fromisoformat(de)
	end_date = date.fromisoformat(ate)
	_, report_path = generate_period_report(llm, repo, start_date, end_date)
	typer.echo(str(report_path))


def _load_overrides(
	provider: str | None,
	api_key: str | None,
	model: str | None,
	vault_path: Path | None,
) -> Settings:
	settings = load_settings()
	updates: dict[str, object] = {}
	if provider is not None:
		updates["llm_provider"] = provider
	if api_key is not None:
		updates["llm_api_key"] = api_key
	if model is not None:
		updates["llm_model"] = model
	if vault_path is not None:
		updates["vault_path"] = vault_path
	if updates:
		settings = settings.model_copy(update=updates)
	return settings


def main() -> None:
	app()
```
CLI passa a ser o composition root: monta `Settings`, resolve `LLMAdapter` via registry, instancia `FileSystemEntryRepository`, injeta os dois nos use cases. Nenhuma lógica de negócio ou I/O de vault dentro do CLI.

---

## Migração incremental

1. Criar `domain/`, `ports/` (sem remover nada do `core/` ainda) — build continua verde.
2. Criar `formatters/` movendo as funções puras de `core/report.py`.
3. Criar `infrastructure/filesystem_entry_repository.py` e `infrastructure/llm/*`, movendo `core/parser.py` + I/O de `core/report.py` + `core/llm/*`.
4. Criar `use_cases/analyze_entry.py` e `use_cases/generate_period_report.py`.
5. Atualizar `config.py` (registry) e `cli/main.py` (composition root).
6. Apagar `core/` (models.py, parser.py, analysis.py, report.py, llm/).
7. Atualizar imports em `tests/test_analysis_report.py`, `tests/test_cli.py`, `tests/test_llm_adapter.py` para os novos caminhos. Onde os testes hoje usam `tmp_path` + `FileSystemEntryRepository`-equivalente implícito, considerar um `InMemoryEntryRepository` de teste (implementa `EntryRepository` guardando tudo em dicionários) para os testes de use case, mantendo 1-2 testes de integração contra `FileSystemEntryRepository` real.
8. Rodar `pytest` a cada etapa (2–6), não só no final.
