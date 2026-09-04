from __future__ import annotations

from datetime import date
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .core.llm import FakeLLMAdapter, GeminiAdapter, LLMAdapter


def _default_vault_path() -> Path:
	return Path(__file__).resolve().parents[3] / "diarium-vault"


class Settings(BaseSettings):
	model_config = SettingsConfigDict(env_prefix="DIARIUM_", env_file=".env", extra="ignore")

	llm_provider: str = "fake"
	llm_api_key: str | None = None
	llm_model: str = "gemini-2.5-flash"
	vault_path: Path = Field(default_factory=_default_vault_path)
	default_report_start: date | None = None
	default_report_end: date | None = None


def build_adapter(settings: Settings) -> LLMAdapter:
	provider = settings.llm_provider.lower()
	if provider == "fake":
		return FakeLLMAdapter()
	if provider == "gemini":
		if not settings.llm_api_key:
			raise ValueError("DIARIUM_LLM_API_KEY is required when llm_provider=gemini")
		return GeminiAdapter(api_key=settings.llm_api_key, model_name=settings.llm_model)
	raise ValueError(f"Unsupported llm_provider: {settings.llm_provider}")


def load_settings() -> Settings:
	return Settings()
