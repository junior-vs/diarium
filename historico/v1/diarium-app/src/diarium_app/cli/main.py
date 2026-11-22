from __future__ import annotations

from datetime import date
from pathlib import Path

import typer

from ..config import Settings, build_adapter, load_settings
from ..domain.report_period import ReportMode, classify_period, resolve_preset_dates
from ..infrastructure.filesystem_entry_repository import FileSystemEntryRepository
from ..use_cases.analyze_entry import analyze_entry as run_analyze_entry
from ..use_cases.generate_period_report import generate_period_report
from ..use_cases.generate_trend_report import generate_trend_report

app = typer.Typer(help="Diarium CLI — Diário TCC Assistido por LLM")


@app.command()
def analisar(
	arquivo: Path,
	provider: str | None = typer.Option(None, help="Override llm provider"),
	api_key: str | None = typer.Option(None, help="Override llm api key"),
	model: str | None = typer.Option(None, help="Override llm model"),
	vault_path: Path | None = typer.Option(None, help="Override vault path"),  # noqa: B008
) -> None:
	"""Analyze a single diary entry using the specified LLM provider and repository."""
	settings = _load_overrides(provider, api_key, model, vault_path)
	llm = build_adapter(settings)
	repo = FileSystemEntryRepository(settings.vault_path)
	_, _, analysis_path = run_analyze_entry(arquivo, llm, repo)
	typer.echo(str(analysis_path))


@app.command()
def relatorio(
	de: str | None = typer.Option(None, "--de", help="Start date (YYYY-MM-DD)"),
	ate: str | None = typer.Option(None, "--ate", help="End date (YYYY-MM-DD)"),
	preset: str | None = typer.Option(
		None,
		"--preset",
		help="Convenience preset: diario, semanal, mensal, trimestral, semestral, anual",
	),
	referencia: str | None = typer.Option(
		None,
		"--referencia",
		help="Reference date for preset calculation (YYYY-MM-DD, defaults to today)",
	),
	provider: str | None = typer.Option(None, help="Override llm provider"),
	api_key: str | None = typer.Option(None, help="Override llm api key"),
	model: str | None = typer.Option(None, help="Override llm model"),
	vault_path: Path | None = typer.Option(None, help="Override vault path"),  # noqa: B008
	forcar: bool = typer.Option(False, "--forcar", help="Recompute analyses even if already persisted"),
	tendencia: bool = typer.Option(False, "--tendencia", help="Force trend report aggregation over sub-periods"),
) -> None:
	"""Generate a period or trend report according to the dates or preset specified."""
	settings = _load_overrides(provider, api_key, model, vault_path)
	repo = FileSystemEntryRepository(settings.vault_path)
	start_date, end_date = _resolve_dates(de, ate, preset, referencia)

	mode = ReportMode.TENDENCIA if tendencia else classify_period(start_date, end_date)
	if mode == ReportMode.TENDENCIA:
		_, report_path = generate_trend_report(repo, start_date, end_date)
	else:
		llm = build_adapter(settings)
		_, report_path = generate_period_report(llm, repo, start_date, end_date, force_recompute=forcar)

	typer.echo(str(report_path))


@app.command("tendencia")
def relatorio_tendencia(
	de: str | None = typer.Option(None, "--de", help="Start date (YYYY-MM-DD)"),
	ate: str | None = typer.Option(None, "--ate", help="End date (YYYY-MM-DD)"),
	preset: str | None = typer.Option(
		None,
		"--preset",
		help="Convenience preset: trimestral, semestral, anual",
	),
	referencia: str | None = typer.Option(
		None,
		"--referencia",
		help="Reference date for preset calculation (YYYY-MM-DD, defaults to today)",
	),
	vault_path: Path | None = typer.Option(None, help="Override vault path"),  # noqa: B008
) -> None:
	"""Generate a trend report explicitly aggregating over processed sub-periods (RF07)."""
	settings = _load_overrides(None, None, None, vault_path)
	repo = FileSystemEntryRepository(settings.vault_path)
	start_date, end_date = _resolve_dates(de, ate, preset, referencia)
	_, trend_path = generate_trend_report(repo, start_date, end_date)
	typer.echo(str(trend_path))


def _resolve_dates(
	de: str | None,
	ate: str | None,
	preset: str | None,
	referencia: str | None,
) -> tuple[date, date]:
	"""Resolver o intervalo de datas a partir de datas explícitas ou preset."""
	if preset:
		ref_date = date.fromisoformat(referencia) if referencia else date.today()
		return resolve_preset_dates(preset, ref_date)
	if de and ate:
		return date.fromisoformat(de), date.fromisoformat(ate)
	raise typer.BadParameter(
		"Especifique --de e --ate (YYYY-MM-DD) ou escolha um --preset (diario, semanal, mensal, trimestral, semestral, anual)."
	)


def _load_overrides(
	provider: str | None,
	api_key: str | None,
	model: str | None,
	vault_path: Path | None,
) -> Settings:
	"""Load the application settings and apply any overrides provided via the CLI."""
	settings = load_settings()
	updates: dict[str, object] = {}
	if provider is not None:
		updates["llm_provider"] = provider
	if api_key is not None:
		updates["llm_api_key"] = api_key
	if model is not None:
		updates["llm_model"] = model
	if vault_path is not None:
		updates["vault_path"] = vault_path
	if updates:
		settings = settings.model_copy(update=updates)
	return settings


def main() -> None:
	app()