from __future__ import annotations

from datetime import date
from pathlib import Path

from ..domain.models import AnalysisResult, ReportResult
from ..ports.entry_repository import EntryRepository
from ..ports.llm_adapter import LLMAdapter
from .analyze_entry import build_entry_payload, run_analysis


def generate_period_report(
	llm: LLMAdapter,
	repo: EntryRepository,
	start_date: date,
	end_date: date,
	*,
	force_recompute: bool = False,
) -> tuple[ReportResult, Path]:
	"""Generate a consolidated report for a given period using the provided LLM adapter.

	Entradas que já possuem uma análise persistida (com payload reconstruível)
	são reaproveitadas em vez de recomputadas, a menos que ``force_recompute``
	seja ``True``.
	"""
	entries = repo.list_entries_in_range(start_date, end_date)
	if not entries:
		raise ValueError("No diary entries found for the requested period")
	analyses: list[AnalysisResult] = []
	for entry in entries:
		existing = None if force_recompute else repo.find_existing_analysis(entry)
		if existing is not None:
			analyses.append(existing)
			continue
		analysis = run_analysis(entry, llm)
		analyses.append(analysis)
		analysis_path = repo.save_analysis(entry, analysis)
		repo.mark_source_processed(entry, analysis, analysis_path)
	report = llm.consolidate(
		analyses,
		[build_entry_payload(entry) for entry in entries],
	)
	report_path = repo.save_report(start_date, end_date, report, entries)
	return report, report_path