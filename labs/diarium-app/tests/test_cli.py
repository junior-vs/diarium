from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from diarium_app.cli.main import app

runner = CliRunner()


def _write_diary(tmp_path: Path) -> Path:
	month_dir = tmp_path / "diary" / "2026" / "09"
	month_dir.mkdir(parents=True, exist_ok=True)
	path = month_dir / "2026-09-03.md"
	path.write_text(
		"""---
data: 2026-09-03
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
---

# Diário
Hoje foi puxado, mas consegui terminar algumas coisas.
""",
		encoding="utf-8",
	)
	return path


def test_cli_analisar_and_relatorio(tmp_path: Path) -> None:
	entry_path = _write_diary(tmp_path)
	analysis_result = runner.invoke(
		app,
		[
			"analisar",
			str(entry_path),
			"--provider",
			"fake",
			"--vault-path",
			str(tmp_path),
		],
	)
	assert analysis_result.exit_code == 0, analysis_result.stdout
	assert (tmp_path / "analyses" / "2026" / "09" / "2026-09-03-analise.md").exists()

	report_result = runner.invoke(
		app,
		[
			"relatorio",
			"--de",
			"2026-09-01",
			"--ate",
			"2026-09-30",
			"--provider",
			"fake",
			"--vault-path",
			str(tmp_path),
		],
	)
	assert report_result.exit_code == 0, report_result.stdout
	assert (tmp_path / "analyses" / "2026" / "09" / "2026-09-relatorio.md").exists()


def test_cli_relatorio_presets(tmp_path: Path) -> None:
	_write_diary(tmp_path)

	# Preset mensal
	result_mensal = runner.invoke(
		app,
		[
			"relatorio",
			"--preset",
			"mensal",
			"--referencia",
			"2026-09-15",
			"--provider",
			"fake",
			"--vault-path",
			str(tmp_path),
		],
	)
	assert result_mensal.exit_code == 0, result_mensal.stdout
	assert (tmp_path / "analyses" / "2026" / "09" / "2026-09-relatorio.md").exists()

	# Preset trimestral (intervalo > 45 dias, gera relatório de tendência)
	result_trimestral = runner.invoke(
		app,
		[
			"relatorio",
			"--preset",
			"trimestral",
			"--referencia",
			"2026-09-15",
			"--provider",
			"fake",
			"--vault-path",
			str(tmp_path),
		],
	)
	assert result_trimestral.exit_code == 0, result_trimestral.stdout
	assert (tmp_path / "analyses" / "2026" / "2026-07-01_2026-09-30-tendencia.md").exists()


def test_cli_command_tendencia(tmp_path: Path) -> None:
	result = runner.invoke(
		app,
		[
			"tendencia",
			"--preset",
			"semestral",
			"--referencia",
			"2026-09-15",
			"--vault-path",
			str(tmp_path),
		],
	)
	assert result.exit_code == 0, result.stdout
	assert (tmp_path / "analyses" / "2026" / "2026-07-01_2026-12-31-tendencia.md").exists()


def test_cli_relatorio_missing_params_fails() -> None:
	result = runner.invoke(app, ["relatorio"])
	assert result.exit_code != 0
	assert "Especifique --de e --ate" in result.output