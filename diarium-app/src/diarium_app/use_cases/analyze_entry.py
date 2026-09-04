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
	"""Analyze a diary entry and return the entry data, analysis result, and analysis file path."""
	entry = repo.load_entry(path)
	result = run_analysis(entry, llm)
	analysis_path = repo.save_analysis(entry, result)
	repo.mark_source_processed(entry, result, analysis_path)
	return entry, result, analysis_path


def run_analysis(entry: EntryData, llm: LLMAdapter) -> AnalysisResult:
	"""Run analysis on a diary entry using the provided LLM adapter."""

	result = llm.analyze_entry(entry.conteudo, entry.habit_data.model_dump(mode="json"))
	result.entrada_origem = resolve_entry_date(entry)
	return result
