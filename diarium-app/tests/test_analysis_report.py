from __future__ import annotations

from datetime import date
from pathlib import Path

from diarium_app.infrastructure.filesystem_entry_repository import FileSystemEntryRepository
from diarium_app.infrastructure.llm import FakeLLMAdapter
from diarium_app.formatters.analysis_markdown import build_analysis_markdown
from diarium_app.formatters.report_markdown import build_report_markdown
from diarium_app.use_cases.analyze_entry import analyze_entry, build_entry_payload, run_analysis
from diarium_app.use_cases.generate_period_report import generate_period_report


def _write_diary(tmp_path: Path, day: str, extra_frontmatter: str = "") -> Path:
	month_dir = tmp_path / "diary" / "2026" / "September"
	month_dir.mkdir(parents=True, exist_ok=True)
	path = month_dir / f"{day}.md"
	path.write_text(
		f"""---
data: {day}
tags: [diario]
processado: false
mit: tarefa importante
sono: 7
estresse: 3
energia_humor: 4
hidratacao: 6
sol_manha: true
atividade_fisica: false
leitura: true
estudo: false
{extra_frontmatter}---

# Diário
Hoje foi puxado, mas consegui terminar algumas coisas.
""",
		encoding="utf-8",
	)
	return path


def test_analysis_flow_produces_markdown_and_updates_source_note(tmp_path: Path) -> None:
	entry_path = _write_diary(tmp_path, "2026-09-03")
	repo = FileSystemEntryRepository(tmp_path)
	adapter = FakeLLMAdapter()
	entry, analysis, analysis_path = analyze_entry(entry_path, adapter, repo)

	assert analysis.entrada_origem == date(2026, 9, 3)
	assert analysis_path == tmp_path / "analyses" / "2026" / "September" / "2026-09-03-analise.md"
	assert "## Análise" in analysis_path.read_text(encoding="utf-8")
	assert adapter.analyze_calls[0][1]["data"] == "2026-09-03"
	source_text = entry_path.read_text(encoding="utf-8")
	assert "processado: true" in source_text
	assert "diarium:analysis:start" in source_text


def test_report_flow_uses_raw_entries_and_writes_monthly_report(tmp_path: Path) -> None:
	_write_diary(tmp_path, "2026-09-03")
	_write_diary(tmp_path, "2026-09-04")
	repo = FileSystemEntryRepository(tmp_path)
	adapter = FakeLLMAdapter()

	report, report_path = generate_period_report(adapter, repo, date(2026, 9, 1), date(2026, 9, 30))

	assert report.distorcoes_recorrentes == ["catastrofização"]
	assert report_path == tmp_path / "analyses" / "2026" / "September" / "2026-09-relatorio.md"
	assert "## Relatório Consolidado" in report_path.read_text(encoding="utf-8")
	assert len(adapter.consolidate_calls) == 1
	assert len(adapter.analyze_calls) == 2
	assert adapter.consolidate_calls[0][1][0]["data"] == "2026-09-03"
	assert adapter.consolidate_calls[0][1][1]["data"] == "2026-09-04"


def test_markdown_builders_include_expected_sections(tmp_path: Path) -> None:
	entry_path = _write_diary(tmp_path, "2026-09-03")
	repo = FileSystemEntryRepository(tmp_path)
	entry = repo.load_entry(entry_path)
	adapter = FakeLLMAdapter()
	analysis = run_analysis(entry, adapter)

	analysis_md = build_analysis_markdown(entry, analysis)
	report_md = build_report_markdown(
		date(2026, 9, 1),
		date(2026, 9, 30),
		adapter.consolidate([analysis], [build_entry_payload(entry)]),
		[entry],
	)

	assert "entrada_origem:" in analysis_md
	assert "[[2026-09-03]]" in analysis_md
	assert "### Distorções recorrentes" in report_md
	assert "### Entradas cobertas" in report_md
