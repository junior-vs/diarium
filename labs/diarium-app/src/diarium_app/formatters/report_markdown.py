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
	footer: str | None = None,
) -> str:
	"""Gerar uma representação em Markdown do relatório do diário."""
	metadata: dict[str, Any] = {
		"data_inicio": start_date.isoformat(),
		"data_fim": end_date.isoformat(),
		"tags": ["relatorio-tcc"],
		"dados_insuficientes": report.dados_insuficientes,
		"report_json": report.model_dump(mode="json"),
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

	# RF14 / ADR-021: Tema recorrente
	lines.extend(["", "### Tema recorrente"])
	if report.dados_insuficientes:
		lines.append("- Dados insuficientes para identificar tema recorrente (mínimo de entradas não atingido).")
	elif report.tema_recorrente:
		lines.append(report.tema_recorrente.strip())
	else:
		lines.append("- Nenhum tema recorrente identificado.")

	# RF09 / RF13: Correlações hábito x humor
	lines.extend(["", "### Correlações hábito x humor"])
	if report.dados_insuficientes:
		lines.append("- Dados insuficientes para correlacionar hábitos e humor (mínimo de entradas não atingido).")
	elif report.correlacoes_habito_humor:
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

	# RF18: Rodapé de limite de papel
	if footer:
		lines.extend(["", footer.strip()])

	post = frontmatter.Post("\n".join(lines).strip() + "\n", **metadata)
	return frontmatter.dumps(post)


def _render_bullets(items: list[str], empty_message: str) -> list[str]:
	"""Renderizar uma lista de itens como marcadores em Markdown."""
	if not items:
		return [f"- {empty_message}"]
	return [f"- {item}" for item in items]
