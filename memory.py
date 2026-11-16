"""Session transcripts for many-minds — plain files, no server, no DB.

M1 only saves the chat session transcript. remember/recall land in M2.
"""
import json
from datetime import datetime
from pathlib import Path


def sessions_dir(memory_dir):
    d = Path(memory_dir) / "sessions"
    d.mkdir(parents=True, exist_ok=True)
    return d


def save_session(memory_dir, model, messages):
    """Write one transcript file (one JSON object per line); returns its path."""
    d = sessions_dir(memory_dir)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    path = d / f"session-{stamp}.jsonl"
    with open(path, "w", encoding="utf-8") as f:
        for m in messages:
            f.write(json.dumps({"model": model, **m}, ensure_ascii=False) + "\n")
    return path
