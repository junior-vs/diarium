from __future__ import annotations

from diarium_app.core.llm import FakeLLMAdapter, build_analysis_prompt, build_consolidation_prompt, load_prompt
from diarium_app.core.models import AnalysisResult, ReportResult


def test_fake_adapter_returns_structured_analysis() -> None:
	adapter = FakeLLMAdapter()
	result = adapter.analyze_entry("Vai dar tudo errado", {"sono": 5})

	assert isinstance(result, AnalysisResult)
	assert result.distorcoes[0].tipo == "catastrofização"
	assert result.abcde is not None
	assert result.resumo == "Análise sintética de teste."
	assert len(adapter.analyze_calls) == 1


def test_fake_adapter_returns_structured_report() -> None:
	adapter = FakeLLMAdapter()
	result = adapter.consolidate([], [{"data": "2026-09-01"}])

	assert isinstance(result, ReportResult)
	assert result.distorcoes_recorrentes == ["catastrofização"]
	assert result.correlacoes_habito_humor[0].habito == "sono"
	assert len(adapter.consolidate_calls) == 1


def test_prompt_loader_reads_versioned_assets() -> None:
	prompt = load_prompt("analysis.txt")

	assert "{front_matter_dados}" in prompt
	assert "{conteudo_do_diario}" in prompt


def test_prompt_helpers_render_expected_values() -> None:
	analysis_prompt = build_analysis_prompt("sono=8", "texto do diário")
	consolidation_prompt = build_consolidation_prompt(
		"2026-09-01",
		"2026-09-30",
		"[{'sono': 8}]",
		"[{'resumo': 'ok'}]",
	)

	assert "sono=8" in analysis_prompt
	assert "texto do diário" in analysis_prompt
	assert "2026-09-01" in consolidation_prompt
	assert "2026-09-30" in consolidation_prompt
