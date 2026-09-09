from __future__ import annotations

import re
from pathlib import Path

from diarium_app.infrastructure.llm.prompt_loader import (
	build_analysis_prompt,
	build_consolidation_prompt,
	build_risk_screening_prompt,
	load_prompt,
)


def _find_docs_prompts_file() -> Path:
	# Procura docs/prompts.md a partir da raiz do repositório
	current = Path(__file__).resolve().parent
	for ancestor in [current, *current.parents]:
		candidate = ancestor / "docs" / "prompts.md"
		if candidate.exists():
			return candidate
		candidate_vault = ancestor.parent / "docs" / "prompts.md"
		if candidate_vault.exists():
			return candidate_vault
	raise FileNotFoundError("Não foi possível localizar docs/prompts.md")


def test_prompts_sync_with_docs_prompts_md() -> None:
	"""Garante que os arquivos .txt em runtime são idênticos aos blocos em docs/prompts.md (T7.4)."""
	prompts_md_path = _find_docs_prompts_file()
	content = prompts_md_path.read_text(encoding="utf-8")

	# Extrair blocos cercados por ```
	code_blocks = re.findall(r"```\n(.*?)\n```", content, re.DOTALL)
	assert len(code_blocks) >= 3, f"Esperados pelo menos 3 blocos de prompt em docs/prompts.md, encontrados {len(code_blocks)}"

	risk_screening_doc = code_blocks[0].replace("\r\n", "\n").strip()
	analysis_doc = code_blocks[1].replace("\r\n", "\n").strip()
	consolidation_doc = code_blocks[2].replace("\r\n", "\n").strip()

	risk_screening_txt = load_prompt("risk_screening.txt").replace("\r\n", "\n").strip()
	analysis_txt = load_prompt("analysis.txt").replace("\r\n", "\n").strip()
	consolidation_txt = load_prompt("consolidation.txt").replace("\r\n", "\n").strip()

	assert risk_screening_txt == risk_screening_doc, "risk_screening.txt divergiu de docs/prompts.md §2"
	assert analysis_txt == analysis_doc, "analysis.txt divergiu de docs/prompts.md §3"
	assert consolidation_txt == consolidation_doc, "consolidation.txt divergiu de docs/prompts.md §4"


def test_build_risk_screening_prompt() -> None:
	prompt = build_risk_screening_prompt("Hoje pensei coisas sombrias.")
	assert "Hoje pensei coisas sombrias." in prompt
	assert "Você está fazendo uma triagem de segurança" in prompt
