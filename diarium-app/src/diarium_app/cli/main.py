from __future__ import annotations

from datetime import date
from pathlib import Path

import typer

from ..config import Settings, build_adapter, load_settings
from ..infrastructure.filesystem_entry_repository import FileSystemEntryRepository
from ..use_cases.analyze_entry import analyze_entry as run_analyze_entry
from ..use_cases.generate_period_report import generate_period_report

app = typer.Typer(help="Diarium CLI")


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
	de: str = typer.Option(..., "--de", help="Start date"),
	ate: str = typer.Option(..., "--ate", help="End date"),
	provider: str | None = typer.Option(None, help="Override llm provider"),
	api_key: str | None = typer.Option(None, help="Override llm api key"),
	model: str | None = typer.Option(None, help="Override llm model"),
	vault_path: Path | None = typer.Option(None, help="Override vault path"),  # noqa: B008
	forcar: bool = typer.Option(False, "--forcar", help="Recompute analyses even if already persisted"),
) -> None:
	"""Generate a consolidated report for a specified period using the specified LLM provider and repository."""
	settings = _load_overrides(provider, api_key, model, vault_path)
	llm = build_adapter(settings)
	repo = FileSystemEntryRepository(settings.vault_path)
	start_date = date.fromisoformat(de)
	end_date = date.fromisoformat(ate)
	_, report_path = generate_period_report(llm, repo, start_date, end_date, force_recompute=forcar)
	typer.echo(str(report_path))


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