from __future__ import annotations

from collections.abc import Callable
from datetime import date
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .infrastructure.llm.fake_adapter import FakeLLMAdapter
from .infrastructure.llm.gemini_adapter import GeminiAdapter
from .ports.llm_adapter import LLMAdapter


def _default_vault_path() -> Path:
	return Path(__file__).resolve().parents[3] / "diarium-vault"


class Settings(BaseSettings):
	"""Application settings for the Diarium app."""
	model_config = SettingsConfigDict(env_prefix="DIARIUM_", env_file=".env", extra="ignore")

	llm_provider: str = "fake"
	llm_api_key: str | None = None
	# Se None, o modelo default do provider ativo é usado (ver _PROVIDER_DEFAULT_MODELS).
	# Definir DIARIUM_LLM_MODEL no .env sobrepõe o default para qualquer provider.
	llm_model: str | None = None
	vault_path: Path = Field(default_factory=_default_vault_path)
	default_report_start: date | None = None
	default_report_end: date | None = None


ProviderFactory = Callable[[Settings], LLMAdapter]

_PROVIDERS: dict[str, ProviderFactory] = {}


# Modelo default por provider, usado apenas quando DIARIUM_LLM_MODEL não é definido.
# Ao adicionar um novo provider (ex.: OpenAI), registrar o default aqui também.
_PROVIDER_DEFAULT_MODELS: dict[str, str] = {
	"""Modelo predefinido para o fornecedor Gemini."""
	"gemini": "gemini-2.5-flash",
}


def register_provider(name: str, factory: ProviderFactory) -> None:
	"""Register a new LLM provider with the given factory."""
	_PROVIDERS[name.lower()] = factory

def resolve_model_name(settings: Settings) -> str:
	"""Resolve o modelo efetivo para o provider ativo.

	``DIARIUM_LLM_MODEL`` no .env tem prioridade; na ausência, usa o default
	registrado para ``llm_provider`` em ``_PROVIDER_DEFAULT_MODELS``.
	"""
	if settings.llm_model:
		return settings.llm_model
	default_model = _PROVIDER_DEFAULT_MODELS.get(settings.llm_provider.lower())
	if default_model is None:
		raise ValueError(
			f"No default model registered for provider '{settings.llm_provider}'; "
			"set DIARIUM_LLM_MODEL explicitly in the environment."
		)
	return default_model

def build_adapter(settings: Settings) -> LLMAdapter:
	"""Build an LLM adapter based on the current settings."""
	factory = _PROVIDERS.get(settings.llm_provider.lower())
	if factory is None:
		raise ValueError(f"Unsupported llm_provider: {settings.llm_provider}")
	return factory(settings)


def _build_gemini_adapter(settings: Settings) -> LLMAdapter:
	"""Build a Gemini LLM adapter using the provided settings."""
	if not settings.llm_api_key:
		raise ValueError("DIARIUM_LLM_API_KEY is required when llm_provider=gemini")
	return GeminiAdapter(api_key=settings.llm_api_key, model_name=resolve_model_name(settings))


register_provider("fake", lambda settings: FakeLLMAdapter())
register_provider("gemini", _build_gemini_adapter)

# Para adicionar o provider OpenAI no futuro:
#   1. Criar infrastructure/llm/openai_adapter.py com uma classe OpenAIAdapter(LLMAdapter).
#   2. Adicionar "openai": "<modelo-default>" em _PROVIDER_DEFAULT_MODELS.
#   3. register_provider("openai", _build_openai_adapter) com uma factory análoga
#      a _build_gemini_adapter (lendo settings.llm_api_key / settings.llm_model).
#   Nenhuma outra função deste módulo precisa mudar (Open/Closed).


def load_settings() -> Settings:
	return Settings()