from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ...domain.models import (
	ABCDE,
	ABCDETrigger,
	AnalysisResult,
	CognitiveDistortion,
	HabitMoodCorrelation,
	ReportResult,
	RiskScreeningResult,
)
from ...ports.llm_adapter import LLMAdapter


class FakeLLMAdapter(LLMAdapter):

	def __init__(self, default_risk: RiskScreeningResult = RiskScreeningResult.SEM_INDICIO) -> None:
		"""Inicializar o adaptador falso do LLM."""
		self.analyze_calls: list[tuple[str, Mapping[str, Any]]] = []
		self.consolidate_calls: list[tuple[list[AnalysisResult], list[Mapping[str, Any]]]] = []
		self.screen_risk_calls: list[str] = []
		self.default_risk = default_risk

	def screen_risk(self, text: str) -> RiskScreeningResult:
		"""Executar triagem determinística de risco para o texto."""
		self.screen_risk_calls.append(text)
		return self.default_risk

	def analyze_entry(self, text: str, habit_data: Mapping[str, Any]) -> AnalysisResult:
		"""Analisar uma entrada de diário e retornar o resultado da análise."""
		self.analyze_calls.append((text, habit_data))
		return AnalysisResult(
			distorcoes=[
				CognitiveDistortion(
					tipo="catastrofização",
					trecho_citado="Vai dar tudo errado",
				),
			],
			gatilhos=[
				ABCDETrigger(
					a="Houve um gatilho difícil no dia.",
					b="Achei que tudo iria dar errado.",
					c="Fiquei ansioso.",
					comportamento="Evitei checar as mensagens de trabalho.",
					d_perguntas=[
						"Qual é a evidência real de que tudo dará errado?",
						"O que de pior poderia razoavelmente acontecer?",
					],
					e=None,
				),
			],
			abcde=ABCDE(
				a="Houve um gatilho difícil no dia.",
				b="Achei que tudo iria dar errado.",
				c="Fiquei ansioso.",
				d="Não tenho evidência suficiente para concluir isso.",
				e="Posso lidar com a situação em partes.",
			),
			resumo="Análise sintética de teste.",
		)

	def consolidate(
		self,
		analyses: list[AnalysisResult],
		habit_data: list[Mapping[str, Any]],
	) -> ReportResult:
		"""Consolidar múltiplas análises de entradas de diário e retornar o relatório resultante."""
		self.consolidate_calls.append((analyses, habit_data))
		return ReportResult(
			distorcoes_recorrentes=["catastrofização"],
			padroes_de_gatilho=["pressão no trabalho"],
			correlacoes_habito_humor=[
				HabitMoodCorrelation(
					habito="sono",
					relacao="Menos sono coincide com mais estresse relatado.",
				),
			],
			evolucao="Melhora gradual ao longo do período.",
			pontos_para_terapia=["Explorar gatilhos de cobrança excessiva."],
		)
