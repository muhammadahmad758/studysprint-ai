"""JSON storage for StudySprint AI.

Writes are atomic: the new state is written to a temporary file in the
same folder and then renamed over the old file, so a crash mid-save
cannot leave a half-written data file behind.
"""

from __future__ import annotations

import json
import os
import tempfile

from .models import State

DEFAULT_DATA_FILE = "studysprint_data.json"


def load(path: str) -> State:
    """Load state from ``path``; return an empty state if the file is missing."""
    if not os.path.exists(path):
        return State()
    with open(path, "r", encoding="utf-8") as handle:
        return State.from_dict(json.load(handle))


def save(state: State, path: str) -> None:
    """Save state to ``path`` atomically."""
    folder = os.path.dirname(os.path.abspath(path))
    os.makedirs(folder, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=folder, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(state.to_dict(), handle, indent=2)
        os.replace(tmp_path, path)
    except BaseException:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise
