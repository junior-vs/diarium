from __future__ import annotations

import re
from datetime import date
from pathlib import Path

from ..domain.models import AnalysisResult

SOURCE_BLOCK_START = "<!-- diarium:analysis:start -->"
SOURCE_BLOCK_END = "<!-- diarium:analysis:end -->"

_SECTION_PATTERN = re.compile(
	rf"{re.escape(SOURCE_BLOCK_START)}.*?{re.escape(SOURCE_BLOCK_END)}\n?",
	re.DOTALL,
)


def build_source_note_section(entry_date: date, analysis: AnalysisResult, analysis_path: Path) -> str:
	"""Gerar a seção de nota de origem para uma entrada de diário processada."""
	lines = [
		SOURCE_BLOCK_START,
		"## Análise processada",
		f"- **Data:** {entry_date.isoformat()}",
		f"- **Arquivo gerado:** [[{analysis_path.stem}]]",
		f"- **Resumo:** {analysis.resumo.strip() or 'Sem resumo gerado.'}",
		"",
		"### Distorções",
	]
	if analysis.distorcoes:
		for distortion in analysis.distorcoes:
			lines.append(f"- **{distortion.tipo}**: {distortion.trecho_citado}")
	else:
		lines.append("- Nenhuma distorção identificada.")
	lines.append(SOURCE_BLOCK_END)
	return "\n".join(lines).strip() + "\n"


def upsert_generated_section(content: str, generated_section: str) -> str:
	"""Inserir ou atualizar a seção gerada em um conteúdo existente.

	Se a seção já existir, ela será substituída. Caso contrário, a seção gerada será adicionada ao final do conteúdo.
	"""
	clean_content = content.rstrip()
	if _SECTION_PATTERN.search(clean_content):
		return _SECTION_PATTERN.sub(generated_section, clean_content)
	if clean_content:
		return f"{clean_content}\n\n{generated_section}"
	return generated_section
