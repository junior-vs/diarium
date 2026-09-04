from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any

from ..domain.models import AnalysisResult, ReportResult


class LLMResponseValidationError(ValueError):
	"""Disparado quando o provedor retorna um payload que não corresponde ao esquema."""


class LLMAdapter(ABC):
	@abstractmethod
	def analyze_entry(self, text: str, habit_data: Mapping[str, Any]) -> AnalysisResult:
		"""Analisar uma única entrada do diário e retornar um resultado estruturado."""

	@abstractmethod
	def consolidate(
		self,
		analyses: list[AnalysisResult],
		habit_data: list[Mapping[str, Any]],
	) -> ReportResult:
		"""Consolidar múltiplas análises em um resultado de relatório."""
