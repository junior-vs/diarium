from __future__ import annotations

from datetime import date
from typing import Any

import frontmatter

from ..domain.models import TrendReportResult


def build_trend_markdown(
	start_date: date,
	end_date: date,
	trend: TrendReportResult,
	footer: str | None = None,
) -> str:
	"""Gerar uma representação em Markdown do relatório de tendência."""
	metadata: dict[str, Any] = {
		"data_inicio": start_date.isoformat(),
		"data_fim": end_date.isoformat(),
		"tags": ["relatorio-tendencia"],
		"trend_json": trend.model_dump(mode="json"),
	}
	lines = [
		"## Relatório de Tendência",
		"",
		f"**Período:** {start_date.isoformat()} a {end_date.isoformat()}",
		"",
		"### Variação de temas",
	]
	if trend.variacao_temas:
		lines.extend(f"- {item}" for item in trend.variacao_temas)
	else:
		lines.append("- Nenhuma variação de temas identificada.")

	lines.extend(["", "### Variação de correlações"])
	if trend.variacao_correlacoes:
		lines.extend(f"- {item}" for item in trend.variacao_correlacoes)
	else:
		lines.append("- Nenhuma variação de correlações identificada.")

	# RF08: Sub-períodos ausentes
	if trend.sub_periodos_ausentes:
		lines.extend(["", "### Sub-períodos ausentes"])
		lines.extend(f"- {sub}" for sub in trend.sub_periodos_ausentes)

	# RF18: Rodapé incondicional de limite de papel
	if footer:
		lines.extend(["", footer.strip()])

	post = frontmatter.Post("\n".join(lines).strip() + "\n", **metadata)
	return frontmatter.dumps(post)
