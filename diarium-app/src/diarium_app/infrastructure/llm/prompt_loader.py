from __future__ import annotations

from importlib.resources import files

PROMPTS_PACKAGE = "diarium_app.infrastructure.llm.prompts"


def load_prompt(name: str) -> str:
	prompt_path = files(PROMPTS_PACKAGE) / name
	return prompt_path.read_text(encoding="utf-8")


def build_analysis_prompt(front_matter_dados: str, conteudo_do_diario: str) -> str:
	return load_prompt("analysis.txt").format(
		front_matter_dados=front_matter_dados,
		conteudo_do_diario=conteudo_do_diario,
	)


def build_consolidation_prompt(
	data_inicio: str,
	data_fim: str,
	dados_estruturados_periodo: str,
	lista_de_analises: str,
) -> str:
	return load_prompt("consolidation.txt").format(
		data_inicio=data_inicio,
		data_fim=data_fim,
		dados_estruturados_periodo=dados_estruturados_periodo,
		lista_de_analises=lista_de_analises,
	)


def build_risk_screening_prompt(conteudo: str) -> str:
	return load_prompt("risk_screening.txt").format(conteudo=conteudo)