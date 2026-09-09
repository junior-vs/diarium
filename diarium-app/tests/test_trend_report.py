from __future__ import annotations

from datetime import date
from pathlib import Path

from diarium_app.domain.models import HabitMoodCorrelation, ReportResult
from diarium_app.infrastructure.filesystem_entry_repository import FileSystemEntryRepository
from diarium_app.infrastructure.llm.fake_adapter import FakeLLMAdapter
from diarium_app.use_cases.analyze_entry import analyze_entry, build_entry_payload
from diarium_app.use_cases.generate_period_report import generate_period_report
from diarium_app.use_cases.generate_trend_report import generate_trend_report, list_monthly_subperiods


def _write_diary(tmp_path: Path, day: str) -> Path:
	parts = day.split("-")
	month_dir = tmp_path / "diary" / parts[0] / parts[1]
	month_dir.mkdir(parents=True, exist_ok=True)
	path = month_dir / f"{day}.md"
	path.write_text(
		f"""---
data: {day}
tags: [diario]
processado: false
mit: tarefa
sono: 7
estresse: 3
energia_humor: 4
---

# Diário
Hoje foi um dia comum.
""",
		encoding="utf-8",
	)
	return path


def test_list_monthly_subperiods() -> None:
	subperiods = list_monthly_subperiods(date(2026, 1, 15), date(2026, 3, 20))
	assert len(subperiods) == 3
	assert subperiods[0] == (date(2026, 1, 15), date(2026, 1, 31))
	assert subperiods[1] == (date(2026, 2, 1), date(2026, 2, 28))
	assert subperiods[2] == (date(2026, 3, 1), date(2026, 3, 20))


def test_min_data_guard_activates_below_threshold(tmp_path: Path) -> None:
	"""RF09: Com menos de 5 entradas, dados_insuficientes=True e seções limpas."""
	repo = FileSystemEntryRepository(tmp_path)
	adapter = FakeLLMAdapter()

	# Apenas 3 entradas (< 5)
	for day in ["2026-09-01", "2026-09-02", "2026-09-03"]:
		_write_diary(tmp_path, day)

	report, report_path = generate_period_report(adapter, repo, date(2026, 9, 1), date(2026, 9, 30))

	assert report.dados_insuficientes is True
	assert report.correlacoes_habito_humor == []
	assert report.tema_recorrente is None

	content = report_path.read_text(encoding="utf-8")
	assert "Dados insuficientes para correlacionar hábitos e humor" in content
	assert "Dados insuficientes para identificar tema recorrente" in content


def test_min_data_guard_preserves_data_when_threshold_met(tmp_path: Path) -> None:
	"""RF09: Com 5 ou mais entradas, mantém correlações e temas calculados."""
	repo = FileSystemEntryRepository(tmp_path)
	adapter = FakeLLMAdapter()

	# 5 entradas (>= 5)
	for day in ["2026-09-01", "2026-09-02", "2026-09-03", "2026-09-04", "2026-09-05"]:
		_write_diary(tmp_path, day)

	report, report_path = generate_period_report(adapter, repo, date(2026, 9, 1), date(2026, 9, 30))

	assert report.dados_insuficientes is False
	assert len(report.correlacoes_habito_humor) > 0
	content = report_path.read_text(encoding="utf-8")
	assert "sono" in content


def test_generate_trend_report_aggregates_existing_and_identifies_missing_subperiods(tmp_path: Path) -> None:
	"""RF07 e RF08: Agrega sub-períodos processados e aponta ausências explicitamente."""
	repo = FileSystemEntryRepository(tmp_path)
	adapter = FakeLLMAdapter()

	# Sub-período 1: 2026-01 (gerar relatório salvo)
	e1 = _write_diary(tmp_path, "2026-01-10")
	entry1 = repo.load_entry(e1)
	rep_jan = ReportResult(
		distorcoes_recorrentes=["catastrofização"],
		correlacoes_habito_humor=[HabitMoodCorrelation(habito="sono", relacao="menos sono coincide com estresse")],
		tema_recorrente="Pode haver preocupação com desempenho no trabalho?",
	)
	repo.save_report(date(2026, 1, 1), date(2026, 1, 31), rep_jan, [entry1])

	# Sub-período 2: 2026-02 FALTANTE (não salvamos relatório para fevereiro)

	# Sub-período 3: 2026-03 (gerar relatório salvo)
	e3 = _write_diary(tmp_path, "2026-03-15")
	entry3 = repo.load_entry(e3)
	rep_mar = ReportResult(
		distorcoes_recorrentes=["leitura mental"],
		correlacoes_habito_humor=[HabitMoodCorrelation(habito="sono", relacao="sono regular coincide com bom humor")],
		tema_recorrente="Pode haver preocupação com a percepção dos outros?",
	)
	repo.save_report(date(2026, 3, 1), date(2026, 3, 31), rep_mar, [entry3])

	# Executar relatório de tendência trimestral
	trend, trend_path = generate_trend_report(repo, date(2026, 1, 1), date(2026, 3, 31))

	# RF08: Sub-período ausente identificado
	assert trend.sub_periodos_ausentes == ["2026-02"]

	# RF07: Variações entre sub-períodos
	assert any("catastrofização" in t for t in trend.variacao_temas)
	assert any("leitura mental" in t for t in trend.variacao_temas)
	assert any("2026-01" in c for c in trend.variacao_correlacoes)
	assert any("2026-03" in c for c in trend.variacao_correlacoes)

	assert trend_path.exists()
	content = trend_path.read_text(encoding="utf-8")
	assert "## Relatório de Tendência" in content
	assert "### Sub-períodos ausentes" in content
	assert "2026-02" in content
	assert "Limite de Papel" in content  # RF18 footer
