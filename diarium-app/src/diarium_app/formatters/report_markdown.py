from __future__ import annotations

from datetime import date
from typing import Any

import frontmatter

from ..domain.entry_date import require_entry_date
from ..domain.models import EntryData, ReportResult


def build_report_markdown(
	start_date: date,
	end_date: date,
	report: ReportResult,
	entries: list[EntryData],
) -> str:
	"""Gerar uma representação em Markdown do relatório do diário."""
	metadata: dict[str, Any] = {
		"data_inicio": start_date.isoformat(),
		"data_fim": end_date.isoformat(),
		"tags": ["relatorio-tcc"],
	}
	lines = [
		"## Relatório Consolidado",
		"",
		f"**Período:** {start_date.isoformat()} a {end_date.isoformat()}",
		"",
		"### Distorções recorrentes",
	]
	lines.extend(_render_bullets(report.distorcoes_recorrentes, "Nenhuma distorção recorrente identificada."))
	lines.extend(["", "### Padrões de gatilho"])
	lines.extend(_render_bullets(report.padroes_de_gatilho, "Nenhum padrão de gatilho identificado."))
	lines.extend(["", "### Correlações hábito x humor"])
	if report.correlacoes_habito_humor:
		for correlation in report.correlacoes_habito_humor:
			lines.append(f"- **{correlation.habito}**: {correlation.relacao}")
	else:
		lines.append("- Nenhuma correlação identificada.")
	lines.extend(["", "### Evolução"])
	lines.append(report.evolucao.strip() or "Sem evolução observável.")
	lines.extend(["", "### Pontos para terapia"])
	lines.extend(_render_bullets(report.pontos_para_terapia, "Sem pontos específicos registrados."))
	lines.extend(["", "### Entradas cobertas"])
	for entry in entries:
		entry_date = require_entry_date(entry)
		lines.append(f"- [[{entry_date.isoformat()}]]")
	post = frontmatter.Post("\n".join(lines).strip() + "\n", **metadata)
	return frontmatter.dumps(post)


def _render_bullets(items: list[str], empty_message: str) -> list[str]:
	"""Renderizar uma lista de itens como marcadores em Markdown.

	Se a lista estiver vazia, retorna uma linha com a mensagem de vazio fornecida.
	"""
	if not items:
		return [f"- {empty_message}"]
	return [f"- {item}" for item in items]
