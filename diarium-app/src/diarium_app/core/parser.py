from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import cast

import frontmatter

from .models import EntryData, HabitData


def parse_entry(path: str | Path) -> EntryData:
	post = frontmatter.load(str(path))
	metadata = post.metadata
	habit_data = HabitData(
		mit=cast(str | None, metadata.get("mit")),
		sono=cast(float | None, metadata.get("sono")),
		estresse=cast(int | None, metadata.get("estresse")),
		energia_humor=cast(int | None, metadata.get("energia_humor")),
		hidratacao=cast(int | None, metadata.get("hidratacao")),
		sol_manha=cast(bool | None, metadata.get("sol_manha")),
		atividade_fisica=cast(bool | None, metadata.get("atividade_fisica")),
		leitura=cast(bool | None, metadata.get("leitura")),
		estudo=cast(bool | None, metadata.get("estudo")),
	)
	return EntryData(
		data=cast(date | None, metadata.get("data")),
		conteudo=post.content.strip(),
		habit_data=habit_data,
		caminho_origem=str(path),
	)
