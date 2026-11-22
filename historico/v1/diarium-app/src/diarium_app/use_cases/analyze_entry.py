from __future__ import annotations

from pathlib import Path

from ..domain.entry_date import require_entry_date
from ..domain.models import AnalysisResult, EntryData, RiskScreeningResult
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

def build_entry_payload(entry: EntryData) -> dict[str, object]:
	"""Build the structured payload sent to the LLM for a single entry."""
	entry_date = require_entry_date(entry)
	payload = entry.habit_data.model_dump(mode="json")
	payload["data"] = entry_date.isoformat()
	return payload

def run_analysis(entry: EntryData, llm: LLMAdapter) -> AnalysisResult:
    entry_date = require_entry_date(entry)
    risco = llm.screen_risk(entry.conteudo)          # RF15 — antes, independente
    result = llm.analyze_entry(entry.conteudo, build_entry_payload(entry))
    for gatilho in result.gatilhos:
        bloco_texto = " ".join(filter(None, [gatilho.a, gatilho.b, gatilho.c]))
        if bloco_texto and llm.screen_risk(bloco_texto) is RiskScreeningResult.POSSIVEL_RISCO:
            risco = RiskScreeningResult.POSSIVEL_RISCO
    result.entrada_origem = entry_date
    result.risco = risco
    return result