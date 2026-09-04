from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field


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
	abcde: ABCDE | None = None
	resumo: str = ""
	entrada_origem: date | None = None


class ReportResult(BaseModel):
	"""Representa o resultado consolidado de múltiplas análises de entradas do diário."""
	model_config = {"extra": "ignore"}

	distorcoes_recorrentes: list[str] = Field(default_factory=list)
	padroes_de_gatilho: list[str] = Field(default_factory=list)
	correlacoes_habito_humor: list[HabitMoodCorrelation] = Field(default_factory=list)
	evolucao: str = ""
	pontos_para_terapia: list[str] = Field(default_factory=list)
