"""Safe lookup of a generated control explanation."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

STANDARD_ID = re.compile(r"^GRIM-STD-[0-9]{4}$")


class ExplainError(ValueError):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


def explain_control(directory: Path, standard_id: str) -> dict[str, Any]:
    """Return one stored trace without including raw manifest values."""

    if not STANDARD_ID.fullmatch(standard_id):
        raise ExplainError("GRIM_CONTROL_NOT_FOUND")
    try:
        value = json.loads((directory / "CONTROL_TRACE.json").read_text("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        raise ExplainError("GRIM_CONTROL_TRACE_INVALID") from None
    controls = value.get("controls") if isinstance(value, dict) else None
    if not isinstance(controls, list):
        raise ExplainError("GRIM_CONTROL_TRACE_INVALID")
    for control in controls:
        if isinstance(control, dict) and control.get("standard_id") == standard_id:
            return control
    raise ExplainError("GRIM_CONTROL_NOT_FOUND")
