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
		"""Carregar uma entrada de diário a partir de um arquivo Markdown com frontmatter."""
		
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
		"""Listar todas as entradas de diário dentro de um intervalo de datas."""
		
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
		"""Salvar a análise de uma entrada de diário e retornar o caminho do arquivo gerado."""
		
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
		"""Salvar o relatório de um intervalo de entradas de diário e retornar o caminho do arquivo gerado."""
		path = self._report_path_for_date(start)
		path.parent.mkdir(parents=True, exist_ok=True)
		path.write_text(build_report_markdown(start, end, report, entries), encoding="utf-8")
		return path

	def mark_source_processed(self, entry: EntryData, analysis: AnalysisResult, analysis_path: Path) -> None:
		"""Marcar a entrada de diário como processada e atualizar a seção de nota de origem."""
		source_path = Path(entry.caminho_origem)
		if not source_path.exists():
			return
		post = frontmatter.load(str(source_path))
		post.metadata["processado"] = True
		section = build_source_note_section(require_entry_date(entry), analysis, analysis_path)
		post.content = upsert_generated_section(post.content, section)
		source_path.write_text(frontmatter.dumps(post), encoding="utf-8")

	def _warn_if_existing_derived_outputs(self, start: date) -> None:
		"""Emitir um aviso se existirem análises ou relatórios derivados pré-existentes para a data fornecida."""
		analysis_dir = self._analysis_dir_for_date(start)
		if analysis_dir.exists() and any(analysis_dir.glob("*.md")):
			warnings.warn("Preexisting analyses or reports found; regenerating from raw diary notes.")

	def _analysis_path_for_date(self, entry_date: date) -> Path:
		"""Retornar o caminho do arquivo de análise para a data fornecida."""
		return self._analysis_dir_for_date(entry_date) / f"{entry_date.isoformat()}-analise.md"

	def _report_path_for_date(self, entry_date: date) -> Path:
		"""Retornar o caminho do arquivo de relatório para a data fornecida."""
		return self._analysis_dir_for_date(entry_date) / f"{entry_date.year:04d}-{entry_date.month:02d}-relatorio.md"

	def _analysis_dir_for_date(self, entry_date: date) -> Path:
		"""Retornar o diretório de análises para a data fornecida."""
		return self._vault_path / "analyses" / f"{entry_date.year:04d}" / _month_name(entry_date)


def _month_name(entry_date: date) -> str:
	"""Retornar o nome do mês correspondente à data fornecida."""
	return MONTH_NAMES[entry_date.month - 1]
