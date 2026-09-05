from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from pathlib import Path

from ..domain.models import AnalysisResult, EntryData, ReportResult


class EntryRepository(ABC):
	@abstractmethod
	def load_entry(self, path: str | Path) -> EntryData:
		"""Carregar e analisar uma única entrada do diário a partir do armazenamento."""

	@abstractmethod
	def list_entries_in_range(self, start: date, end: date) -> list[EntryData]:
		"""Retornar todas as entradas do diário cuja data esteja dentro de [start, end]."""

	@abstractmethod
	def find_existing_analysis(self, entry: EntryData) -> AnalysisResult | None:
		"""Retornar uma análise já persistida para a entrada, se existir."""

	@abstractmethod
	def save_analysis(self, entry: EntryData, analysis: AnalysisResult) -> Path:
		"""Persistir a análise de uma única entrada e retornar seu caminho."""

	@abstractmethod
	def save_report(
		self,
		start: date,
		end: date,
		report: ReportResult,
		entries: list[EntryData],
	) -> Path:
		"""Persistir um relatório consolidado e retornar seu caminho."""

	@abstractmethod
	def mark_source_processed(self, entry: EntryData, analysis: AnalysisResult, analysis_path: Path) -> None:
		"""Atualizar a nota do diário de origem para refletir que ela foi analisada."""