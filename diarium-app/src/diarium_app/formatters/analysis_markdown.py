from __future__ import annotations

from typing import Any

import frontmatter

from ..domain.entry_date import require_entry_date
from ..domain.models import AnalysisResult, EntryData


def build_analysis_markdown(entry: EntryData, analysis: AnalysisResult) -> str:
	"""Gerar uma representação em Markdown da análise de uma entrada do diário."""

	# Extrair a data da entrada e preparar os metadados do frontmatter.
	entry_date = require_entry_date(entry)
	metadata: dict[str, Any] = {
		"data": entry_date.isoformat(),
		"tags": ["analise-tcc"],
		"entrada_origem": f"[[{entry_date.isoformat()}]]",
	}
	sections = [
		"## Análise",
		"",
		"### Resumo",
		analysis.resumo.strip() or "Sem resumo gerado.",
		"",
		"### Distorções cognitivas",
	]
	if analysis.distorcoes:
		for distortion in analysis.distorcoes:
			sections.append(f"- **{distortion.tipo}**: {distortion.trecho_citado}")
	else:
		sections.append("- Nenhuma distorção identificada.")
	sections.extend(["", "### ABCDE"])
	if analysis.abcde is None or not any(
		[analysis.abcde.a, analysis.abcde.b, analysis.abcde.c, analysis.abcde.d, analysis.abcde.e]
	):
		sections.append("- Não estruturado para esta entrada.")
	else:
		sections.extend([
			f"- **A**: {analysis.abcde.a or ''}",
			f"- **B**: {analysis.abcde.b or ''}",
			f"- **C**: {analysis.abcde.c or ''}",
			f"- **D**: {analysis.abcde.d or ''}",
			f"- **E**: {analysis.abcde.e or ''}",
		])
	post = frontmatter.Post("\n".join(sections).strip() + "\n", **metadata)
	return frontmatter.dumps(post)
