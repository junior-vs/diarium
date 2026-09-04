from __future__ import annotations

import re
from datetime import date, datetime
from pathlib import Path

from .models import EntryData


def resolve_entry_date(entry: EntryData) -> date | None:
	"""Resolver a data de uma entrada do diário, retornando None se não puder ser determinada."""
	if entry.data is not None:
		return entry.data
	return _infer_date_from_path(entry.caminho_origem)

def require_entry_date(entry: EntryData) -> date:
	"""Obter a data de uma entrada do diário, lançando um erro se não puder ser determinada."""
	entry_date = resolve_entry_date(entry)
	if entry_date is None:
		raise ValueError(f"Não foi possível determinar a data da entrada do diário para {entry.caminho_origem}")
	return entry_date

def _infer_date_from_path(path_value: str) -> date | None:
	"""Inferir a data de uma entrada do diário a partir de seu caminho, retornando None se não puder ser determinada."""
	stem = Path(path_value).stem
	match = re.search(r"\d{4}-\d{2}-\d{2}", stem)
	if not match:
		return None
	try:
		return datetime.strptime(match.group(0), "%Y-%m-%d").date()
	except ValueError:
		return None
