from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import cast

import frontmatter

from ..domain.entry_date import require_entry_date, resolve_entry_date
from ..domain.models import (
	AnalysisResult,
	AtividadeSignificativa,
	EntryData,
	HabitData,
	ReportResult,
	TrendReportResult,
)
from ..formatters.analysis_markdown import build_analysis_markdown
from ..formatters.report_markdown import build_report_markdown
from ..formatters.source_note import build_source_note_section, upsert_generated_section
from ..formatters.trend_markdown import build_trend_markdown
from ..ports.entry_repository import EntryRepository
from .asset_loader import load_footer, load_safety_block


class FileSystemEntryRepository(EntryRepository):
	def __init__(self, vault_path: str | Path) -> None:
		self._vault_path = Path(vault_path)

	def load_entry(self, path: str | Path) -> EntryData:
		"""Carregar uma entrada de diário a partir de um arquivo Markdown com frontmatter."""
		post = frontmatter.load(str(path))
		metadata = post.metadata
		raw_ativ = metadata.get("atividade_significativa")
		atividade_significativa: AtividadeSignificativa | None = None
		if isinstance(raw_ativ, dict):
			atividade_significativa = AtividadeSignificativa(
				descricao=cast("str | None", raw_ativ.get("descricao")),
				prazer=cast("int | None", raw_ativ.get("prazer")),
				dominio=cast("int | None", raw_ativ.get("dominio")),
			)
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
			atividade_significativa=atividade_significativa,
			positive_data_log=cast("str | None", metadata.get("positive_data_log")),
		)
		return EntryData(
			data=cast("date | None", metadata.get("data")),
			conteudo=post.content.strip(),
			habit_data=habit_data,
			caminho_origem=str(path),
		)

	def list_entries_in_range(self, start: date, end: date) -> list[EntryData]:
		"""Listar todas as entradas de diário dentro de um intervalo de datas, em ordem cronológica."""
		diary_root = self._vault_path / "diary"
		entries: list[EntryData] = []
		for path in diary_root.rglob("*.md"):
			entry = self.load_entry(path)
			entry_date = resolve_entry_date(entry)
			if entry_date is None:
				continue
			if start <= entry_date <= end:
				entries.append(entry)
		# Ordena pela data resolvida (não pelo path) para garantir ordem
		# cronológica independente da convenção de pastas do vault. Neste ponto
		# todas as entradas já passaram pelo filtro de data resolvível acima,
		# então require_entry_date nunca lança e o tipo fica (EntryData) -> date.
		entries.sort(key=require_entry_date)
		return entries

	def find_existing_analysis(self, entry: EntryData) -> AnalysisResult | None:
		"""Retornar a análise já persistida para a entrada, se existir e for reconstruível."""
		entry_date = resolve_entry_date(entry)
		if entry_date is None:
			return None
		path = self._analysis_path_for_date(entry_date)
		if not path.exists():
			return None
		post = frontmatter.load(str(path))
		raw_analysis = post.metadata.get("analysis_json")
		if raw_analysis is None:
			return None
		try:
			return AnalysisResult.model_validate(raw_analysis)
		except Exception:  # noqa: BLE001 - defensive boundary de dado persistido, ver comentário abaixo
			# Arquivo de análise presente mas sem payload reconstruível
			# (ex.: editado manualmente, ou gerado por uma versão anterior).
			return None

	def save_analysis(self, entry: EntryData, analysis: AnalysisResult) -> Path:
		"""Salvar a análise de uma entrada de diário e retornar o caminho do arquivo gerado."""
		entry_date = require_entry_date(entry)
		path = self._analysis_path_for_date(entry_date)
		path.parent.mkdir(parents=True, exist_ok=True)
		safety_block = load_safety_block()
		footer = load_footer()
		path.write_text(
			build_analysis_markdown(entry, analysis, safety_block=safety_block, footer=footer),
			encoding="utf-8",
		)
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
		footer = load_footer()
		path.write_text(build_report_markdown(start, end, report, entries, footer=footer), encoding="utf-8")
		return path

	def find_existing_report(self, start: date, end: date) -> ReportResult | None:
		"""Retornar um relatório de sub-período já persistido, se existir."""
		path = self._report_path_for_date(start)
		if not path.exists():
			return None
		post = frontmatter.load(str(path))
		raw_report = post.metadata.get("report_json")
		if raw_report is None:
			return None
		try:
			return ReportResult.model_validate(raw_report)
		except Exception:  # noqa: BLE001
			return None

	def save_trend_report(self, start: date, end: date, trend: TrendReportResult) -> Path:
		"""Persistir um relatório de tendência e retornar seu caminho."""
		path = self._trend_report_path_for_range(start, end)
		path.parent.mkdir(parents=True, exist_ok=True)
		footer = load_footer()
		path.write_text(build_trend_markdown(start, end, trend, footer=footer), encoding="utf-8")
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

	def _analysis_path_for_date(self, entry_date: date) -> Path:
		"""Retornar o caminho do arquivo de análise para a data fornecida."""
		return self._analysis_dir_for_date(entry_date) / f"{entry_date.isoformat()}-analise.md"

	def _report_path_for_date(self, entry_date: date) -> Path:
		"""Retornar o caminho do arquivo de relatório para a data fornecida."""
		return self._analysis_dir_for_date(entry_date) / f"{entry_date.year:04d}-{entry_date.month:02d}-relatorio.md"

	def _trend_report_path_for_range(self, start: date, end: date) -> Path:
		"""Retornar o caminho do arquivo de relatório de tendência para o intervalo fornecido."""
		return self._vault_path / "analyses" / f"{start.year:04d}" / f"{start.isoformat()}_{end.isoformat()}-tendencia.md"

	def _analysis_dir_for_date(self, entry_date: date) -> Path:
		"""Retornar o diretório de análises para a data fornecida: analyses/AAAA/MM."""
		return self._vault_path / "analyses" / f"{entry_date.year:04d}" / f"{entry_date.month:02d}"