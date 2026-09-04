from __future__ import annotations

from datetime import date
from pathlib import Path

import typer

from ..config import Settings, build_adapter, load_settings
from ..core.analysis import analyze_entry
from ..core.parser import parse_entry
from ..core.report import generate_period_report, write_analysis

app = typer.Typer(help="Diarium CLI")


@app.command()
def analisar(
	arquivo: Path,
	provider: str | None = typer.Option(None, help="Override llm provider"),
	api_key: str | None = typer.Option(None, help="Override llm api key"),
	model: str | None = typer.Option(None, help="Override llm model"),
	vault_path: Path | None = typer.Option(None, help="Override vault path"),
) -> None:
	settings = _load_overrides(provider, api_key, model, vault_path)
	adapter = build_adapter(settings)
	entry = parse_entry(arquivo)
	result = analyze_entry(entry, adapter)
	analysis_path = write_analysis(entry, result, settings.vault_path)
	typer.echo(str(analysis_path))


@app.command()
def relatorio(
	de: str = typer.Option(..., "--de", help="Start date"),
	ate: str = typer.Option(..., "--ate", help="End date"),
	provider: str | None = typer.Option(None, help="Override llm provider"),
	api_key: str | None = typer.Option(None, help="Override llm api key"),
	model: str | None = typer.Option(None, help="Override llm model"),
	vault_path: Path | None = typer.Option(None, help="Override vault path"),
) -> None:
	settings = _load_overrides(provider, api_key, model, vault_path)
	adapter = build_adapter(settings)
	start_date = date.fromisoformat(de)
	end_date = date.fromisoformat(ate)
	_, report_path = generate_period_report(settings.vault_path, adapter, start_date, end_date)
	typer.echo(str(report_path))


def _load_overrides(
	provider: str | None,
	api_key: str | None,
	model: str | None,
	vault_path: Path | None,
) -> Settings:
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
