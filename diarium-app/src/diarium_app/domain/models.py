from __future__ import annotations

from datetime import date, time
from enum import Enum

from pydantic import BaseModel, Field

class RiskScreeningResult(str, Enum): 
	SEM_INDICIO = 'sem_indicio'
	POSSIVEL_RISCO = 'possivel_risco'

class ABCDETrigger(BaseModel):
    """Um bloco de gatilho individual, com horário (ADR-018/019)."""
    model_config = {"extra": "ignore"}
    horario: time | None = None
    a: str | None = None
    b: str | None = None
    c: str | None = None
    comportamento: str | None = None          # ADR-019
    d_perguntas: list[str] = Field(default_factory=list)  # ADR-020: sempre lista, nunca resposta resolvida
    e: str | None = None                       # ADR-020: fica em aberto por padrão

class HabitData(BaseModel):
	model_config = {"extra": "ignore"}

	mit: str | None = None
	sono: float | None = None
	estresse: int | None = None
	energia_humor: int | None = None
	hidratacao: int | None = None
	sol_manha: bool | None = None
	atividade_fisica: bool | None = None
	leitura: bool | None = None
	estudo: bool | None = None


class EntryData(BaseModel):
	"""Representa os dados de uma entrada do diário."""
	model_config = {"extra": "ignore"}

	data: date | None = None
	conteudo: str
	habit_data: HabitData = Field(default_factory=HabitData)
	caminho_origem: str


class CognitiveDistortion(BaseModel):
	"""Representa uma distorção cognitiva identificada em uma entrada do diário."""
	model_config = {"extra": "ignore"}

	tipo: str
	trecho_citado: str


class ABCDE(BaseModel):
	"""Representa a estrutura ABCDE de uma entrada do diário."""
	model_config = {"extra": "ignore"}

	a: str | None = None
	b: str | None = None
	c: str | None = None
	d: str | None = None
	e: str | None = None


class HabitMoodCorrelation(BaseModel):
	"""Representa a correlação entre um hábito e o humor em uma entrada do diário."""
	model_config = {"extra": "ignore"}

	habito: str
	relacao: str


class AnalysisResult(BaseModel):
	"""Representa o resultado da análise de uma entrada do diário."""
	model_config = {"extra": "ignore"}
	distorcoes: list[CognitiveDistortion] = Field(default_factory=list)
	gatilhos: list[ABCDETrigger] = Field(default_factory=list)   # troca de `abcde: ABCDE | None`
	resumo: str = ""
	entrada_origem: date | None = None
	risco: RiskScreeningResult = RiskScreeningResult.SEM_INDICIO  # não vem do LLM, ver use case


class ReportResult(BaseModel):
    """Representa o resultado consolidado de múltiplas análises de entradas do diário."""
    model_config = {"extra": "ignore"}
    distorcoes_recorrentes: list[str] = Field(default_factory=list)
    padroes_de_gatilho: list[str] = Field(default_factory=list)
    correlacoes_habito_humor: list[HabitMoodCorrelation] = Field(default_factory=list)
    tema_recorrente: str | None = None          # RF14 — sempre pergunta, nunca rótulo
    evolucao: str = ""
    pontos_para_terapia: list[str] = Field(default_factory=list)
    dados_insuficientes: bool = False            # RF09 — guarda determinística, não pedido ao LLM

class TrendReportResult(BaseModel):              # RF07 — SRP: não sobrecarrega ReportResult
    """Representa o resultado de tendências em múltiplas análises de entradas do diário."""
    model_config = {"extra": "ignore"}
    variacao_temas: list[str] = Field(default_factory=list)
    variacao_correlacoes: list[str] = Field(default_factory=list)
    sub_periodos_ausentes: list[str] = Field(default_factory=list)  # RF08

class AtividadeSignificativa(BaseModel):
    model_config = {"extra": "ignore"}
    descricao: str | None = None
    prazer: int | None = None   # 0-5
    dominio: int | None = None  # 0-5

class HabitData(BaseModel):
	model_config = {"extra": "ignore"}

	mit: str | None = None
	sono: float | None = None
	estresse: int | None = None
	energia_humor: int | None = None
	hidratacao: int | None = None
	sol_manha: bool | None = None
	atividade_fisica: bool | None = None
	leitura: bool | None = None
	estudo: bool | None = None
	# em HabitData:
	atividade_significativa: AtividadeSignificativa | None = None  # RF16
	positive_data_log: str | None = None                            # RF17