from __future__ import annotations

import calendar
from datetime import date, timedelta
from enum import Enum


class ReportMode(str, Enum):
	PERIODO = "periodo"
	TENDENCIA = "tendencia"


def classify_period(start: date, end: date, *, trend_threshold_days: int = 45) -> ReportMode:
	"""Decide período vs. tendência (RF06/RF07). Pura, sem I/O — fácil de testar exaustivamente."""
	return ReportMode.TENDENCIA if (end - start).days > trend_threshold_days else ReportMode.PERIODO


def resolve_preset_dates(preset: str, ref_date: date) -> tuple[date, date]:
	"""Calcular o intervalo de datas (início, fim) para um preset de conveniência (RF06, RF07)."""
	normalized = preset.strip().lower()
	if normalized == "diario":
		return ref_date, ref_date
	if normalized == "semanal":
		start = ref_date - timedelta(days=ref_date.weekday())
		end = start + timedelta(days=6)
		return start, end
	if normalized == "mensal":
		_, last_day = calendar.monthrange(ref_date.year, ref_date.month)
		return date(ref_date.year, ref_date.month, 1), date(ref_date.year, ref_date.month, last_day)
	if normalized == "trimestral":
		quarter = (ref_date.month - 1) // 3
		start_month = quarter * 3 + 1
		end_month = start_month + 2
		_, last_day = calendar.monthrange(ref_date.year, end_month)
		return date(ref_date.year, start_month, 1), date(ref_date.year, end_month, last_day)
	if normalized == "semestral":
		start_month = 1 if ref_date.month <= 6 else 7
		end_month = 6 if ref_date.month <= 6 else 12
		_, last_day = calendar.monthrange(ref_date.year, end_month)
		return date(ref_date.year, start_month, 1), date(ref_date.year, end_month, last_day)
	if normalized == "anual":
		return date(ref_date.year, 1, 1), date(ref_date.year, 12, 31)
	raise ValueError(
		f"Preset desconhecido: '{preset}'. Escolha entre: diario, semanal, mensal, trimestral, semestral, anual."
	)