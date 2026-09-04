from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Mapping

from ..models import AnalysisResult, ReportResult


class LLMResponseValidationError(ValueError):
	"""Raised when the provider returns a payload that does not match the schema."""


class LLMAdapter(ABC):
	@abstractmethod
	def analyze_entry(self, text: str, habit_data: Mapping[str, Any]) -> AnalysisResult:
		"""Analyze a single diary entry and return a structured result."""

	@abstractmethod
	def consolidate(
		self,
		analyses: list[AnalysisResult],
		habit_data: list[Mapping[str, Any]],
	) -> ReportResult:
		"""Consolidate multiple analyses into a report result."""
