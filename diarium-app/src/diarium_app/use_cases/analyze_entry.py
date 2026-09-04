from __future__ import annotations

from pathlib import Path

from ..domain.entry_date import require_entry_date
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
	entry_date = require_entry_date(entry)
	result = llm.analyze_entry(entry.conteudo, build_entry_payload(entry))
	result.entrada_origem = entry_date
	return result


def build_entry_payload(entry: EntryData) -> dict[str, object]:
	"""Build the structured payload sent to the LLM for a single entry."""
	entry_date = require_entry_date(entry)
	payload = entry.habit_data.model_dump(mode="json")
	payload["data"] = entry_date.isoformat()
	return payload
