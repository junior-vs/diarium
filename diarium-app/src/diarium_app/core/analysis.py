from __future__ import annotations

import re
from datetime import date, datetime
from pathlib import Path

from .llm import LLMAdapter
from .models import AnalysisResult, EntryData
from .parser import parse_entry


def analyze(path: str | Path, adapter: LLMAdapter) -> AnalysisResult:
	entry = parse_entry(path)
	return analyze_entry(entry, adapter)


def analyze_entry(entry: EntryData, adapter: LLMAdapter) -> AnalysisResult:
	result = adapter.analyze_entry(entry.conteudo, entry.habit_data.model_dump(mode="json"))
	result.entrada_origem = _resolve_entry_date(entry)
	return result


def _resolve_entry_date(entry: EntryData) -> date | None:
	if entry.data is not None:
		return entry.data
	path_date = _infer_date_from_path(entry.caminho_origem)
	if path_date is not None:
		return path_date
	return None


def _infer_date_from_path(path_value: str) -> date | None:
	stem = Path(path_value).stem
	match = re.search(r"\d{4}-\d{2}-\d{2}", stem)
	if not match:
		return None
	try:
		return datetime.strptime(match.group(0), "%Y-%m-%d").date()
	except ValueError:
		return None
