"""Render project-supplied values as inert context data."""

from __future__ import annotations

import json
import unicodedata
from typing import Any

MAX_INERT_TEXT = 20_000


class ContextRenderError(ValueError):
    """Controlled context-rendering failure."""

    def __init__(self, code: str, message: str):
        self.code = code
        super().__init__(message)


def _has_control_character(value: str) -> bool:
    return any(
        character not in {"\n", "\r"}
        and unicodedata.category(character) in {"Cc", "Cf"}
        for character in value
    )


def render_inert_text(value: str) -> str:
    """Return Markdown-indented inert text after enforcing render limits."""

    if len(value) > MAX_INERT_TEXT:
        raise ContextRenderError("text_too_long", "context text exceeds render limit")
    if _has_control_character(value):
        raise ContextRenderError(
            "control_character",
            "context text contains unsupported control characters",
        )
    lines = value.splitlines() or [""]
    return "\n".join(f"    {line}" for line in lines)


def render_inert_json(value: Any) -> str:
    """Render JSON as inert Markdown data without interpreting its contents."""

    text = json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False)
    return render_inert_text(text)
