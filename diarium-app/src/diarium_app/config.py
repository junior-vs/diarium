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
	llm_model: str = "gemini-2.5-flash"
	vault_path: Path = Field(default_factory=_default_vault_path)
	default_report_start: date | None = None
	default_report_end: date | None = None


ProviderFactory = Callable[[Settings], LLMAdapter]

_PROVIDERS: dict[str, ProviderFactory] = {}


def register_provider(name: str, factory: ProviderFactory) -> None:
	"""Register a new LLM provider with the given factory."""
	_PROVIDERS[name.lower()] = factory


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
	return GeminiAdapter(api_key=settings.llm_api_key, model_name=settings.llm_model)


register_provider("fake", lambda settings: FakeLLMAdapter())
register_provider("gemini", _build_gemini_adapter)


def load_settings() -> Settings:
	return Settings()
