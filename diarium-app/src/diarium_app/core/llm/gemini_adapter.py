from __future__ import annotations

import importlib
import json
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from ..models import AnalysisResult, ReportResult
from .base import LLMAdapter, LLMResponseValidationError
from .prompt_loader import build_analysis_prompt, build_consolidation_prompt

DEFAULT_MODEL_NAME = "gemini-1.5-flash"

StructuredModel = TypeVar("StructuredModel", AnalysisResult, ReportResult)
genai = cast(Any, importlib.import_module("google.genai"))
types = cast(Any, importlib.import_module("google.genai.types"))


def _inline_refs(schema: Any, definitions: Mapping[str, Any] | None = None) -> Any:
	if definitions is None and isinstance(schema, dict):
		definitions = schema.get("$defs", {})
	if isinstance(schema, dict):
		if "$ref" in schema and definitions is not None:
			ref_name = schema["$ref"].split("/")[-1]
			return _inline_refs(definitions[ref_name], definitions)
		return {
			key: _inline_refs(value, definitions)
			for key, value in schema.items()
			if key != "$defs"
		}
	if isinstance(schema, list):
		return [_inline_refs(item, definitions) for item in schema]
	return schema


class GeminiAdapter(LLMAdapter):
	def __init__(self, api_key: str, model_name: str = DEFAULT_MODEL_NAME) -> None:
		if not api_key:
			raise ValueError("api_key is required for GeminiAdapter")
		self._client = genai.Client(api_key=api_key)
		self._model_name = model_name

	def analyze_entry(self, text: str, habit_data: Mapping[str, Any]) -> AnalysisResult:
		prompt = build_analysis_prompt(
			front_matter_dados=json.dumps(dict(habit_data), ensure_ascii=False, default=str),
			conteudo_do_diario=text,
		)
		return self._generate_structured_response(prompt, AnalysisResult)

	def consolidate(
		self,
		analyses: list[AnalysisResult],
		habit_data: list[Mapping[str, Any]],
	) -> ReportResult:
		prompt = build_consolidation_prompt(
			data_inicio=self._extract_period_start(habit_data),
			data_fim=self._extract_period_end(habit_data),
			dados_estruturados_periodo=json.dumps([dict(item) for item in habit_data], ensure_ascii=False, default=str),
			lista_de_analises=json.dumps([analysis.model_dump(mode="json") for analysis in analyses], ensure_ascii=False, default=str),
		)
		return self._generate_structured_response(prompt, ReportResult)

	def _generate_structured_response(self, prompt: str, model: type[StructuredModel]) -> StructuredModel:
		config = types.GenerateContentConfig(
			response_mime_type="application/json",
			response_schema=model,
		)
		response = self._client.models.generate_content(
			model=self._model_name,
			contents=prompt,
			config=config,
		)
		parsed = getattr(response, "parsed", None)
		if parsed is None:
			response_text = getattr(response, "text", None)
			if not response_text:
				raise LLMResponseValidationError("Gemini returned an empty response")
			try:
				return model.model_validate_json(response_text)
			except Exception as exc:  # pragma: no cover - defensive provider boundary
				raise LLMResponseValidationError(str(exc)) from exc
		try:
			if isinstance(parsed, model):
				return parsed
			return model.model_validate(parsed)
		except Exception as exc:  # pragma: no cover - defensive provider boundary
			raise LLMResponseValidationError(str(exc)) from exc

	@staticmethod
	def _extract_period_start(habit_data: list[Mapping[str, Any]]) -> str:
		if not habit_data:
			return ""
		first = habit_data[0].get("data")
		return str(first) if first is not None else ""

	@staticmethod
	def _extract_period_end(habit_data: list[Mapping[str, Any]]) -> str:
		if not habit_data:
			return ""
		last = habit_data[-1].get("data")
		return str(last) if last is not None else ""
