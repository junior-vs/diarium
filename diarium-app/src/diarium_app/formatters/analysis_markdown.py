from __future__ import annotations

from typing import Any

import frontmatter

from ..domain.entry_date import require_entry_date
from ..domain.models import AnalysisResult, EntryData, RiskScreeningResult


def build_analysis_markdown(
	entry: EntryData,
	analysis: AnalysisResult,
	safety_block: str | None = None,
	footer: str | None = None,
) -> str:
	"""Gerar uma representação pura em Markdown da análise de uma entrada do diário."""
	entry_date = require_entry_date(entry)
	metadata: dict[str, Any] = {
		"data": entry_date.isoformat(),
		"tags": ["analise-tcc"],
		"entrada_origem": f"[[{entry_date.isoformat()}]]",
		"risco": analysis.risco.value,
		# Permite reconstruir o AnalysisResult sem chamar o LLM novamente (ver
		# FileSystemEntryRepository.find_existing_analysis).
		"analysis_json": analysis.model_dump(mode="json"),
	}

	sections: list[str] = []

	# RF15: Inserir bloco de segurança no topo se houver possível risco
	if analysis.risco == RiskScreeningResult.POSSIVEL_RISCO and safety_block:
		sections.append(safety_block.strip())
		sections.append("")

	sections.extend([
		"## Análise",
		"",
		"### Resumo",
		analysis.resumo.strip() or "Sem resumo gerado.",
		"",
		"### Distorções cognitivas",
	])

	if analysis.distorcoes:
		for distortion in analysis.distorcoes:
			sections.append(f"- **{distortion.tipo}**: {distortion.trecho_citado}")
	else:
		sections.append("- Nenhuma distorção identificada.")

	# RF04 / ADR-018, ADR-019, ADR-020: Estrutura de gatilhos
	sections.extend(["", "### Gatilhos e ABCDE"])
	if analysis.gatilhos:
		for idx, gatilho in enumerate(analysis.gatilhos, start=1):
			horario_prefix = f"{gatilho.horario.strftime('%H:%M')} — " if gatilho.horario else ""
			sections.append(f"#### {horario_prefix}Gatilho {idx}")
			sections.append(f"- **A (Evento):** {gatilho.a or 'Não informado'}")
			sections.append(f"- **B (Pensamento):** {gatilho.b or 'Não informado'}")
			sections.append(f"- **C (Emoção):** {gatilho.c or 'Não informado'}")
			sections.append(f"- **Comportamento:** {gatilho.comportamento or 'Não informado'}")
			sections.append("- **D (Perguntas socráticas):**")
			if gatilho.d_perguntas:
				for pergunta in gatilho.d_perguntas:
					sections.append(f"  - {pergunta}")
			else:
				sections.append("  - Nenhuma pergunta registrada.")
			sections.append(f"- **E (Efeito):** {gatilho.e or 'Em aberto'}")
			sections.append("")
		if sections and sections[-1] == "":
			sections.pop()
	elif analysis.abcde is not None and any(
		[analysis.abcde.a, analysis.abcde.b, analysis.abcde.c, analysis.abcde.d, analysis.abcde.e]
	):
		sections.extend([
			f"- **A**: {analysis.abcde.a or ''}",
			f"- **B**: {analysis.abcde.b or ''}",
			f"- **C**: {analysis.abcde.c or ''}",
			f"- **D**: {analysis.abcde.d or ''}",
			f"- **E**: {analysis.abcde.e or ''}",
		])
	else:
		sections.append("- Não estruturado para esta entrada.")

	# RF18: Rodapé incondicional de limite de papel
	if footer:
		sections.extend(["", footer.strip()])

	post = frontmatter.Post("\n".join(sections).strip() + "\n", **metadata)
	return frontmatter.dumps(post)