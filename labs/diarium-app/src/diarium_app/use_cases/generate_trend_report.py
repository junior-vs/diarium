from __future__ import annotations

import calendar
from datetime import date
from pathlib import Path

from ..domain.models import ReportResult, TrendReportResult
from ..ports.entry_repository import EntryRepository


def list_monthly_subperiods(start: date, end: date) -> list[tuple[date, date]]:
	"""Dividir o intervalo cronológico em sub-períodos mensais limitados por start e end."""
	subperiods: list[tuple[date, date]] = []
	current_year = start.year
	current_month = start.month

	while (current_year, current_month) <= (end.year, end.month):
		_, last_day = calendar.monthrange(current_year, current_month)
		sub_start = max(start, date(current_year, current_month, 1))
		sub_end = min(end, date(current_year, current_month, last_day))
		subperiods.append((sub_start, sub_end))

		if current_month == 12:
			current_year += 1
			current_month = 1
		else:
			current_month += 1

	return subperiods


def compute_trend_variations(
	sub_reports: list[tuple[str, ReportResult]],
) -> tuple[list[str], list[str]]:
	"""Comparar sub-períodos e gerar variações em linguagem descritiva observada (RNF07)."""
	if not sub_reports:
		return [], []

	variacao_temas: list[str] = []
	variacao_correlacoes: list[str] = []

	# 1. Rastrear frequência de distorções e temas reflexivos por sub-período
	distortion_presence: dict[str, list[str]] = {}
	themes_by_period: list[tuple[str, str]] = []

	for label, rep in sub_reports:
		for dist in rep.distorcoes_recorrentes:
			distortion_presence.setdefault(dist, []).append(label)
		if rep.tema_recorrente:
			themes_by_period.append((label, rep.tema_recorrente))

	all_labels = [label for label, _ in sub_reports]
	for dist, labels in distortion_presence.items():
		if len(labels) == len(all_labels) and len(all_labels) > 1:
			variacao_temas.append(
				f"A distorção '{dist}' foi observada de forma consistente em todos os sub-períodos analisados ({', '.join(labels)})."
			)
		else:
			variacao_temas.append(
				f"A distorção '{dist}' apareceu com mais frequência em {', '.join(labels)}, não constando nos demais sub-períodos."
			)

	for label, theme in themes_by_period:
		variacao_temas.append(f"Em {label}, observou-se a reflexão temática: \"{theme}\"")

	# 2. Rastrear correlações observadas entre hábitos e humor
	for label, rep in sub_reports:
		if rep.dados_insuficientes:
			variacao_correlacoes.append(f"Em {label}: dados insuficientes para correlacionar hábitos e humor.")
		elif rep.correlacoes_habito_humor:
			for corr in rep.correlacoes_habito_humor:
				variacao_correlacoes.append(f"Em {label}: correlação observada entre {corr.habito} ({corr.relacao}).")
		else:
			variacao_correlacoes.append(f"Em {label}: nenhuma correlação específica entre hábitos e humor observada.")

	return variacao_temas, variacao_correlacoes


def generate_trend_report(
	repo: EntryRepository,
	start_date: date,
	end_date: date,
) -> tuple[TrendReportResult, Path]:
	"""Gerar relatório de tendência agregando sobre sub-períodos mensais já processados (RF07, RF08)."""
	subperiods = list_monthly_subperiods(start_date, end_date)
	sub_periodos_ausentes: list[str] = []
	found_reports: list[tuple[str, ReportResult]] = []

	for sub_start, sub_end in subperiods:
		period_label = f"{sub_start.year:04d}-{sub_start.month:02d}"
		report = repo.find_existing_report(sub_start, sub_end)
		if report is None:
			sub_periodos_ausentes.append(period_label)
		else:
			found_reports.append((period_label, report))

	variacao_temas, variacao_correlacoes = compute_trend_variations(found_reports)

	trend = TrendReportResult(
		variacao_temas=variacao_temas,
		variacao_correlacoes=variacao_correlacoes,
		sub_periodos_ausentes=sub_periodos_ausentes,
	)

	trend_path = repo.save_trend_report(start_date, end_date, trend)
	return trend, trend_path
