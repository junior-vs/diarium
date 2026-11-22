from __future__ import annotations

from diarium_app.infrastructure.llm import FakeLLMAdapter, build_analysis_prompt, build_consolidation_prompt, load_prompt
from diarium_app.domain.models import AnalysisResult, ReportResult, RiskScreeningResult


def test_fake_adapter_returns_structured_analysis() -> None:
	adapter = FakeLLMAdapter()
	result = adapter.analyze_entry("Vai dar tudo errado", {"sono": 5})

	assert isinstance(result, AnalysisResult)
	assert result.distorcoes[0].tipo == "catastrofização"
	assert len(result.gatilhos) == 1
	assert result.gatilhos[0].comportamento == "Evitei checar as mensagens de trabalho."
	assert len(result.gatilhos[0].d_perguntas) == 2
	assert result.abcde is not None
	assert result.resumo == "Análise sintética de teste."
	assert len(adapter.analyze_calls) == 1


def test_fake_adapter_screen_risk() -> None:
	adapter = FakeLLMAdapter(default_risk=RiskScreeningResult.POSSIVEL_RISCO)
	risk = adapter.screen_risk("texto sensível")

	assert risk == RiskScreeningResult.POSSIVEL_RISCO
	assert adapter.screen_risk_calls == ["texto sensível"]


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


def test_gemini_adapter_screen_risk_uses_structured_schema() -> None:
	from unittest.mock import MagicMock
	from diarium_app.infrastructure.llm.gemini_adapter import GeminiAdapter, RiskScreeningResponse

	adapter = GeminiAdapter(api_key="test-key")
	mock_response = MagicMock()
	mock_response.parsed = RiskScreeningResponse(risco=RiskScreeningResult.POSSIVEL_RISCO)
	adapter._client.models.generate_content = MagicMock(return_value=mock_response)

	risk = adapter.screen_risk("Texto de teste")
	assert risk == RiskScreeningResult.POSSIVEL_RISCO
	adapter._client.models.generate_content.assert_called_once()

