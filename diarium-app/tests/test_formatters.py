from __future__ import annotations

from datetime import date, time
from pathlib import Path

from diarium_app.domain.models import (
	ABCDETrigger,
	AnalysisResult,
	CognitiveDistortion,
	EntryData,
	HabitMoodCorrelation,
	ReportResult,
	RiskScreeningResult,
	TrendReportResult,
)
from diarium_app.formatters.analysis_markdown import build_analysis_markdown
from diarium_app.formatters.report_markdown import build_report_markdown
from diarium_app.formatters.trend_markdown import build_trend_markdown
from diarium_app.infrastructure.asset_loader import load_footer, load_safety_block


def _sample_entry() -> EntryData:
	return EntryData(
		data=date(2026, 9, 3),
		conteudo="Hoje tive uma reunião difícil e fiquei com medo.",
		caminho_origem="diary/2026/09/2026-09-03.md",
	)


def test_analysis_markdown_renders_gatilhos_with_socratic_d_and_comportamento() -> None:
	entry = _sample_entry()
	analysis = AnalysisResult(
		distorcoes=[CognitiveDistortion(tipo="catastrofização", trecho_citado="vai dar errado")],
		gatilhos=[
			ABCDETrigger(
				horario=time(14, 30),
				a="Reunião de alinhamento com a diretoria.",
				b="Eles vão perceber que não sei o que estou fazendo.",
				c="Ansiedade e aperto no peito.",
				comportamento="Fiquei em silêncio e evitei fazer perguntas.",
				d_perguntas=[
					"Qual é a evidência real de que você não sabe o que está fazendo?",
					"O que ficar em silêncio protege você de descobrir?",
				],
				e=None,
			)
		],
		resumo="Sessão marcada por ansiedade de desempenho.",
		risco=RiskScreeningResult.SEM_INDICIO,
	)

	md = build_analysis_markdown(entry, analysis, safety_block=load_safety_block(), footer=load_footer())

	assert "14:30 — Gatilho 1" in md
	assert "- **A (Evento):** Reunião de alinhamento" in md
	assert "- **Comportamento:** Fiquei em silêncio" in md
	assert "- **D (Perguntas socráticas):**" in md
	assert "Qual é a evidência real" in md
	assert "- **E (Efeito):** Em aberto" in md
	assert "Limite de Papel" in md  # RF18 footer
	assert "Um espaço para pausar" not in md  # sem risco


def test_analysis_markdown_injects_safety_block_when_possivel_risco() -> None:
	"""RF15: Quando possível risco, bloco de segurança estático fica no topo e análise normal abaixo."""
	entry = _sample_entry()
	analysis = AnalysisResult(
		distorcoes=[CognitiveDistortion(tipo="desesperança", trecho_citado="não vale a pena continuar")],
		resumo="Entrada com ideação expressa.",
		risco=RiskScreeningResult.POSSIVEL_RISCO,
	)

	md = build_analysis_markdown(entry, analysis, safety_block=load_safety_block(), footer=load_footer())

	# Bloco de segurança no topo
	assert "## Um espaço para pausar" in md
	assert "Centro de Valorização da Vida (CVV)" in md
	# Análise normal preservada abaixo
	assert "## Análise" in md
	assert "### Distorções cognitivas" in md
	# Posição relativa: bloco de segurança antes de ## Análise
	pos_seguranca = md.index("## Um espaço para pausar")
	pos_analise = md.index("## Análise")
	assert pos_seguranca < pos_analise
	# Rodapé incondicional ao final
	assert "Limite de Papel" in md


def test_report_markdown_handles_tema_recorrente_and_dados_insuficientes() -> None:
	start = date(2026, 9, 1)
	end = date(2026, 9, 30)

	# Caso 1: dados insuficientes (RF09)
	report_insuf = ReportResult(
		distorcoes_recorrentes=["catastrofização"],
		dados_insuficientes=True,
	)
	md_insuf = build_report_markdown(start, end, report_insuf, [_sample_entry()], footer=load_footer())
	assert "Dados insuficientes para identificar tema recorrente" in md_insuf
	assert "Dados insuficientes para correlacionar hábitos e humor" in md_insuf
	assert "Limite de Papel" in md_insuf

	# Caso 2: dados suficientes com tema recorrente (RF14)
	report_suf = ReportResult(
		distorcoes_recorrentes=["catastrofização"],
		correlacoes_habito_humor=[HabitMoodCorrelation(habito="sono", relacao="menos sono coincide com mais estresse")],
		tema_recorrente="Pode haver uma preocupação recorrente sobre atender expectativas de terceiros?",
		dados_insuficientes=False,
	)
	md_suf = build_report_markdown(start, end, report_suf, [_sample_entry()], footer=load_footer())
	assert "Pode haver uma preocupação recorrente sobre atender expectativas de terceiros?" in md_suf
	assert "menos sono coincide com mais estresse" in md_suf
	assert "Limite de Papel" in md_suf


def test_trend_markdown_renders_variations_and_sub_periodos_ausentes() -> None:
	start = date(2026, 1, 1)
	end = date(2026, 6, 30)
	trend = TrendReportResult(
		variacao_temas=["Tema de incapacidade apareceu com menor frequência no segundo trimestre"],
		variacao_correlacoes=["A correlação sono-estresse enfraqueceu em maio"],
		sub_periodos_ausentes=["2026-03"],
	)

	md = build_trend_markdown(start, end, trend, footer=load_footer())

	assert "## Relatório de Tendência" in md
	assert "Tema de incapacidade apareceu com menor frequência" in md
	assert "A correlação sono-estresse enfraqueceu" in md
	assert "### Sub-períodos ausentes" in md
	assert "2026-03" in md
	assert "Limite de Papel" in md
