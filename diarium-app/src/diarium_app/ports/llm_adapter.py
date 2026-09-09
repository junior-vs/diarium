from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any

from ..domain.models import AnalysisResult, ReportResult, RiskScreeningResult


class LLMResponseValidationError(ValueError):
	"""Disparado quando o provedor retorna um payload que não corresponde ao esquema."""


class LLMAdapter(ABC):
    @abstractmethod
    def screen_risk(self, text: str) -> RiskScreeningResult:
        """Triagem determinística de risco, independente de analyze_entry (ADR-022)."""

    @abstractmethod
    def analyze_entry(self, text: str, habit_data: Mapping[str, Any]) -> AnalysisResult: ...

    @abstractmethod
    def consolidate(self, analyses: list[AnalysisResult], habit_data: list[Mapping[str, Any]]) -> ReportResult: ...