from __future__ import annotations

from importlib.resources import files

ASSETS_PACKAGE = "diarium_app.infrastructure.assets"


def load_safety_block() -> str:
	"""Carregar o texto estático do bloco de segurança (RF15)."""
	return (files(ASSETS_PACKAGE) / "bloco_seguranca.md").read_text(encoding="utf-8")


def load_footer() -> str:
	"""Carregar o texto estático do rodapé de limite de papel (RF18)."""
	return (files(ASSETS_PACKAGE) / "rodape.md").read_text(encoding="utf-8")
