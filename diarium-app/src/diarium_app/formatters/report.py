from __future__ import annotations

import re
import warnings
from datetime import date
from pathlib import Path
from typing import Any

import frontmatter

from ..use_cases.analyze_entry import _resolve_entry_date, analyze_entry
from ..infrastructure.llm import LLMAdapter
from ..domain.models import AnalysisResult, EntryData, ReportResult
from ..infrastructure.parser import parse_entry

MONTH_NAMES = (
	"January",
	"February",
	"March",
	"April",
	"May",
	"June",
	"July",
	"August",
	"September",
	"October",
	"November",
	"December",
)

SOURCE_BLOCK_START = "<!-- diarium:analysis:start -->"
SOURCE_BLOCK_END = "<!-- diarium:analysis:end -->"


def write_analysis(
	entry: EntryData,
	analysis: AnalysisResult,
	vault_path: str | Path,
	update_source: bool = True,
) -> Path:
	entry_date = _require_entry_date(entry)
	analysis_path = _analysis_path_for_date(Path(vault_path), entry_date)
	analysis_path.parent.mkdir(parents=True, exist_ok=True)
	analysis_path.write_text(build_analysis_markdown(entry, analysis), encoding="utf-8")
	if update_source:
		_update_source_note(entry, analysis, analysis_path)
	return analysis_path


def build_analysis_markdown(entry: EntryData, analysis: AnalysisResult) -> str:
	entry_date = _require_entry_date(entry)
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
	sections.extend([
		"",
		"### ABCDE",
	])
	if analysis.abcde is None or not any([analysis.abcde.a, analysis.abcde.b, analysis.abcde.c, analysis.abcde.d, analysis.abcde.e]):
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


def generate_period_report(
	vault_path: str | Path,
	adapter: LLMAdapter,
	start_date: date,
	end_date: date,
	update_source: bool = True,
) -> tuple[ReportResult, Path]:
	vault_root = Path(vault_path)
	entries = collect_entries_in_range(vault_root, start_date, end_date)
	if not entries:
		raise ValueError("No diary entries found for the requested period")
	warn_if_existing_derived_outputs(vault_root, start_date)
	analyses: list[AnalysisResult] = []
	for entry in entries:
		analysis = analyze_entry(entry, adapter)
		analyses.append(analysis)
		write_analysis(entry, analysis, vault_root, update_source=update_source)
	report = adapter.consolidate(analyses, [entry.habit_data.model_dump(mode="json") for entry in entries])
	report_path = write_report(vault_root, start_date, end_date, report, entries)
	return report, report_path


def write_report(
	vault_path: str | Path,
	start_date: date,
	end_date: date,
	report: ReportResult,
	entries: list[EntryData],
) -> Path:
	report_path = _report_path_for_date(Path(vault_path), start_date)
	report_path.parent.mkdir(parents=True, exist_ok=True)
	report_path.write_text(build_report_markdown(start_date, end_date, report, entries), encoding="utf-8")
	return report_path


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
		entry_date = _require_entry_date(entry)
		lines.append(f"- [[{entry_date.isoformat()}]]")
	post = frontmatter.Post("\n".join(lines).strip() + "\n", **metadata)
	return frontmatter.dumps(post)


def collect_entries_in_range(vault_path: Path, start_date: date, end_date: date) -> list[EntryData]:
	diary_root = vault_path / "diary"
	entries: list[EntryData] = []
	for path in sorted(diary_root.rglob("*.md")):
		entry = parse_entry(path)
		entry_date = _resolve_entry_date(entry)
		if entry_date is None:
			continue
		if start_date <= entry_date <= end_date:
			entries.append(entry)
	return entries


def warn_if_existing_derived_outputs(vault_path: Path, start_date: date) -> None:
	analysis_dir = _analysis_dir_for_date(vault_path, start_date)
	if analysis_dir.exists() and any(analysis_dir.glob("*.md")):
		warnings.warn("Preexisting analyses or reports found; regenerating from raw diary notes.")


def _update_source_note(entry: EntryData, analysis: AnalysisResult, analysis_path: Path) -> None:
	source_path = Path(entry.caminho_origem)
	if not source_path.exists():
		return
	post = frontmatter.load(str(source_path))
	post.metadata["processado"] = True
	post.content = _upsert_generated_section(post.content, _build_source_note_section(_require_entry_date(entry), analysis, analysis_path))
	source_path.write_text(frontmatter.dumps(post), encoding="utf-8")


def _build_source_note_section(entry_date: date, analysis: AnalysisResult, analysis_path: Path) -> str:
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


def _upsert_generated_section(content: str, generated_section: str) -> str:
	pattern = re.compile(
		rf"{re.escape(SOURCE_BLOCK_START)}.*?{re.escape(SOURCE_BLOCK_END)}\n?",
		re.DOTALL,
	)
	clean_content = content.rstrip()
	if pattern.search(clean_content):
		return pattern.sub(generated_section, clean_content)
	if clean_content:
		return f"{clean_content}\n\n{generated_section}"
	return generated_section


def _analysis_path_for_date(vault_path: Path, entry_date: date) -> Path:
	return vault_path / "analyses" / f"{entry_date.year:04d}" / _month_name(entry_date) / f"{entry_date.isoformat()}-analise.md"


def _report_path_for_date(vault_path: Path, entry_date: date) -> Path:
	return vault_path / "analyses" / f"{entry_date.year:04d}" / _month_name(entry_date) / f"{entry_date.year:04d}-{entry_date.month:02d}-relatorio.md"


def _analysis_dir_for_date(vault_path: Path, entry_date: date) -> Path:
	return vault_path / "analyses" / f"{entry_date.year:04d}" / _month_name(entry_date)


def _month_name(entry_date: date) -> str:
	return MONTH_NAMES[entry_date.month - 1]


def _require_entry_date(entry: EntryData) -> date:
	entry_date = _resolve_entry_date(entry)
	if entry_date is None:
		raise ValueError(f"Could not determine entry date for {entry.caminho_origem}")
	return entry_date


def _render_bullets(items: list[str], empty_message: str) -> list[str]:
	if not items:
		return [f"- {empty_message}"]
	return [f"- {item}" for item in items]
